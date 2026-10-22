"""CodeBurn integration helper for bench-router.

Wraps the CodeBurn CLI (https://github.com/getagentseal/codeburn) to track
AI coding token usage and costs across Claude Code, Codex, Antigravity CLI,
and other agents operating in this project.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_PROJECT = "bench-router"


def find_codeburn() -> str | None:
    """Find codeburn executable in PATH or npx fallback."""
    return shutil.which("codeburn")


def run_codeburn_cmd(cmd_args: list[str], capture_output: bool = False) -> subprocess.CompletedProcess:
    """Execute codeburn command."""
    bin_path = find_codeburn()
    if bin_path:
        full_cmd = [bin_path] + cmd_args
    else:
        npx = shutil.which("npx")
        if not npx:
            raise RuntimeError("Neither 'codeburn' nor 'npx' is available in PATH. Run: npm install -g codeburn")
        full_cmd = [npx, "--yes", "codeburn"] + cmd_args

    return subprocess.run(
        full_cmd,
        capture_output=capture_output,
        text=True,
        check=False
    )


def get_status() -> str:
    """Get compact status string (today + month)."""
    proc = run_codeburn_cmd(["status"], capture_output=True)
    return proc.stdout.strip()


def get_overview(project: str = DEFAULT_PROJECT, period: str = "month") -> str:
    """Get text overview table filtered by project."""
    proc = run_codeburn_cmd(["overview", "--project", project, "--period", period], capture_output=True)
    return proc.stdout


def export_json(project: str = DEFAULT_PROJECT, out_path: str | None = None) -> str:
    """Export usage data as JSON."""
    args = ["export", "-f", "json", "--project", project]
    if out_path:
        args += ["-o", out_path]
    proc = run_codeburn_cmd(args, capture_output=True)
    return proc.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 eval/codeburn.py",
        description="CodeBurn token & cost tracking integration for bench-router"
    )
    sub = parser.add_subparsers(dest="action")

    p_status = sub.add_parser("status", help="Show compact today + month spend")

    p_overview = sub.add_parser("overview", help="Show detailed usage table for project")
    p_overview.add_argument("--project", default=DEFAULT_PROJECT, help="Project name (default: bench-router)")
    p_overview.add_argument("--period", default="month", choices=["today", "week", "30days", "month", "all", "lifetime"])

    p_export = sub.add_parser("export", help="Export project usage to JSON/CSV")
    p_export.add_argument("--format", default="json", choices=["json", "csv"])
    p_export.add_argument("--project", default=DEFAULT_PROJECT)
    p_export.add_argument("-o", "--output", help="Output file path")

    p_web = sub.add_parser("web", help="Launch CodeBurn web dashboard")
    p_doctor = sub.add_parser("doctor", help="Check provider detection health")

    p_hook = sub.add_parser("antigravity-hook", help="Install/uninstall Antigravity CLI usage hook")
    p_hook.add_argument("mode", choices=["install", "uninstall"])

    args = parser.parse_args(argv)

    if not args.action:
        parser.print_help()
        return 0

    if args.action == "status":
        print(get_status())
        return 0
    elif args.action == "overview":
        print(get_overview(project=args.project, period=args.period))
        return 0
    elif args.action == "export":
        cmd = ["export", "-f", args.format, "--project", args.project]
        if args.output:
            cmd += ["-o", args.output]
        proc = run_codeburn_cmd(cmd)
        return proc.returncode
    elif args.action == "web":
        proc = run_codeburn_cmd(["web"])
        return proc.returncode
    elif args.action == "doctor":
        proc = run_codeburn_cmd(["doctor"])
        return proc.returncode
    elif args.action == "antigravity-hook":
        proc = run_codeburn_cmd(["antigravity-hook", args.mode])
        return proc.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
