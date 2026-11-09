"""Optional CodeBurn 0.9.27 quota adapter. No installation or paid probes at runtime."""
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from . import usage as policy


def collect(profiles, *, now, runner=None, which=shutil.which):
    binary = os.environ.get("BENCH_ROUTER_CODEBURN", "codeburn")
    providers = []
    if which(binary):
        try:
            # Reuse the owned subprocess lifecycle, not CodexBar's schema or policy.
            from .usage_process import run_cli
            proc = (runner or run_cli)([binary, "quota", "--format", "json"], capture_output=True,
                                      text=True, encoding="utf-8", errors="replace", timeout=120, shell=False)
            raw = json.loads(proc.stdout) if proc.returncode == 0 and len(proc.stdout.encode()) <= 8 * 1024 * 1024 else {}
            providers = raw.get("providers", []) if isinstance(raw, dict) else []
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    providers = providers if isinstance(providers, list) else []
    stamp = max(now, datetime.now(timezone.utc)).isoformat() if runner is None else now.isoformat()
    out = {}
    for p in profiles:
        provider, model = policy.PROVIDERS.get(p.get("kind")), policy.model_id(p)
        rows = [x for x in providers if isinstance(x, dict) and x.get("id") == provider]
        row = rows[0] if len(rows) == 1 else {}
        windows = []
        raw_windows = row.get("windows")
        for w in raw_windows if isinstance(raw_windows, list) else []:
            if not isinstance(w, dict) or not isinstance(w.get("label"), str):
                continue
            label = w["label"].casefold()
            scope = "primary" if label == "5-hour" else "secondary" if label == "weekly" else None
            family = next((f for f in ("fable", "opus", "sonnet", "haiku") if f in model), None)
            if provider == "claude" and family and label == "weekly · " + family:
                scope = "model-" + family
            if provider == "antigravity":
                scope = None
                pool = "gemini" if model.startswith("gemini") else "3p" if model.startswith(("claude", "gpt")) else None
                group, _, bucket = label.partition(" · ")
                groups = {"gemini": {"gemini", "gemini models"},
                          "3p": {"claude and gpt", "claude + gpt", "claude/gpt"}}
                if pool and group in groups[pool]:
                    if bucket in {"5-hour", "session", pool + "-5h", "gemini 5-hour" if pool == "gemini" else "claude/gpt 5-hour"}:
                        scope = pool + "-session"
                    elif bucket in {"weekly", pool + "-weekly", "gemini weekly" if pool == "gemini" else "claude/gpt weekly"}:
                        scope = pool + "-weekly"
                if re.sub(r"[^a-z0-9]", "", label) == re.sub(r"[^a-z0-9]", "", model):
                    scope = "model-" + model
            if scope:
                windows.append(policy.Window(scope, w.get("usedPct"), stamp, "live",
                                             w.get("resetsAt"), 300 if scope == "primary" or scope.endswith("-session") else
                                             10080 if scope == "secondary" or scope.endswith("-weekly") or provider == "claude" else None))
        out[p["id"]] = policy.Observation(p["id"], provider, model, "codeburn", "live", row.get("plan"),
            "ok" if row.get("available") is True else "unavailable", "ambient_cli", tuple(windows),
            (policy.Balance(status="unsupported"),) if provider == "claude" else ())
    return out
