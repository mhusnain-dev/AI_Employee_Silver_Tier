---
name: dashboard-updater
description: Regenerate the Obsidian Dashboard.md from status.json and the current state of the Inbox, Needs_Action, and Done folders. Use this whenever item counts change so the AI Employee dashboard reflects the latest status.
---

# Dashboard Updater (Agent Skill)

Reads the current vault state and rewrites `Dashboard.md` with live metrics:

- New items = files in `Inbox/`
- In-progress items = files in `Needs_Action/`
- Completed items = files in `Done/`
- Total watcher events logged = `status.json`

This keeps the Obsidian dashboard (the AI Employee's nerve center / GUI) up
to date. Part of the Bronze-Tier deliverables: "Claude Code successfully
reading from and writing to the vault" and a live `Dashboard.md`.

## How to run

```bash
python .claude/skills/dashboard-updater/update_dashboard.py
```

## What it does

1. Loads `status.json` (created by the filesystem-watcher skill).
2. Counts files in `Inbox/`, `Needs_Action/`, `Done/`.
3. Rewrites `Dashboard.md` with the computed counts.
4. Prints a confirmation.

## Notes

- Always regenerates the whole file (deterministic output).
- Safe to run at any time; no side effects outside `Dashboard.md`.
