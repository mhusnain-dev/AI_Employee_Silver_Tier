#!/usr/bin/env python
"""
Gmail OAuth authentication helper (Agent Skill)

Run ONCE to obtain token.json for the Gmail watcher and email MCP server:

    python .claude/skills/gmail-watcher/authenticate.py

Prerequisites:
- credentials.json (OAuth client) must be in the vault root.
  Create it at https://console.cloud.google.com/apis/credentials
- Enable the Gmail API for your project first.

token.json is never committed (gitignored).
"""

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow


def find_vault_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "Inbox").is_dir() and (candidate / "Dashboard.md").is_file():
            return candidate
    return Path.cwd()


ROOT = find_vault_root()
CREDENTIALS = ROOT / "credentials.json"
TOKEN = ROOT / "token.json"
# Superset: read (watcher) + send/compose (email MCP server)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]


def main():
    if not CREDENTIALS.exists():
        raise SystemExit(
            f"❌ {CREDENTIALS} not found. Download your OAuth client JSON from "
            "https://console.cloud.google.com/apis/credentials and place it in the vault root."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    print(f"✅ Authentication complete. Saved {TOKEN}")


if __name__ == "__main__":
    main()
