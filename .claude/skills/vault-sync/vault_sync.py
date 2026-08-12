#!/usr/bin/env python
"""
Bronze-Tier Vault Sync (Agent Skill)

A tiny utility that demonstrates the AI Employee can read from and write to
the vault (Dashboard.md).  It:

1. Loads the current Dashboard.md.
2. Appends a timestamped "synced" note (simulating a write).
3. Saves the updated content back to Dashboard.md.

This script is deliberately simple so it can be invoked from any other
automation (e.g., from the filesystem watcher) to prove that the vault is
read-write capable.
"""

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
VAULT_MD = ROOT / "Dashboard.md"

def read_vault():
    if not VAULT_MD.exists():
        print(f"❌ {VAULT_MD} not found.", file=sys.stderr)
        sys.exit(1)
    return VAULT_MD.read_text(encoding="utf-8")

def write_vault(new_content):
    VAULT_MD.write_text(new_content, encoding="utf-8")
    print(f"✅ Updated {VAULT_MD}")

def main():
    # 1️⃣ Read current vault content
    content = read_vault()

    # 2️⃣ Append a sync marker (idempotent)
    marker = f"\n# Auto-synced by vault_sync.py on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
    if marker.strip() not in content:
        content += marker

    # 3️⃣ Write back the enriched content
    write_vault(content)

if __name__ == "__main__":
    main()
