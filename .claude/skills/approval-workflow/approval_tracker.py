#!/usr/bin/env python
"""
Approval Workflow Tracker (Agent Skill)

Helps Claude Code manage the Human-in-the-Loop approval workflow:

- list <state>   : list approval files in Pending_Approval|Approved|Rejected
- status         : print counts for each state
- complete <file>: an action in Approved/ was executed; log it and archive to Done/
- cancel <file>  : an action in Rejected/ was cancelled; log it and archive to Done/

Logs go to Logs/YYYY-MM-DD.json in the vault root (doc §6.3 audit format).
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_vault_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "Inbox").is_dir() and (candidate / "Dashboard.md").is_file():
            return candidate
    return Path.cwd()


ROOT = find_vault_root()
STATES = {
    "pending": ROOT / "Pending_Approval",
    "approved": ROOT / "Approved",
    "rejected": ROOT / "Rejected",
}
DONE_DIR = ROOT / "Done"
LOGS_DIR = ROOT / "Logs"


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta


def list_files(state: str):
    directory = STATES[state]
    files = sorted(directory.glob("*.md")) if directory.exists() else []
    if not files:
        print(f"No files in {directory.relative_to(ROOT)}")
        return
    for f in files:
        meta = read_frontmatter(f)
        action = meta.get("action", "?")
        target = meta.get("target", "?")
        reason = meta.get("reason", "")
        print(f"{f.name} | action={action} | target={target} | reason={reason}")


def status():
    for state, directory in STATES.items():
        count = len(list(directory.glob("*.md"))) if directory.exists() else 0
        print(f"{state}: {count}")
    done = len(list(DONE_DIR.glob("*.md"))) if DONE_DIR.exists() else 0
    print(f"done: {done}")


def log_action(path: Path, result: str):
    meta = read_frontmatter(path)
    LOGS_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"{today}.json"
    entries = []
    if log_file.exists():
        try:
            entries = json.loads(log_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            entries = []
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_type": meta.get("action", "unknown"),
        "actor": "claude_code",
        "target": meta.get("target", ""),
        "parameters": {"file": path.name, "reason": meta.get("reason", "")},
        "approval_status": meta.get("status", "approved"),
        "approved_by": "human",
        "result": result,
    }
    entries.append(entry)
    log_file.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    print(f"✅ Logged {result} action to {log_file.name}")


def archive(path: Path, state: str):
    DONE_DIR.mkdir(exist_ok=True)
    dest = DONE_DIR / path.name
    path.rename(dest)
    print(f"✅ Archived {path.name} → {DONE_DIR.name}/")


def main():
    parser = argparse.ArgumentParser(description="Approval workflow tracker")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="counts per state")
    list_p = sub.add_parser("list", help="list approval files")
    list_p.add_argument("state", choices=list(STATES.keys()))

    complete = sub.add_parser("complete", help="mark approved action as executed")
    complete.add_argument("file", help="filename in Approved/")
    cancel = sub.add_parser("cancel", help="mark rejected action as cancelled")
    cancel.add_argument("file", help="filename in Rejected/")

    args = parser.parse_args()

    if args.command == "status":
        status()
    elif args.command == "list":
        list_files(args.state)
    elif args.command in ("complete", "cancel"):
        state = "approved" if args.command == "complete" else "rejected"
        path = STATES[state] / args.file
        if not path.exists():
            print(f"❌ {args.file} not found in {state}/", file=sys.stderr)
            sys.exit(1)
        log_action(path, args.command)
        archive(path, state)


if __name__ == "__main__":
    main()
