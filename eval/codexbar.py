"""Pass native CodexBar commands through without maintaining a second report schema.

Examples: python3 -m eval.codexbar usage --provider claude --json
          python3 -m eval.codexbar cost --provider codex --group-by project
          python3 -m eval.codexbar serve --port 8080
JSON export: redirect `cost --json` to a file. Provider failures retain their exit status.
"""
import os
import shutil
import subprocess
import sys


def main(argv=None):
    exe = os.environ.get("BENCH_ROUTER_CODEXBAR", "codexbar")
    if not shutil.which(exe):
        print("CodexBar is not installed. Run: mise run install-codexbar", file=sys.stderr)
        return 69
    try:
        return subprocess.run([exe, *(sys.argv[1:] if argv is None else argv)], check=False).returncode
    except OSError:
        print("Unable to start CodexBar", file=sys.stderr)
        return 69


if __name__ == "__main__":
    sys.exit(main())
