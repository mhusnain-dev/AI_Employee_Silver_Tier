---
name: filesystem-watcher
description: Monitor the vault Inbox folder for newly created files, move them to Needs_Action, and log each event to status.json. Use this whenever the AI Employee needs to detect new items dropped into the Inbox and hand them off for processing.
---

# Filesystem Watcher (Agent Skill)

The AI Employee's sensory layer for file drops. Watches the Obsidian vault's
`Inbox/` folder and, whenever a new file appears, moves it to `Needs_Action/`
and appends a `new_item` record to `status.json` at the vault root.

This is one of the Bronze-Tier deliverables from the hackathon brief:
"One working Watcher script (file system monitoring)".

## How to run

```bash
# Start watching (runs continuously until Ctrl-C)
python .claude/skills/filesystem-watcher/filesystem_watcher.py
```

Optional flags (defaults resolve to the vault root):

```bash
python .claude/skills/filesystem-watcher/filesystem_watcher.py --inbox Inbox --needs-action Needs_Action
```

## What it does

1. Watches `Inbox/` (non-recursive) for newly created files.
2. Moves each new file to `Needs_Action/`.
3. Appends `{"event": "new_item", "file": ..., "timestamp": ...}` to `status.json`.
4. Keeps running until interrupted.

## Prerequisites

- `watchdog` installed (see root `requirements.txt`):
  `pip install -r requirements.txt`

## Notes

- Only newly created files are handled; edits to existing files are ignored.
- Directories are ignored.
- To watch a custom folder, pass `--inbox <path>` (the `Needs_Action` sibling
  must exist).
