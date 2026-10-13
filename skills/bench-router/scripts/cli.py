"""Run the repository CLI from a linked skill directory or any working directory."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from bench_router.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
