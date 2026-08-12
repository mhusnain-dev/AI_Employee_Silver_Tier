#!/usr/bin/env python
"""
Email MCP Server — the AI Employee's "Hands" for email (hackathon doc §C Action).

A custom Model Context Protocol server (stdio) exposing Gmail tools to
Claude Code:
  - search_email(query)         -> find emails
  - draft_email(to, subject, ...) -> create a Gmail draft
  - send_email(to, subject, ...) -> send, ONLY after approval (or known-contact auto-send)

Sending is gated by the Human-in-the-Loop workflow:
  1. send_email to an unknown contact -> writes Pending_Approval/EMAIL_SEND_<to>.md
  2. human moves it to Approved/
  3. send_email is called again (or Claude retries) -> finds the approved file, sends,
     logs to Logs/, and archives via the approval tracker.

Modes:
  normal  : requires token.json (run authenticate.py once)
  --mock  : no credentials; canned responses for verification

Run via .mcp.json:
  "command": "python", "args": ["mcp-servers/email_mcp/server.py"]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp_types as types

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    Request = Credentials = build = HttpError = None

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]

MOCK = False


def find_vault_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "Inbox").is_dir() and (candidate / "Dashboard.md").is_file():
            return candidate
    return Path.cwd()


ROOT = find_vault_root()
TOKEN = ROOT / "token.json"
PENDING = ROOT / "Pending_Approval"
APPROVED = ROOT / "Approved"
LOGS = ROOT / "Logs"
HANDBOOK = ROOT / "Company_Handbook.md"
KNOWN_CONTACTS_JSON = ROOT / "known_contacts.json"


# ---------- helpers ----------

def get_service():
    if not TOKEN.exists():
        raise RuntimeError("token.json not found — run .claude/skills/gmail-watcher/authenticate.py first.")
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError("Gmail credentials invalid/expired — re-run authenticate.py.")
    return build("gmail", "v1", credentials=creds)


def known_contacts() -> set:
    contacts = set()
    if KNOWN_CONTACTS_JSON.exists():
        try:
            data = json.loads(KNOWN_CONTACTS_JSON.read_text(encoding="utf-8"))
            contacts.update(data.get("known_contacts", []))
        except json.JSONDecodeError:
            pass
    if HANDBOOK.exists():
        m = re.search(r"known_contacts:\n((?:[ \t]*-[ \t]*\S+\n?)+)", HANDBOOK.read_text(encoding="utf-8"))
        if m:
            for line in m.group(1).splitlines():
                match = re.match(r"\s*-\s*(\S+)", line)
                if match:
                    contacts.add(match.group(1))
    return contacts


def find_approved(target: str) -> Optional[Path]:
    if not APPROVED.exists():
        return None
    for f in APPROVED.glob("*.md"):
        text = f.read_text(encoding="utf-8")
        if "action: send_email" in text and target.lower() in text.lower():
            return f
    return None


def log_action(action_type: str, target: str, result: str):
    LOGS.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = LOGS / f"{today}.json"
    entries = []
    if log_file.exists():
        try:
            entries = json.loads(log_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            entries = []
    entries.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_type": action_type,
        "actor": "claude_code",
        "target": target,
        "parameters": {},
        "approval_status": "approved",
        "approved_by": "human",
        "result": result,
    })
    log_file.write_text(json.dumps(entries, indent=2), encoding="utf-8")


# ---------- tool handlers ----------

async def _search_email(query: str) -> types.CallToolResult:
    if MOCK:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps([
                {"id": "mock001", "from": "client@example.com", "subject": "Invoice request", "snippet": "Can you send the invoice for January?"}
            ]))]
        )
    service = get_service()
    results = service.users().messages().list(userId="me", q=query, maxResults=10).execute()
    messages = results.get("messages", [])
    out = []
    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"]).execute()
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        out.append({
            "id": m["id"],
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "snippet": msg.get("snippet", ""),
        })
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(out))]
    )


async def _draft_email(to: str, subject: str, body: str) -> types.CallToolResult:
    if MOCK:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps({"status": "mock_draft_created", "to": to, "subject": subject}))]
        )
    from email.message import EmailMessage
    import base64
    service = get_service()
    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject
    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    created = service.users().drafts().create(
        userId="me", body={"message": {"raw": encoded}}
    ).execute()
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps({"status": "draft_created", "draft_id": created.get("id")}))]
    )


async def _send_email(to: str, subject: str, body: str) -> types.CallToolResult:
    if to.lower() in known_contacts():
        if MOCK:
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps({"status": "mock_sent", "to": to, "note": "known contact (auto-send)"}))]
            )
        return await _send_real(to, subject, body)

    approved = find_approved(to)
    if approved:
        if MOCK:
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps({"status": "mock_sent", "to": to, "approval": approved.name}))]
            )
        result = await _send_real(to, subject, body)
        log_action("send_email", to, "success")
        tracker = ROOT / ".claude" / "skills" / "approval-workflow" / "approval_tracker.py"
        if tracker.exists():
            import subprocess
            subprocess.run([sys.executable, str(tracker), "complete", approved.name], check=False)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result)]
        )

    PENDING.mkdir(exist_ok=True)
    filename = f"EMAIL_SEND_{re.sub(r'[^a-z0-9]+', '_', to.lower())}.md"
    path = PENDING / filename
    if not path.exists():
        path.write_text(f"""---
type: approval_request
action: send_email
target: {to}
subject: {subject}
created: {datetime.now(timezone.utc).isoformat()}
status: pending
---

# Send Email — Approval Required

- **To:** {to}
- **Subject:** {subject}

## Body
{body}

## To Approve
Move this file to `/Approved`, then ask me to send again.

## To Reject
Move this file to `/Rejected`.
""", encoding="utf-8")
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps({
            "status": "requires_approval",
            "message": f"Approval needed. File created: Pending_Approval/{filename}. Move it to Approved/ then call send_email again.",
        }))]
    )


async def _send_real(to: str, subject: str, body: str) -> str:
    from email.message import EmailMessage
    import base64
    service = get_service()
    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject
    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": encoded}).execute()
    log_action("send_email", to, "success")
    return json.dumps({"status": "sent", "to": to, "subject": subject})


# ---------- handler functions ----------

async def list_tools_handler(ctx, params) -> types.ListToolsResult:
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="search_email",
                description="Search the user's Gmail for emails matching a query (e.g. 'from:client is:unread').",
                inputSchema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="draft_email",
                description="Create a Gmail draft to `to` with `subject` and `body` (no sending).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["to", "subject", "body"],
                },
            ),
            types.Tool(
                name="send_email",
                description="Send an email to `to`. Requires human approval first: call this once to create a Pending_Approval file, the human moves it to Approved/, then call again to send. Replies to known contacts auto-send without approval.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["to", "subject", "body"],
                },
            ),
        ]
    )


async def call_tool_handler(ctx, params) -> types.CallToolResult:
    name = params.name
    args = params.arguments or {}

    if name == "search_email":
        return await _search_email(args["query"])
    elif name == "draft_email":
        return await _draft_email(args["to"], args["subject"], args["body"])
    elif name == "send_email":
        return await _send_email(args["to"], args["subject"], args["body"])
    else:
        raise ValueError(f"Unknown tool: {name}")


# ---------- main ----------

async def main():
    parser = argparse.ArgumentParser(description="Email MCP server")
    parser.add_argument("--mock", action="store_true", help="run without credentials (canned responses)")
    args = parser.parse_args()
    global MOCK
    MOCK = args.mock

    server = Server(
        "email-mcp",
        on_list_tools=list_tools_handler,
        on_call_tool=call_tool_handler,
    )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())