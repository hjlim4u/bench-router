"""Optional Jev decisions, or a request for the host's cheap native subagent. No dispatch or file writes."""
import argparse
import http.client
import json
import os
import sys
import urllib.request
from pathlib import Path

_SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SKILL if (_SKILL / "bench_router").is_dir() else _SKILL.parents[1]))
from bench_router import routing as r  # noqa: E402

JEV_URL = "https://api.typesafe.ai/v1/systemone"
MAX_BYTES = 1024 * 1024
NATIVE_MODELS = {"antigravity": "flash", "codex": "gpt-6-luna", "claude": "haiku"}


def validate_request(request):
    if not isinstance(request, dict) or set(request) != {"state", "questions"}:
        raise r.InputError("decision request: state and questions required")
    if not isinstance(request["state"], (str, dict, list)):
        raise r.InputError("decision state: text, object or array required")
    questions = request["questions"]
    if not isinstance(questions, dict) or not questions:
        raise r.InputError("decision questions: nonempty object required")
    for name, q in questions.items():
        r._str(name, "decision question ID")
        if (not isinstance(q, dict) or not {"type", "instructions"} <= set(q)
                or set(q) - {"type", "instructions", "criteria"} or q["type"] not in ("choice", "noul")):
            raise r.InputError(f"decision question {name}: choice or noul required")
        r._str(q["instructions"], f"decision question {name}.instructions")
        criteria = q.get("criteria", {})
        if not isinstance(criteria, dict) or not all(v is None or isinstance(v, str) for v in criteria.values()):
            raise r.InputError(f"decision question {name}: criteria must map options to descriptions")
        if q["type"] == "choice" and not 2 <= len(criteria) <= 255:
            raise r.InputError(f"decision question {name}: 2..255 choices required")
        if q["type"] == "noul" and set(criteria) - {"true", "false"}:
            raise r.InputError(f"decision question {name}: noul criteria must use true/false")
        for option in criteria:
            r._str(option, f"decision question {name} option")
    return request


def validate_response(request, response):
    answers = response.get("answers") if isinstance(response, dict) else None
    if not isinstance(answers, dict) or set(answers) != set(request["questions"]):
        raise r.InputError("decision response: one answer per question required")
    out = {}
    for name, q in request["questions"].items():
        a = answers[name]
        if not isinstance(a, dict) or a.get("type") != q["type"]:
            raise r.InputError(f"decision answer {name}: type mismatch")
        if q["type"] == "choice":
            choice = a.get("choice")
            if not isinstance(choice, str) or choice not in q["criteria"]:
                raise r.InputError(f"decision answer {name}: choice outside supplied options")
            out[name] = {"type": "choice", "choice": choice}
        else:
            out[name] = {"type": "noul", "noul": r._num(a.get("noul"), f"decision answer {name}.noul", 0, 1)}
        if "confidence" in a:
            out[name]["confidence"] = r._num(a["confidence"], f"decision answer {name}.confidence", 0, 1)
    return out


def decide(request, env=None, response=None, host=None):
    request = validate_request(request)
    env = os.environ if env is None else env
    if host is not None and host not in NATIVE_MODELS:
        raise r.InputError(f"decision host: one of {sorted(NATIVE_MODELS)} required")
    cheap_model = env.get("BENCH_ROUTER_DECISION_MODEL") or NATIVE_MODELS.get(host, "cheapest_available")
    if response is not None:
        return {"status": "ok", "provider": "subagent", "agent": "bench-decider", "host": host, "model": cheap_model,
                "answers": validate_response(request, response), "confidence_kind": "self_reported"}
    key = (env.get("TYPESAFE_API_KEY") or "").strip() or (env.get("JEV_API_KEY") or "").strip()
    reason = "jev_not_configured"
    if key:
        model = env.get("JEV_MODEL") or "jev-1.13.0"
        req = urllib.request.Request(JEV_URL, json.dumps({**request, "model": model}, ensure_ascii=False).encode("utf-8"),
                                     {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as res:
                body = res.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise r.InputError("decision response too large")
            raw = json.loads(body.decode("utf-8"), object_pairs_hook=r._no_dupes, parse_constant=r._reject_const)
            answers = validate_response(request, raw)
            usage = raw.get("usage", {})
            if not isinstance(usage, dict):
                raise r.InputError("decision usage: object required")
            usage = {k: r._int(usage[k], f"decision usage.{k}", 0) for k in ("input_tokens", "output_tokens") if k in usage}
            return {"status": "ok", "provider": "jev", "model": r._str(raw.get("model"), "decision model"),
                    "answers": answers, "usage": usage, "confidence_kind": "provider_reported"}
        except (OSError, ValueError, http.client.HTTPException):
            # No response bodies or credentials in the fallback packet; the host owns subagent invocation.
            reason = "jev_unavailable"
    return {"status": "subagent_required", "provider": "subagent", "agent": "bench-decider", "host": host, "model": cheap_model,
            "reason": reason, "request": request}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--request", required=True, help="JSON: state plus choice/noul questions")
    ap.add_argument("--host", choices=sorted(NATIVE_MODELS), help="current Orchestrator; selects its native bench-decider model")
    ap.add_argument("--response", help="validate a native subagent's JSON response instead of calling Jev")
    args = ap.parse_args(argv)
    try:
        request = r.load_json_strict(args.request, MAX_BYTES)
        response = r.load_json_strict(args.response, MAX_BYTES) if args.response else None
        if args.response and not isinstance(response, dict):
            raise r.InputError("decision response: object required")
        result = decide(request, response=response, host=args.host)
    except (r.InputError, OSError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
