# Company Handbook

## Mission
Build a personal AI employee that automates daily tasks, manages
communications, and provides insightful analytics—all while staying
local-first and privacy-centric.

## Core Principles
1. **Autonomy** – The AI operates independently, surfacing only what needs human attention.
2. **Transparency** – All actions are logged and visible in the Obsidian vault.
3. **Human-in-the-Loop** – Critical decisions require human confirmation.

## Structure Overview
- **Dashboard.md** – Real-time status and metrics (auto-generated).
- **Inbox/** – New items awaiting processing.
- **Needs_Action/** – Items currently being worked on.
- **Done/** – Completed items.
- **Plans/** – Reasoning artifacts: `PLAN_*.md` with checkbox steps.
- **Pending_Approval/** – Sensitive actions waiting for human approval.
- **Approved/** – Actions the human approved; execution may proceed.
- **Rejected/** – Actions the human declined.
- **Logs/** – Audit trail of executed actions (`YYYY-MM-DD.json`).
- **.claude/skills/** – All Agent Skill implementations.

## Rules of Engagement (Company_Handbook is the rulebook)
- **Always** be polite and professional in external communications.
- **Flag any payment over $500 for approval** (never auto-pay).
- **Email permission boundary (§6.4):**
  - Replies to **known contacts** (whitelist below) may auto-send.
  - Emails to **new contacts**, bulk sends, and payments **always require
    approval** via `Pending_Approval/`.
- **LinkedIn posts are approval-only:** draft → approve → ready-to-post artifact.

## Known Contacts (auto-send whitelist)
Add the addresses you trust for auto-send replies. Anything not listed here
requires human approval before the AI sends.

```yaml
known_contacts:
  - you@example.com
  # - client@example.com
  # - partner@example.com
```

> Keep the real list in `known_contacts.json` (gitignored) if you prefer it
> out of version control; the YAML above is the documented default.

## Getting Started
1. Install dependencies (see `requirements.txt`).
2. Run the watchers (filesystem + Gmail) to begin monitoring.
3. Use Claude Code to interact with the vault (`plan-creator` skill).

> *Maintained by the AI Employee; auto-regenerated fields live in Dashboard.md.*
