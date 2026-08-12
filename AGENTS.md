# AGENTS.md — Project Constitution

This vault is a Personal AI Employee ("Digital FTE") built to the
`Personal AI Employee Hackathon 0` brief. Claude Code is the reasoning engine;
Obsidian (local markdown) is the memory/dashboard. This file is the
constitution: principles and constraints that guide every spec and build.

## Principles

- **Local-first and privacy-centric.** Sensitive data stays on this machine.
  Never send secrets, credentials, or raw personal data out unless required
  by a documented integration.
- **Human-in-the-loop for sensitive actions.** Payments, sending email to new
  contacts, and posting to social media require human approval via the
  `Pending_Approval/` → `Approved/` (or `Rejected/`) workflow before execution.
- **All AI functionality ships as Agent Skills.** Each skill lives in
  `.claude/skills/<name>/` with a `SKILL.md` (name + description frontmatter)
  plus its supporting script(s). No loose AI logic outside skills.
- **The spec is the source of truth.** Every feature ships with its spec in
  `specs/<feature>/`. Update the spec in the same commit as the code it describes.
- **Plain language over cleverness.** A new contributor should understand any
  file in five minutes.

## Constraints

- **Stack:** Python 3 for skills and watchers; Markdown-only vault; MCP for
  external actions. Propose (don't assume) any new dependency.
- **Never commit secrets or runtime state:** `credentials.json`, `token.json`,
  `.env`, `*.cache.json`, `status.json`, `.venv/`. Keep them gitignored.
- **Vault sync never includes secrets.** Only markdown/state are tracked.
- **No destructive external actions without approval** (payments, sends, posts).

## Definition of done

- Behaviour matches the spec, edge cases included.
- Each skill has a `SKILL.md` and runs from a clean checkout.
- Verification (demo run / test) shown against the spec's acceptance criteria.
- A human has reviewed the diff against the spec before merge/push.

## Operating rules for this vault

- `Inbox/` → new items; `Needs_Action/` → being processed; `Done/` → complete.
- `Plans/` → `PLAN_*.md` reasoning artifacts; `Pending_Approval/`/`Approved/`/
  `Rejected/` → HITL; `Logs/` → action audit trail.
- Always regenerate `Dashboard.md` via the `dashboard-updater` skill rather than
  hand-editing it.
