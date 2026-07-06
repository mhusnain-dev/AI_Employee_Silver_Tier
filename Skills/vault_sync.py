#!/usr/bin/env python
"""
Bronze‑Tier Vault Sync

A tiny utility that demonstrates Claude Code can read from and write to the
vault (Dashboard.md).  It:

1. Loads the current Dashboard.md.
2. Appends a timestamped “synced” note (simulating a write).
3. Saves the updated content back to Dashboard.md.

This script is deliberately simple so it can be invoked from any other
automation (e.g., from the filesystem watcher) to prove that the vault is
read‑write capable.
"""

import sys
from pathlib import Path
from datetime import datetime

VAULT_MD = Path("Dashboard.md")

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
    marker = f"\n# Auto‑synced by vault_sync.py on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
    if marker.strip() not in content:
        content += marker

    # 3️⃣ Write back the enriched content
    write_vault(content)

if __name__ == "__main__":
    main()