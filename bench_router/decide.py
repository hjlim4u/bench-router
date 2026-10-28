"""Optional Jev decisions, or a request for the host's cheap native subagent. No dispatch or file writes."""
import argparse
import json

from bench_router import routing as r
from bench_router.decision_provider import (
    MAX_BYTES, NATIVE_MODELS, decide,
)


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
