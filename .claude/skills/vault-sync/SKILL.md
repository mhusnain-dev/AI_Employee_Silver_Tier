---
name: vault-sync
description: Demonstrate that the AI Employee can read from and write to the Obsidian vault by appending a timestamped sync marker to Dashboard.md. Use this to prove or test vault read/write capability.
---

# Vault Sync (Agent Skill)

Proves the core Bronze-Tier capability: **Claude Code successfully reading
from and writing to the vault**. The skill reads the current `Dashboard.md`,
appends a timestamped "auto-synced" marker, and writes it back.

## How to run

```bash
python .claude/skills/vault-sync/vault_sync.py
```

## What it does

1. Reads the current `Dashboard.md` from the vault root.
2. Appends `# Auto-synced by vault_sync.py on <UTC timestamp>` if not present
   (idempotent).
3. Writes the updated content back to `Dashboard.md`.
4. Prints a confirmation.

## Notes

- Idempotent: running twice does not duplicate the marker.
- Demonstrates read + write in one script; used as the read/write proof for
  Bronze Tier.
