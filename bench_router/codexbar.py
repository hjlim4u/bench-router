"""CodexBar 0.84 CLI contract: fresh, account-bound quota before paid decisions."""
import base64
import json
import math
import os
import re
import signal
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

BIN = os.environ.get("BENCH_ROUTER_CODEXBAR", "codexbar")
PROVIDERS = {"claude": "claude", "codex": "codex", "agy": "antigravity"}
MAX_AGE_S = 300
CALL_TIMEOUT_S = 120  # agy's native /usage report can take 90 seconds on a cold start


class Availability(dict):
    """Keep the existing reason-map contract; carry volatile observations outside decision hashes."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.details = {}


def run_cli(cmd, *, timeout=CALL_TIMEOUT_S, **kwargs):
    """Own only this probe's process group. Give CodexBar time to cancel its native children first."""
    with tempfile.TemporaryFile() as output:
        with subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.DEVNULL,
                              start_new_session=True) as proc:
            try:
                proc.wait(timeout=timeout)
            finally:
                if proc.poll() is None:
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except (ProcessLookupError, subprocess.TimeoutExpired):
                        pass
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
            output.seek(0)
            return subprocess.CompletedProcess(cmd, proc.returncode, output.read(8 * 1024 * 1024 + 1).decode("utf-8", "replace"))


def number(value):
    return value if type(value) is int or (type(value) is float and math.isfinite(value)) else None


def fresh(value, now):
    try:
        age = (now - datetime.fromisoformat(value.replace("Z", "+00:00"))).total_seconds()
        return -60 <= age <= MAX_AGE_S
    except (AttributeError, TypeError, ValueError, OverflowError):
        return False


def query(provider, source, runner=None):
    """No inference prompts or Claude/Codex PTY fallback; never log credentials or raw errors."""
    try:
        proc = (runner or run_cli)([BIN, "usage", "--provider", provider, "--source", source, "--json"],
                      capture_output=True, text=True, encoding="utf-8", errors="replace",
                      timeout=CALL_TIMEOUT_S, shell=False)
        if len(proc.stdout.encode("utf-8")) > 8 * 1024 * 1024:
            return {}
        rows = json.loads(proc.stdout)
        # A nonzero multi-provider result can retain successful rows. Select exactly one account.
        rows = [p for p in rows if isinstance(p, dict) and p.get("provider") == provider] if isinstance(rows, list) else []
        return rows[0] if len(rows) == 1 and isinstance(rows[0].get("source"), str) else {}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {}


def usage(payload, now):
    data = payload.get("usage")
    if (payload.get("error") or payload.get("diagnostic") or not isinstance(data, dict)
            or not fresh(data.get("updatedAt"), now)):
        return {}
    return data


def measured(window):
    return (isinstance(window, dict) and not window.get("isSyntheticPlaceholder")
            and number(window.get("usedPercent")) is not None and window["usedPercent"] >= 0)


def windows(data, provider, model, labels):
    """Only limits applying to this model; shared pools remain shared, never summed."""
    labels = labels if isinstance(labels, dict) else {}
    family = next((x for x in ("fable", "opus", "sonnet", "haiku") if x in model), None)
    extras = data.get("extraRateWindows")
    extras = extras if isinstance(extras, list) else []
    named = [x for x in extras if isinstance(x, dict) and isinstance(x.get("id"), str)]
    if provider == "antigravity":
        pool = "gemini" if model.startswith("gemini") else "3p" if model.startswith(("claude", "gpt")) else None
        if pool is None:
            return []
        bare_model = re.sub(r"-(low|medium|high)$", "", model)
        def applies(key):
            if key in {f"antigravity-quota-summary-{pool}-5h", f"antigravity-quota-summary-{pool}-weekly",
                       "antigravity-gemini" if pool == "gemini" else "antigravity-claude-gpt"}:
                return True
            if key in (model, bare_model):
                return True
            prefix = "antigravity-quota-summary-"
            if not key.startswith(prefix):
                return False
            bucket = key.removeprefix(prefix)
            # Summary Gemini IDs can omit the version (gemini-argon-wtu-weekly).
            alias = re.sub(r"^gemini-\d+(?:\.\d+)?-", "gemini-", bare_model)
            return bucket.startswith(bare_model + "-") or bucket.startswith(alias + "-")
        selected = [{**x["window"], "scope": x["id"]} for x in named if applies(x["id"]) and x.get("usageKnown", True) is True
                    and measured(x.get("window"))]
        if selected:
            return selected
        # Family representatives are usable only if that pool has no named observations.
        # Reset-only rows must not turn their synthetic 100% representative into exhaustion.
        if any(applies(x["id"]) for x in named):
            return []
        key = "primary" if pool == "gemini" else "secondary"
        return [{**data[key], "scope": key}] if measured(data.get(key)) else []
    selected = [{**data[k], "scope": k} for k in ("primary", "secondary") if measured(data.get(k))]
    if provider == "claude":
        label = str(labels.get("tertiary", "")).lower()
        if family and family in label and measured(data.get("tertiary")):
            selected.append({**data["tertiary"], "scope": "tertiary"})
        selected += [{**x["window"], "scope": x["id"]} for x in named if family and x["id"].startswith("claude-weekly-scoped-")
                     and family in re.findall(r"[a-z]+", x["id"] + " " + str(x.get("title", "")).lower())
                     and x.get("usageKnown", True) is True and measured(x.get("window"))]
    return selected


def needs_credits(model, data):
    # Claude Pro Fable uses prepaid Claude.ai Usage credits, separate from API Console billing.
    plan = str(data.get("loginMethod") or "").lower()
    return "fable" in model and not any(x in plan for x in ("max", "team", "enterprise"))


def claude_identity():
    """Display identity only; OAuth CLI output can omit its asynchronously fetched email."""
    if any(os.environ.get(k) for k in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")):
        return {}
    root = os.environ.get("CLAUDE_CONFIG_DIR")
    path = Path(root) / ".claude.json" if root else Path.home() / ".claude.json"
    try:
        obj = json.loads(path.read_text("utf-8"))
        account = obj.get("oauthAccount", {})
        return account if isinstance(account, dict) else {}
    except (OSError, ValueError, AttributeError):
        return {}


def worker_email(provider):
    """Read local CLI display identity only; never emit or copy credential contents."""
    if provider == "claude":
        return claude_identity().get("emailAddress")
    try:
        if provider == "antigravity":
            obj = json.loads((Path.home() / ".gemini/antigravity-cli/antigravity-oauth-token").read_text("utf-8"))
            return obj.get("id_token_email")
        if provider == "codex":
            obj = json.loads((Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json").read_text("utf-8"))
            token = obj["tokens"]["id_token"].split(".")[1]
            claims = json.loads(base64.urlsafe_b64decode(token + "=" * (-len(token) % 4)))
            return claims.get("email")
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError):
        pass
    return None


def account_binding(provider, payload, data, expected):
    actual = data.get("accountEmail")
    expected = expected if isinstance(expected, str) and expected else None
    actual = actual if isinstance(actual, str) and actual else None
    if expected and actual:
        return "matched" if str(expected).casefold() == str(actual).casefold() else "mismatch"
    # Native Auto owns matching its selected Antigravity account; a remote/browser
    # response must additionally match the CLI that bench-router will actually run.
    if actual or payload.get("account") or (provider == "antigravity" and payload.get("source") in {"web", "app", "ide", "oauth"}):
        return "unverified"
    return "ambient_cli"


def credit_reason(payload, base, now):
    web = usage(payload, now)
    if not web or payload.get("source") != "web":
        return "codexbar_credits_unverified"
    identity = claude_identity()
    email = base.get("accountEmail") or identity.get("emailAddress")
    if not email or str(email).casefold() != str(web.get("accountEmail", "")).casefold():
        return "codexbar_credit_account_mismatch"
    base_org = base.get("accountOrganization") or identity.get("organizationName")
    web_org = web.get("accountOrganization")
    if base_org and web_org and str(base_org).casefold() != str(web_org).casefold():
        return "codexbar_credit_account_mismatch"
    base_id, web_id = base.get("identity"), web.get("identity")
    base_id = base_id if isinstance(base_id, dict) else {}
    web_id = web_id if isinstance(web_id, dict) else {}
    if base_id.get("accountID") and web_id.get("accountID") and base_id["accountID"] != web_id["accountID"]:
        return "codexbar_credit_account_mismatch"
    # Preserve every known spend cap; a balance-only Web response synthesizes limit=0,
    # which must never erase the OAuth source's real spend limit.
    for data in (base, web):
        cap = data.get("providerCost")
        if isinstance(cap, dict) and fresh(cap.get("updatedAt"), now):
            used, limit = number(cap.get("used")), number(cap.get("limit"))
            if used is not None and limit is not None and limit > 0 and used >= limit:
                return "codexbar_spend_limit_exhausted"
    cost = web.get("providerCost")
    if not isinstance(cost, dict) or not fresh(cost.get("balanceUpdatedAt") or cost.get("updatedAt"), now):
        return "codexbar_credits_unverified"
    balance = number(cost.get("balance"))
    if balance is None or cost.get("currencyCode") != "USD":
        return "codexbar_credits_unverified"
    if balance <= 0:
        return "codexbar_credits_exhausted"
    used, limit = number(cost.get("used")), number(cost.get("limit"))
    if used is None or limit is None or min(used, limit) < 0:
        return "codexbar_credits_unverified"
    if limit > 0 and used >= limit:
        return "codexbar_spend_limit_exhausted"
    return None


def reserve_percent():
    from .routing import InputError
    try:
        value = float(os.environ.get("BENCH_ROUTER_MIN_REMAINING", "10"))
        if math.isfinite(value) and 0 <= value <= 100:
            return value
    except ValueError:
        pass
    raise InputError("BENCH_ROUTER_MIN_REMAINING must be a finite percentage from 0 to 100")


def describe(payload, selected, binding, reason, threshold, now):
    """Allowlisted numeric observations, no raw provider messages, emails, or reset-credit IDs."""
    data = usage(payload, now)
    rows = []
    for w in selected:
        row = {"used_percent": w["usedPercent"], "remaining_percent": max(0, 100 - w["usedPercent"])}
        scope = w.get("scope", "unknown")
        row["scope"] = scope if isinstance(scope, str) and re.fullmatch(r"[a-zA-Z0-9_.-]{1,120}", scope) else "unknown"
        for key, target in (("resetsAt", "resets_at"), ("windowMinutes", "window_minutes")):
            value = w.get(key)
            if key == "resetsAt":
                try:
                    value = datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
                except (TypeError, AttributeError, ValueError):
                    continue
            elif number(value) is None or value <= 0:
                continue
            row[target] = value
        if row not in rows:
            rows.append(row)
    remaining = min((w["remaining_percent"] for w in rows), default=None)
    source = payload.get("source")
    detail = {"provider": payload.get("provider"), "source": source if source in {
        "oauth", "web", "cli", "app", "ide", "offline"} else "unknown",
        "updated_at": data.get("updatedAt"), "checked_at": now.isoformat(), "account_binding": binding,
        "windows": rows, "remaining_percent": remaining, "reason": reason,
        "guard": {"min_remaining_percent": threshold, "decision": "unknown" if remaining is None else
                  "low" if remaining < threshold or remaining == 0 else "safe"}, "pace": {}}
    pace = payload.get("pace")
    if isinstance(pace, dict):
        for key in ("primary", "secondary", "tertiary"):
            p = pace.get(key)
            if not isinstance(p, dict) or key not in {w.get("scope") for w in selected}:
                continue
            row = {}
            if isinstance(p.get("stage"), str) and p["stage"] in {"ahead", "farAhead", "behind", "farBehind", "onTrack"}:
                row["stage"] = p["stage"]
            if type(p.get("willLastToReset")) is bool:
                row["will_last_to_reset"] = p["willLastToReset"]
            if number(p.get("etaSeconds")) is not None and p["etaSeconds"] >= 0:
                row["eta_seconds"] = p["etaSeconds"]
            if row:
                detail["pace"][key] = row
    detail["warnings"] = (["ambient_account_unverified"] if binding == "ambient_cli" else []) + (
        ["pace_runs_out_before_reset"] if any(p.get("will_last_to_reset") is False for p in detail["pace"].values()) else [])
    return detail


def availability(profiles, runner=None, which=shutil.which, now=None):
    """Unknown quota excludes a candidate before evaluation; external/offline callers bypass this."""
    clock = lambda: now or datetime.now(timezone.utc)
    threshold = reserve_percent()
    providers = sorted({PROVIDERS[p["kind"]] for p in profiles if p.get("kind") in PROVIDERS})
    identities = {provider: worker_email(provider) for provider in providers}
    def fetch(provider):
        return query(provider, "auto" if provider == "antigravity" else "oauth", runner) if which(BIN) else {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        payloads = dict(zip(providers, pool.map(fetch, providers)))
    out, web = Availability(), None
    for p in profiles:
        provider = PROVIDERS.get(p.get("kind"))
        payload = payloads.get(provider, {})
        data = usage(payload, clock())
        credit_check = "not_checked"
        if provider == "claude" and not data and which(BIN):
            if web is None:
                web = query("claude", "web", runner)
            if usage(web, clock()) and account_binding(provider, web, web["usage"], identities.get(provider)) == "matched":
                payload, data = web, web["usage"]
        args = p.get("args", [])
        model = str(p.get("model_id", "")).lower()
        for flag in ("--model", "-m"):
            if flag in args and args.index(flag) + 1 < len(args):
                model = args[args.index(flag) + 1].lower()
        selected = windows(data, provider, model, payload.get("rateWindowLabels") or {})
        reason = "codexbar_quota_unverified" if not selected else None
        binding = account_binding(provider, payload, data, identities.get(provider)) if data else "unverified"
        if not reason and binding in {"mismatch", "unverified"}:
            reason = "codexbar_account_mismatch" if binding == "mismatch" else "codexbar_account_unverified"
        if binding in {"mismatch", "unverified"}:
            selected = []  # Another account's quota must not appear as this worker's allowance.
        if not reason and any(w["usedPercent"] >= 100 for w in selected):
            reason = "codexbar_quota_exhausted"
        if not reason and provider == "claude" and needs_credits(model, data):
            if web is None:
                web = query("claude", "web", runner)
            credit_check = reason = credit_reason(web, data, clock())
            if reason != "codexbar_credit_account_mismatch" and usage(web, clock()) and web.get("source") == "web":
                selected += windows(usage(web, clock()), provider, model, web.get("rateWindowLabels") or {})
                if any(w["usedPercent"] >= 100 for w in selected):
                    reason = "codexbar_quota_exhausted"
        if not reason and any(100 - w["usedPercent"] < threshold for w in selected):
            reason = "codexbar_quota_low"
        out[p["id"]] = reason
        out.details[p["id"]] = describe(payload, selected, binding, reason, threshold, clock())
        out.details[p["id"]]["provider"] = provider
        if credit_check != "not_checked":
            cost = usage(web, clock()).get("providerCost")
            cost = cost if isinstance(cost, dict) else {}
            stamp = cost.get("balanceUpdatedAt") or cost.get("updatedAt")
            verified = credit_check not in {"codexbar_credit_account_mismatch", "codexbar_credits_unverified"} and fresh(stamp, clock())
            out.details[p["id"]]["credits"] = {"status": credit_check or "available",
                "balance": number(cost.get("balance")) if verified else None,
                "currency": "USD" if verified and cost.get("currencyCode") == "USD" else None,
                "updated_at": stamp if verified else None}
    return out
