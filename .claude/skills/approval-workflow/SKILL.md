---
name: approval-workflow
description: Manage the Human-in-the-Loop approval workflow for sensitive actions (payments, sending email to new contacts, LinkedIn posts). Create Pending_Approval files, detect when the human moves them to Approved/ or Rejected/, execute or cancel, and log every action to Logs/. Use whenever a sensitive external action needs human confirmation.
---

# Approval Workflow (Agent Skill)

The AI Employee's safety gate (hackathon doc §"Human-in-the-Loop Pattern").
Sensitive actions never execute directly — they are written as approval files
that a human approves or rejects by moving the file.

## Folder contract

- `Pending_Approval/` — action is waiting for a human decision.
- `Approved/` — human moved the file here → the action may execute.
- `Rejected/` — human moved the file here → the action is cancelled.
- `Done/` — archived approval files after execution/cancellation.
- `Logs/YYYY-MM-DD.json` — audit trail of every executed/cancelled action.

## When to create an approval file

Create `Pending_Approval/<ACTION>_<target>.md` whenever the action is
sensitive: payments, sending email to a **new** contact, bulk sends, LinkedIn
posts, anything irreversible. Known-contact replies auto-send (no approval).

Approval file format:

```markdown
---
type: approval_request
action: send_email        # e.g. payment, send_email, linkedin_post
target: client@example.com
amount: 0                 # set for payments
reason: Why this needs to happen
created: 2026-01-07T10:30:00Z
status: pending
---

# Action Details
- What: <what will happen>
- To: <target>
- Reference: <any ids>

# To Approve
Move this file to `/Approved`.

# To Reject
Move this file to `/Rejected`.
```

## How to use

1. **Check what needs attention** — when you create or detect an approval
   file, tell the human where it is.
2. **Detect a decision** — when a file has moved to `Approved/` or
   `Rejected/`, act accordingly:
   - `Approved/` → execute the action (via the right MCP tool / skill), then:
     ```bash
     python .claude/skills/approval-workflow/approval_tracker.py complete <file>
     ```
   - `Rejected/` → do nothing external, then:
     ```bash
     python .claude/skills/approval-workflow/approval_tracker.py cancel <file>
     ```
3. **Inspect state** at any time:
   ```bash
   python .claude/skills/approval-workflow/approval_tracker.py status
   python .claude/skills/approval-workflow/approval_tracker.py list pending
   ```

## Rules

- Never execute an action that is still in `Pending_Approval/`.
- Never execute an action that was rejected.
- Always log the outcome (the tracker does this).
- If an approval has been pending a long time, surface it on the dashboard.
