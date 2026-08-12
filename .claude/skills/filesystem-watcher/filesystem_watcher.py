#!/usr/bin/env python
"""
Bronze-Tier File-System Watcher (Agent Skill)

Monitors the vault Inbox folder for newly created files.
When a file appears it is moved to Needs_Action and a record is appended
to status.json.  The script runs continuously until interrupted.
"""

import json
import sys
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

# ----- Configuration -----
STATUS_FILE_NAME = "status.json"


def find_vault_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "Inbox").is_dir() and (candidate / "Dashboard.md").is_file():
            return candidate
    return Path.cwd()


ROOT = find_vault_root()
STATUS_FILE = ROOT / STATUS_FILE_NAME


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, inbox_dir: Path, needs_action_dir: Path):
        self.inbox_dir = inbox_dir.resolve()
        self.needs_action_dir = needs_action_dir.resolve()

    def on_created(self, event: FileCreatedEvent):
        # Ignore directories – only watch files
        if event.is_directory:
            return

        src_path = Path(event.src_path)

        # Only react to files created inside the monitored Inbox folder
        if src_path.parent.resolve() != self.inbox_dir:
            return

        # Move the file to Needs_Action
        dest_path = self.needs_action_dir / src_path.name
        src_path.rename(dest_path)

        # Record the event in status.json
        record = {
            "event": "new_item",
            "file": dest_path.name,
            "timestamp": time.time()
        }

        # Load existing status or start a new structure
        if STATUS_FILE.exists():
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {"items": []}
        else:
            data = {"items": []}

        data["items"].append(record)

        # Persist the updated status
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Moved '{src_path.name}' → '{dest_path.name}' and logged to status.json", file=sys.stdout, flush=True)


def process_existing_files(inbox_dir: Path, needs_action_dir: Path):
    """One-shot: move all existing files from Inbox to Needs_Action."""
    inbox_dir = inbox_dir.resolve()
    needs_action_dir = needs_action_dir.resolve()
    count = 0
    for src_path in inbox_dir.iterdir():
        if src_path.is_file():
            dest_path = needs_action_dir / src_path.name
            src_path.rename(dest_path)
            record = {
                "event": "new_item",
                "file": dest_path.name,
                "timestamp": time.time()
            }
            if STATUS_FILE.exists():
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {"items": []}
            else:
                data = {"items": []}
            data["items"].append(record)
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"✅ Moved '{src_path.name}' → '{dest_path.name}' and logged to status.json", file=sys.stdout, flush=True)
            count += 1
    return count


if __name__ == "__main__":
    import argparse

    default_inbox = ROOT / "Inbox"
    default_needs_action = ROOT / "Needs_Action"

    parser = argparse.ArgumentParser(description="Bronze-Tier filesystem watcher")
    parser.add_argument(
        "--inbox",
        default=str(default_inbox),
        help=f"Path to the Inbox directory to monitor (default: {default_inbox})",
    )
    parser.add_argument(
        "--needs-action",
        default=str(default_needs_action),
        help=f"Path to the Needs_Action directory (default: {default_needs_action})",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process existing files in Inbox once and exit (for scheduler/cron)",
    )
    args = parser.parse_args()

    monitored_path = Path(args.inbox).resolve()
    needs_action_path = Path(args.needs_action).resolve()

    if not monitored_path.exists():
        print(f"❌ Inbox path does not exist: {monitored_path}", file=sys.stderr, flush=True)
        sys.exit(1)
    if not needs_action_path.exists():
        print(f"❌ Needs_Action path does not exist: {needs_action_path}", file=sys.stderr, flush=True)
        sys.exit(1)

    if args.once:
        count = process_existing_files(monitored_path, needs_action_path)
        print(f"✅ One-shot complete: processed {count} file(s).", flush=True)
        sys.exit(0)

    event_handler = NewFileHandler(monitored_path, needs_action_path)
    observer = Observer()
    observer.schedule(event_handler, str(monitored_path), recursive=False)
    observer.start()
    print(f"👀 Watching '{monitored_path}' for new files… (Ctrl-C to stop)", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Stopping watcher…", flush=True)
    observer.join()
