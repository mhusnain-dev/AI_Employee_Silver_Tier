#!/usr/bin/env python
"""
Bronze‑Tier File‑System Watcher

Monitors the Inbox folder for newly created files.
When a file appears it is moved to Needs_Action and a record is appended
to status.json.  The script runs continuously until interrupted.
"""

import json
import os
import sys
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

# ----- Configuration -----
INBOX_DIR = Path("Inbox")
STATUS_FILE = Path("status.json")
# -------------------------

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event: FileCreatedEvent):
        # Ignore directories – only watch files
        if event.is_directory:
            return

        src_path = Path(event.src_path)

        # Only react to files created inside the Inbox folder
        if src_path.parent.resolve() != INBOX_DIR.resolve():
            return

        # Move the file to Needs_Action
        dest_path = Path("Needs_Action") / src_path.name
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

        print(f"✅ Moved '{src_path.name}' → 'Needs_Action/' and logged to status.json")


if __name__ == "__main__":
    # Allow optional command‑line argument to override the default Inbox path
    import argparse
    parser = argparse.ArgumentParser(description="Bronze‑Tier filesystem watcher")
    parser.add_argument(
        "--inbox",
        default=str(INBOX_DIR),
        help="Path to the Inbox directory to monitor (default: Inbox)",
    )
    args = parser.parse_args()
    monitored_path = Path(args.inbox)

    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(monitored_path), recursive=False)
    observer.start()
    print(f"👀 Watching '{monitored_path}' for new files… (Ctrl‑C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Stopping watcher…")
    observer.join()