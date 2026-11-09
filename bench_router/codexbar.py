"""CodexBar 0.84 CLI contract: fresh, account-bound quota before paid decisions."""
import base64
import json
import hashlib
import os
import re
from . import usage as policy
from .usage import Availability, fresh, number
from .usage_process import run_cli
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

BIN = os.environ.get("BENCH_ROUTER_CODEXBAR", "codexbar")
PROVIDERS = policy.PROVIDERS
CALL_TIMEOUT_S = 120  # agy's native /usage report can take 90 seconds on a cold start


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
    return policy.needs_credits("claude", model, data.get("loginMethod"))


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


def credit_binding(payload, base, now):
    web = usage(payload, now)
    if not web or payload.get("source") != "web":
        return "unverified"
    identity = claude_identity()
    email = base.get("accountEmail") or identity.get("emailAddress")
    if not email or str(email).casefold() != str(web.get("accountEmail", "")).casefold():
        return "mismatch"
    base_org = base.get("accountOrganization") or identity.get("organizationName")
    web_org = web.get("accountOrganization")
    if base_org and web_org and str(base_org).casefold() != str(web_org).casefold():
        return "mismatch"
    base_id, web_id = base.get("identity"), web.get("identity")
    base_id = base_id if isinstance(base_id, dict) else {}
    web_id = web_id if isinstance(web_id, dict) else {}
    if base_id.get("accountID") and web_id.get("accountID") and base_id["accountID"] != web_id["accountID"]:
        return "mismatch"
    return "matched"


def collect(profiles, *, now, runner=None, which=shutil.which):
    """Translate CodexBar sources to observations; the common policy owns eligibility."""
    providers = sorted({PROVIDERS[p["kind"]] for p in profiles if p.get("kind") in PROVIDERS})
    identities = {provider: worker_email(provider) for provider in providers}
    def fetch(provider):
        return query(provider, "auto" if provider == "antigravity" else "oauth", runner) if which(BIN) else {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        payloads = dict(zip(providers, pool.map(fetch, providers)))
    out, web = {}, None
    def clock():
        # Fixture time is injected. Live snapshots can be newer than batch start.
        return max(now, datetime.now(timezone.utc)) if runner is None else now
    for p in profiles:
        provider, model = PROVIDERS.get(p.get("kind")), policy.model_id(p)
        payload = payloads.get(provider, {})
        data = usage(payload, clock())
        if provider == "claude" and not data and which(BIN):
            if web is None:
                web = query("claude", "web", runner)
            if usage(web, clock()) and account_binding(provider, web, web["usage"], identities.get(provider)) == "matched":
                payload, data = web, web["usage"]
        binding = account_binding(provider, payload, data, identities.get(provider)) if data else "unverified"
        selected, balances, caps = [], [], []
        email = identities.get(provider)
        account_key = hashlib.sha256((provider + ":" + email.casefold()).encode()).hexdigest() if isinstance(email, str) else None
        def add_windows(raw, raw_payload, bound):
            for w in windows(raw, provider, model, raw_payload.get("rateWindowLabels")):
                selected.append(policy.Window(w["scope"], w["usedPercent"], raw.get("updatedAt"),
                    raw_payload.get("source", "unknown"), w.get("resetsAt"), w.get("windowMinutes"), bound, account_key))
        def add_cap(raw, source, bound):
            c = raw.get("providerCost")
            if isinstance(c, dict):
                caps.append(policy.SpendCap(c.get("used"), c.get("limit"), c.get("currencyCode"),
                    c.get("updatedAt"), source, bound, account_key))
        add_windows(data, payload, binding)
        if data and needs_credits(model, data):
            if web is None and which(BIN):
                web = query("claude", "web", runner)
            wb = credit_binding(web or {}, data, clock())
            wd = usage(web or {}, clock())
            c = wd.get("providerCost") or {}
            c = c if isinstance(c, dict) else {}
            balances.append(policy.Balance(c.get("balance"), c.get("currencyCode"),
                observed_at=c.get("balanceUpdatedAt") or c.get("updatedAt"), source="web", binding=wb,
                status="measured" if number(c.get("balance")) is not None else "unknown", account_key=account_key))
            if wb == "matched":
                add_windows(wd, web, wb)
                add_cap(wd, "web", wb)
            add_cap(data, payload.get("source", "unknown"), "matched" if wb == "matched" else binding)
        pace = {}
        raw_pace = payload.get("pace")
        if isinstance(raw_pace, dict):
            for scope, raw in raw_pace.items():
                if isinstance(raw, dict):
                    pace[scope] = {"stage": raw.get("stage"), "will_last_to_reset": raw.get("willLastToReset"),
                                   "eta_seconds": raw.get("etaSeconds")}
        out[p["id"]] = policy.Observation(p["id"], provider, model, "codexbar", payload.get("source", "unknown"),
            data.get("loginMethod"), "ok" if data else "unavailable", binding,
            tuple(selected), tuple(balances), tuple(caps), pace, account_key)
    return out


def availability(profiles, runner=None, which=shutil.which, now=None):
    """Compatibility entry point; production callers use usage.probe."""
    return policy.probe(profiles, collector=lambda ps, *, now: collect(ps, now=now, runner=runner, which=which), now=now)
