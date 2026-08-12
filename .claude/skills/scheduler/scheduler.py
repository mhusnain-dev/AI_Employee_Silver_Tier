#!/usr/bin/env python
"""
Scheduler Skill (Agent Skill)

Runs watchers and dashboard updater on a configurable schedule.
Supports cron-like intervals and one-shot runs.
Also provides Windows Task Scheduler and Linux cron examples.

Usage:
  python .claude/skills/scheduler/scheduler.py --once
  python .claude/skills/scheduler/scheduler.py --interval 300  # every 5 min
"""

import argparse
import asyncio
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def find_vault_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "Inbox").is_dir() and (candidate / "Dashboard.md").is_file():
            return candidate
    return Path.cwd()


ROOT = find_vault_root()
PYTHON = sys.executable
SKILLS_DIR = ROOT / ".claude" / "skills"


def run_cmd(cmd: list, cwd: Path = ROOT) -> tuple:
    """Run command, return (success, output)."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def run_watchers(once: bool = False) -> bool:
    """Run filesystem watcher (and gmail watcher if credentials exist)."""
    fs_script = SKILLS_DIR / "filesystem-watcher" / "filesystem_watcher.py"
    gmail_script = SKILLS_DIR / "gmail-watcher" / "gmail_watcher.py"

    ok = True
    if fs_script.exists():
        args = [PYTHON, str(fs_script)]
        if once:
            args.append("--once")
        success, out = run_cmd(args)
        if not success:
            print(f"⚠️ filesystem-watcher: {out}")
            ok = False
        else:
            print(f"✅ filesystem-watcher: {out}")

    if gmail_script.exists() and (ROOT / "credentials.json").exists():
        args = [PYTHON, str(gmail_script)]
        if once:
            args.append("--once")
        success, out = run_cmd(args)
        if not success:
            print(f"⚠️ gmail-watcher: {out}")
            ok = False
        else:
            print(f"✅ gmail-watcher: {out}")
    elif gmail_script.exists():
        print("ℹ️ gmail-watcher: credentials.json not found, skipping (use --mock for testing)")

    return ok


def run_dashboard() -> bool:
    """Regenerate Dashboard.md from current vault state."""
    script = SKILLS_DIR / "dashboard-updater" / "update_dashboard.py"
    if not script.exists():
        return True
    success, out = run_cmd([PYTHON, str(script)])
    if not success:
        print(f"⚠️ dashboard-updater: {out}")
        return False
    print(f"✅ {out}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Scheduler for AI Employee watchers and dashboard")
    parser.add_argument("--once", action="store_true", help="run once and exit")
    parser.add_argument("--interval", type=int, default=300, help="interval in seconds (default: 300)")
    parser.add_argument("--watchers-only", action="store_true", help="only run watchers, skip dashboard")
    parser.add_argument("--dashboard-only", action="store_true", help="only run dashboard updater")
    args = parser.parse_args()

    print(f"🕐 Scheduler started at {datetime.now().isoformat()}")
    if args.once:
        print("Running one cycle...")
    else:
        print(f"Running every {args.interval}s. Press Ctrl-C to stop.")

    try:
        while True:
            cycle_start = time.time()
            print(f"\n--- Cycle at {datetime.now().isoformat()} ---")

            if not args.dashboard_only:
                run_watchers(once=args.once)

            if not args.watchers_only:
                run_dashboard()

            if args.once:
                break

            elapsed = time.time() - cycle_start
            sleep_time = max(0, args.interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped.")


if __name__ == "__main__":
    main()