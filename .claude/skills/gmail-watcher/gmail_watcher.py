#!/usr/bin/env python
"""
Gmail Watcher (Agent Skill)

Polls the Gmail account for new unread/important emails and writes one
Needs_Action/EMAIL_<id>.md per new email so Claude Code can process it
(hackathon doc §"Gmail Watcher Implementation").

Modes:
  normal   : requires Gmail OAuth (credentials.json + token.json)
  --mock   : no credentials needed; generates sample emails for verification
  --dry-run: logs what it would do without writing files

Usage:
  python .claude/skills/gmail-watcher/authenticate.py        # one-time OAuth
  python .claude/skills/gmail-watcher/gmail_watcher.py        # poll forever
  python .claude/skills/gmail-watcher/gmail_watcher.py --mock --once
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    Request = Credentials = InstalledAppFlow = build = HttpError = None


def find_vault_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "Inbox").is_dir() and (candidate / "Dashboard.md").is_file():
            return candidate
    return Path.cwd()


ROOT = find_vault_root()
NEEDS_ACTION = ROOT / "Needs_Action"
CREDENTIALS = ROOT / "credentials.json"
TOKEN = ROOT / "token.json"
CACHE = ROOT / ".gmail_cache.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
QUERY = "is:unread is:important"
KEYWORDS = ["urgent", "asap", "invoice", "payment", "help", "pricing"]


def load_cache() -> set:
    if CACHE.exists():
        try:
            return set(json.loads(CACHE.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            return set()
    return set()


def save_cache(processed: set):
    CACHE.write_text(json.dumps(sorted(processed), indent=2), encoding="utf-8")


def get_service(mock: bool):
    if mock:
        return None
    if not CREDENTIALS.exists():
        raise FileNotFoundError(
            f"{CREDENTIALS.name} not found. Run authenticate.py first, or use --mock."
        )
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds)


MOCK_MESSAGES = [
    {
        "id": "mock001",
        "from": "client@example.com",
        "subject": "Urgent: Invoice request for January",
        "snippet": "Hi, could you send the invoice for January asap?",
    },
    {
        "id": "mock002",
        "from": "lead@prospects.com",
        "subject": "Pricing question about your services",
        "snippet": "I saw your LinkedIn post and I'd like to know your pricing.",
    },
    {
        "id": "mock003",
        "from": "bank@notifications.com",
        "subject": "Payment reminder",
        "snippet": "Your payment of $500 is due tomorrow.",
    },
]


def fetch_messages(mock: bool):
    if mock:
        return MOCK_MESSAGES
    service = get_service(mock=False)
    results = service.users().messages().list(userId="me", q=QUERY).execute()
    messages = results.get("messages", [])
    out = []
    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"]).execute()
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        snippet = msg.get("snippet", "")
        if not any(kw.lower() in (headers.get("Subject", "") + snippet).lower() for kw in KEYWORDS):
            continue
        out.append(
            {
                "id": m["id"],
                "from": headers.get("From", "Unknown"),
                "subject": headers.get("Subject", "No Subject"),
                "snippet": snippet,
            }
        )
    return out


def priority_for(subject: str) -> str:
    low = subject.lower()
    if any(k in low for k in ("urgent", "asap", "emergency")):
        return "high"
    if any(k in low for k in ("invoice", "payment", "billing")):
        return "high"
    return "normal"


def create_action_file(message: dict, dry_run: bool) -> Path:
    now = datetime.now(timezone.utc).isoformat()
    content = f"""---
type: email
from: {message['from']}
subject: {message['subject']}
received: {now}
priority: {priority_for(message['subject'])}
status: pending
gmail_id: {message['id']}
---

## Email Content
{message['snippet']}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
"""
    path = NEEDS_ACTION / f"EMAIL_{message['id']}.md"
    if dry_run:
        print(f"[DRY RUN] Would write {path}", flush=True)
        return path
    path.write_text(content, encoding="utf-8")
    print(f"✅ Created {path.name}", flush=True)
    return path


def main():
    parser = argparse.ArgumentParser(description="Gmail watcher")
    parser.add_argument("--mock", action="store_true", help="use sample emails (no credentials)")
    parser.add_argument("--interval", type=int, default=120, help="poll interval in seconds")
    parser.add_argument("--once", action="store_true", help="poll once and exit")
    parser.add_argument("--dry-run", action="store_true", help="log intended actions without writing")
    args = parser.parse_args()

    NEEDS_ACTION.mkdir(exist_ok=True)
    processed = load_cache()

    print(
        f"{'MOCK' if args.mock else 'Gmail'} watcher started "
        f"(query: {QUERY if not args.mock else 'sample data'})…",
        flush=True,
    )

    while True:
        try:
            messages = fetch_messages(args.mock)
            for m in messages:
                if m["id"] in processed:
                    continue
                create_action_file(m, args.dry_run)
                processed.add(m["id"])
            save_cache(processed)
        except HttpError as e:
            print(f"⚠️ Gmail API error: {e}", flush=True)
        except FileNotFoundError as e:
            print(f"⚠️ {e}", flush=True)
            print("Run: python .claude/skills/gmail-watcher/authenticate.py", flush=True)
        except Exception as e:
            print(f"⚠️ Error: {e}", flush=True)
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
