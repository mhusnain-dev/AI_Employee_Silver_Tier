# AI Employee Vault — Silver Tier

Local-first Obsidian vault powering a Personal AI Employee (Claude Code +
Obsidian), built to the "Personal AI Employee Hackathon 0" Silver Tier brief.

## Directory-Layout

- **Dashboard.md** – Real-time status and metrics (auto-regenerated).
- **Company_Handbook.md** – Mission, principles, and getting-started guide.
- **Inbox/** – Drop new items here.
- **Needs_Action/** – Items the watcher has moved here for processing.
- **Done/** – Completed items.
- **Plans/** – Reasoning artifacts: `PLAN_*.md` with checkbox steps.
- **Pending_Approval/** – Sensitive actions awaiting human approval.
- **Approved/** – Approved actions ready to execute.
- **Rejected/** – Declined actions.
- **Logs/** – Audit trail (`YYYY-MM-DD.json`).
- **.claude/skills/** – Agent Skills (all AI functionality).
- **mcp-servers/** – Custom MCP servers (e.g., email).

## Agent Skills

| Skill | Entry-point script | Purpose |
|-------|--------------------|---------|
| `filesystem-watcher` | `.claude/skills/filesystem-watcher/filesystem_watcher.py` | Watch `Inbox/`, move new files to `Needs_Action/`, log to `status.json`. |
| `dashboard-updater` | `.claude/skills/dashboard-updater/update_dashboard.py` | Regenerate `Dashboard.md` from current folder state + `status.json`. |
| `vault-sync` | `.claude/skills/vault-sync/vault_sync.py` | Prove vault read/write by appending a sync marker to `Dashboard.md`. |
| `gmail-watcher` | `.claude/skills/gmail-watcher/gmail_watcher.py` | Poll Gmail for unread/important emails → `Needs_Action/EMAIL_*.md`. `--mock` for testing. |
| `plan-creator` | `.claude/skills/plan-creator/plan_template.py` | Create `Plans/PLAN_*.md` with checkbox steps from `Needs_Action/` items. |
| `approval-workflow` | `.claude/skills/approval-workflow/approval_tracker.py` | Manage `Pending_Approval/` → `Approved/`/`Rejected/` → log to `Logs/`. |
| `linkedin-poster` | `.claude/skills/linkedin-poster/create_post.py` / `publish_post.py` | Draft LinkedIn posts to `Pending_Approval/`, approve → ready-to-post artifact. |
| `scheduler` | `.claude/skills/scheduler/scheduler.py` | Run watchers + dashboard on interval; cron & Windows Task Scheduler examples. |

## Email MCP Server

Custom Python MCP server (stdio) exposing Gmail tools to Claude Code:
- `search_email(query)` — find emails
- `draft_email(to, subject, body)` — create Gmail draft
- `send_email(to, subject, body)` — send only after approval (or known-contact auto-send)

Registered via `.mcp.json`. Run `authenticate.py` once to create `token.json`.

## How to Run

1. **Install dependencies**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows   |   source .venv/bin/activate   # macOS/Linux
   pip install -r requirements.txt
   ```

2. **Authenticate Gmail (once, for watcher + MCP)**

   ```bash
   # Place credentials.json in vault root first
   python .claude/skills/gmail-watcher/authenticate.py
   ```

3. **Run the scheduler (one-shot or continuous)**

   ```bash
   # One-shot: run watchers + dashboard
   python .claude/skills/scheduler/scheduler.py --once

   # Continuous: every 5 minutes
   python .claude/skills/scheduler/scheduler.py --interval 300
   ```

   Or use cron / Windows Task Scheduler (see `.claude/skills/scheduler/crontab.example` and `task-scheduler.ps1`).

4. **Process items** — when `Needs_Action/` has items, use `plan-creator` to create `Plans/PLAN_*.md`, execute steps, route sensitive actions to `Pending_Approval/`, wait for approval, then execute.

5. **Refresh dashboard**

   ```bash
   python .claude/skills/dashboard-updater/update_dashboard.py
   ```

6. **Open `Dashboard.md`** in Obsidian to see the live dashboard.

## Testing Without Credentials

Most skills support `--mock` or `--dry-run`:

```bash
# Gmail watcher (sample emails)
python .claude/skills/gmail-watcher/gmail_watcher.py --mock --once

# Email MCP server (canned responses)
python mcp-servers/email_mcp/server.py --mock

# Scheduler one-shot
python .claude/skills/scheduler/scheduler.py --once
```

## Status

- **Bronze Tier: complete** ✅
  - Obsidian vault with `Dashboard.md` + `Company_Handbook.md`
  - Working filesystem watcher
  - Claude Code read/write capability
  - `Inbox/`, `Needs_Action/`, `Done/` folder structure
  - All AI functionality as Agent Skills

- **Silver Tier: complete** ✅
  - Two+ watchers: filesystem + Gmail (with `--mock` mode)
  - LinkedIn auto-post: draft → approval → ready-to-post artifact (safe mode)
  - Plan.md creation loop: `plan-creator` skill + documented operating loop
  - One working MCP server: custom Python email MCP (search/draft/send + approval gating)
  - HITL approval workflow: `Pending_Approval/` → `Approved/`/`Rejected/` → log to `Logs/`
  - Scheduling: `scheduler` skill + Linux cron & Windows Task Scheduler examples
  - All AI functionality as Agent Skills

## Security

- Credentials and runtime state never live in the vault: `.env`,
  `credentials.json`, `token.json`, `status.json`, `*.cache.json`,
  `known_contacts.json` are gitignored.
- Sensitive external actions require human approval (per hackathon brief,
  Section 6).
- Permission boundary (doc §6.4): replies to known contacts auto-send; new
  contacts, bulk sends, payments always require approval.
