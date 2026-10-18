"""Run the CLI from a copied or linked skill directory, or from the repository."""
import sys
from pathlib import Path

_SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SKILL if (_SKILL / "bench_router").is_dir() else _SKILL.parents[1]))

from bench_router.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())


