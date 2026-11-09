"""Tool-neutral observations and execution policy. Collectors never decide eligibility."""
import math
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

PROVIDERS = {"claude": "claude", "codex": "codex", "agy": "antigravity"}
MAX_AGE_S = 300


@dataclass(frozen=True)
class Window:
    scope: str
    used_percent: float | None
    observed_at: str | None
    source: str
    resets_at: str | None = None
    minutes: float | None = None
    binding: str = "ambient_cli"
    account_key: str | None = None


@dataclass(frozen=True)
class Balance:
    amount: float | None = None
    currency: str | None = None
    kind: str = "claude_usage_credits"
    observed_at: str | None = None
    source: str = "unknown"
    binding: str = "unverified"
    status: str = "unknown"
    account_key: str | None = None


@dataclass(frozen=True)
class SpendCap:
    used: float | None
    limit: float | None
    currency: str | None
    observed_at: str | None
    source: str
    binding: str
    account_key: str | None = None


@dataclass(frozen=True)
class Observation:
    profile_id: str
    provider: str
    model: str
    collector: str
    source: str = "unknown"
    plan: str | None = None
    status: str = "unavailable"
    binding: str = "unverified"
    windows: tuple = ()
    balances: tuple = ()
    caps: tuple = ()
    pace: dict = field(default_factory=dict)
    account_key: str | None = None


class Availability(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.details = {}


def number(value):
    return value if type(value) is int or (type(value) is float and math.isfinite(value)) else None


def fresh(value, now):
    try:
        return -60 <= (now - datetime.fromisoformat(value.replace("Z", "+00:00"))).total_seconds() <= MAX_AGE_S
    except (AttributeError, TypeError, ValueError, OverflowError):
        return False


def model_id(profile):
    args = profile.get("args", [])
    model = profile.get("model_id", "")
    for flag in ("--model", "-m"):
        if flag in args and args.index(flag) + 1 < len(args):
            model = args[args.index(flag) + 1]
    return str(model).lower()


def needs_credits(provider, model, plan):
    return provider == "claude" and "fable" in model and not any(
        x in str(plan or "").lower() for x in ("max", "team", "enterprise"))


def reserve_percent():
    from .routing import InputError
    try:
        value = float(os.environ.get("BENCH_ROUTER_MIN_REMAINING", "10"))
        if math.isfinite(value) and 0 <= value <= 100:
            return value
    except ValueError:
        pass
    raise InputError("BENCH_ROUTER_MIN_REMAINING must be a finite percentage from 0 to 100")


def _reason(o, now, threshold):
    if o.status != "ok" or not o.windows:
        return "quota_unverified"
    if o.binding not in ("matched", "ambient_cli"):
        return "account_mismatch" if o.binding == "mismatch" else "account_unverified"
    for w in o.windows:
        if o.account_key and w.account_key and o.account_key != w.account_key:
            return "account_mismatch"
        if (not isinstance(w, Window) or not isinstance(w.scope, str) or not re.fullmatch(r"[a-zA-Z0-9_.-]{1,120}", w.scope) or number(w.used_percent) is None or w.used_percent < 0
                or not fresh(w.observed_at, now)):
            return "quota_unverified"
        if w.binding not in ("matched", "ambient_cli"):
            return "account_mismatch" if w.binding == "mismatch" else "account_unverified"
    if any(w.used_percent >= 100 for w in o.windows):
        return "quota_exhausted"
    if needs_credits(o.provider, o.model, o.plan):
        balances = [b for b in o.balances if isinstance(b, Balance) and b.kind == "claude_usage_credits"]
        if any(b.binding == "mismatch" or (o.account_key and b.account_key and o.account_key != b.account_key) for b in balances):
            return "credit_account_mismatch"
        for c in o.caps:
            if o.account_key and c.account_key and o.account_key != c.account_key:
                return "credit_account_mismatch"
            if (isinstance(c, SpendCap) and c.binding == "matched" and fresh(c.observed_at, now)
                    and number(c.used) is not None and number(c.limit) is not None and c.limit > 0 and c.used >= c.limit):
                return "spend_limit_exhausted"
        if any(number(c.used) is None or number(c.limit) is None or min(c.used, c.limit) < 0
               or not fresh(c.observed_at, now) for c in o.caps):
            return "credits_unverified"
        if not balances or any(b.status != "measured" or b.binding != "matched" or b.currency != "USD"
                               or number(b.amount) is None or not fresh(b.observed_at, now) for b in balances):
            return "credits_unverified"
        if any(b.amount <= 0 for b in balances):
            return "credits_exhausted"
    if any(100 - w.used_percent < threshold for w in o.windows):
        return "quota_low"
    return None


def _safe(value):
    return value if isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9_.-]{1,120}", value) else "unknown"


def _details(o, reason, now, threshold):
    rows = []
    for w in o.windows:
        if o.status != "ok" or not isinstance(w, Window) or w.binding not in ("matched", "ambient_cli") or (o.account_key and w.account_key and o.account_key != w.account_key) or not fresh(w.observed_at, now) or number(w.used_percent) is None:
            continue
        row = {"scope": _safe(w.scope), "used_percent": w.used_percent,
               "remaining_percent": max(0, 100 - w.used_percent)}
        try:
            row["resets_at"] = datetime.fromisoformat(w.resets_at.replace("Z", "+00:00")).isoformat()
        except (AttributeError, ValueError, TypeError):
            pass
        if number(w.minutes) is not None and w.minutes > 0:
            row["window_minutes"] = w.minutes
        if row not in rows:
            rows.append(row)
    remaining = min((w["remaining_percent"] for w in rows), default=None)
    pace = {}
    if isinstance(o.pace, dict):
        for scope, raw in o.pace.items():
            if scope not in {w["scope"] for w in rows} or not isinstance(raw, dict):
                continue
            p = {}
            if raw.get("stage") in ("ahead", "farAhead", "behind", "farBehind", "onTrack"):
                p["stage"] = raw["stage"]
            if type(raw.get("will_last_to_reset")) is bool:
                p["will_last_to_reset"] = raw["will_last_to_reset"]
            if number(raw.get("eta_seconds")) is not None and raw["eta_seconds"] >= 0:
                p["eta_seconds"] = raw["eta_seconds"]
            if p:
                pace[_safe(scope)] = p
    out = {"collector": _safe(o.collector), "provider": o.provider, "source": _safe(o.source),
           "updated_at": next((w.observed_at for w in o.windows if isinstance(w, Window) and fresh(w.observed_at, now)), None),
           "checked_at": now.isoformat(), "account_binding": o.binding, "windows": rows,
           "remaining_percent": remaining, "reason": reason, "pace": pace,
           "guard": {"min_remaining_percent": threshold, "decision": "unknown" if remaining is None else "low" if remaining < threshold or remaining == 0 else "safe"},
           "warnings": (["ambient_account_unverified"] if o.binding == "ambient_cli" else []) +
                       (["pace_runs_out_before_reset"] if any(p.get("will_last_to_reset") is False for p in pace.values()) else [])}
    if needs_credits(o.provider, o.model, o.plan):
        b = next((b for b in o.balances if isinstance(b, Balance) and b.kind == "claude_usage_credits"), Balance())
        verified = b.binding == "matched" and not (o.account_key and b.account_key and o.account_key != b.account_key) and number(b.amount) is not None and b.status == "measured" and b.currency == "USD" and fresh(b.observed_at, now)
        out["credits"] = {"status": reason if reason and ("credit" in reason or "spend" in reason) else "available" if verified else "codexbar_credits_unverified",
                          "balance": b.amount if verified else None, "currency": b.currency if verified else None,
                          "updated_at": b.observed_at if verified else None, "capability": b.status}
    return out


def probe(profiles, *, collector=None, now=None, runner=None, which=None):
    """Inject a batch collector; no external JSON or tool options cross this boundary."""
    threshold = reserve_percent()
    if collector is None:
        name = os.environ.get("BENCH_ROUTER_USAGE_COLLECTOR", "codexbar")
        if name == "codexbar":
            from .codexbar import collect
        elif name == "codeburn":
            from .codeburn import collect
        else:
            from .routing import InputError
            raise InputError("BENCH_ROUTER_USAGE_COLLECTOR must be codexbar or codeburn")
        collector = lambda ps, *, now: collect(ps, now=now, runner=runner, **({"which": which} if which is not None else {}))
    rows = collector(profiles, now=now or datetime.now(timezone.utc))
    rows = rows if isinstance(rows, dict) else {}
    checked = now or datetime.now(timezone.utc)
    out = Availability()
    for p in profiles:
        provider, model = PROVIDERS.get(p.get("kind")), model_id(p)
        o = rows.get(p["id"])
        if (not isinstance(o, Observation) or o.profile_id != p["id"] or o.provider != provider or o.model != model
                or not all(isinstance(x, tuple) for x in (o.windows, o.balances, o.caps))
                or not all(isinstance(w, Window) for w in o.windows)
                or not all(isinstance(b, Balance) for b in o.balances)
                or not all(isinstance(c, SpendCap) for c in o.caps)):
            o = Observation(p["id"], provider, model, "unknown")
        reason = _reason(o, checked, threshold)
        # Historical public identifiers: keep wire compatibility regardless of collector.
        out[p["id"]] = "codexbar_" + reason if reason else None
        out.details[p["id"]] = _details(o, out[p["id"]], checked, threshold)
    return out
