# Silver Tier — Technical Plan

**Spec:** `specs/silver-tier/spec.md` (agreed) — **Constitution:** `AGENTS.md`

## Stack

- Python 3.10+ (already used). Markdown vault unchanged.
- New dependencies (proposed, documented in `requirements.txt`):
  - `google-api-python-client`, `google-auth-oauthlib` — Gmail watcher + email MCP (Gmail API, OAuth2).
  - `mcp` — official Python SDK for the custom email MCP server (FastMCP/stdio).
  - Keep `watchdog` (filesystem watcher).
- Claude Code project MCP config: `.mcp.json` at repo root (committed; secrets stay in gitignored `.env`/`token.json`).

## What gets built (each item is an Agent Skill unless noted)

| # | Deliverable | Path | Satisfies |
|---|-------------|------|-----------|
| 1 | **Gmail watcher** skill | `.claude/skills/gmail-watcher/` (`SKILL.md`, `gmail_watcher.py` poller, `authenticate.py` OAuth helper) | FR1 (2nd watcher) |
| 2 | **LinkedIn poster** skill | `.claude/skills/linkedin-poster/` (`create_post.py` → `Pending_Approval/LINKEDIN_*.md`; `publish_post.py` → ready-to-post artifact after approval) | FR2 |
| 3 | **Plan creator** skill | `.claude/skills/plan-creator/` (`SKILL.md` + `plan_template.py`; documented daily loop) | FR3 |
| 4 | **Email MCP server** (custom Python) | `mcp-servers/email_mcp/server.py`, registered in `.mcp.json`; tools `search_email`, `draft_email`, `send_email` | FR4 |
| 5 | **Approval workflow** skill | `.claude/skills/approval-workflow/` (`SKILL.md` + `approval_tracker.py`) | FR5 |
| 6 | **Scheduler** skill + examples | `.claude/skills/scheduler/` (`scheduler.py`, `crontab.example`, `task-scheduler.ps1`) | FR6 |
| 7 | **Dashboard updater** extension | extend existing skill to count plans, pending approvals, recent events | FR8 |
| 8 | Vault folders | `Plans/`, `Pending_Approval/`, `Approved/`, `Rejected/`, `Logs/` | FR5/FR3 |
| 9 | Docs & hygiene | `Company_Handbook.md` known-contacts whitelist, `requirements.txt`, `.gitignore`, `CLAUDE.md` update | FR5/FR7 |

## Key decisions & trade-offs

1. **Gmail watcher: OAuth2 + polling** (query `is:unread is:important`). Poll every 120 s (doc's own pattern). Dedupe via `.gmail_cache.json` (gitignored). **`--mock` mode** generates sample emails so everything is verifiable before you add real credentials.
2. **Email MCP: custom Python server** using the official `mcp` SDK (stdio). `send_email` checks `Approved/` for a matching approval file, or auto-sends to whitelisted known contacts (§6.4). **`--mock` mode** lets tools return canned results without creds.
3. **LinkedIn: no live posting** (agreed). `create_post.py` drafts from `Business_Goals.md`/request; `publish_post.py` turns an `Approved/` file into a final ready-to-post artifact in `Done/` + logs it. Zero account risk.
4. **Plan loop: skill + documented procedure**, not the Ralph plugin (Gold). `plan-creator` instructs Claude: read `Needs_Action/` → `Plans/PLAN_*.md` → execute → move to `Done/`.
5. **Scheduling: `scheduler.py`** (interval loop) + `crontab.example` + `task-scheduler.ps1`. Verified on Linux via cron.
6. **Approval:** every sensitive action lands in `Pending_Approval/`; execution is triggered by file movement to `Approved/` (or cancelled on `Rejected/`); all actions logged to `Logs/YYYY-MM-DD.json`.

## Build order (small, checkable steps)

1. Vault folders + `.gitignore`/`requirements.txt`/`Company_Handbook.md` updates.
2. `approval-workflow` skill (foundation for everything sensitive).
3. `plan-creator` skill.
4. Gmail watcher skill (+ `--mock` verification).
5. LinkedIn poster skill (draft → approval → artifact).
6. Email MCP server + `.mcp.json` (+ `--mock` verification).
7. Scheduler skill + cron/Windows examples (Linux verified).
8. Dashboard updater extension (FR8).
9. `CLAUDE.md` + README update; full end-to-end demo; commit; then ask to push.

## Out of scope
WhatsApp, Facebook/Instagram/Twitter, Odoo, cloud deploy, Ralph plugin, live LinkedIn posting, real payments (all per spec).
