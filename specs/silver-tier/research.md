# Silver Tier — Research Findings

**System of record:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
**Source:** hackathon doc §"Silver Tier: Functional Assistant" (estimated 20–30 hrs)

## Silver Tier requirements (verbatim from the doc)

1. All Bronze requirements plus:
2. Two or more Watcher scripts (e.g., Gmail + WhatsApp + LinkedIn)
3. Automatically Post on LinkedIn about business to generate sales
4. Claude reasoning loop that creates `Plan.md` files
5. One working MCP server for external action (e.g., sending emails)
6. Human-in-the-loop approval workflow for sensitive actions
7. Basic scheduling via cron or Task Scheduler
8. All AI functionality should be implemented as Agent Skills

## Current state (Bronze, committed `e499da2`)

- Vault with `Dashboard.md`, `Company_Handbook.md`; folders `Inbox/`, `Needs_Action/`, `Done/`.
- 3 Agent Skills in `.claude/skills/`: `filesystem-watcher`, `dashboard-updater`, `vault-sync`.
- Python 3, `watchdog` only dependency. Repo remote: `mhusnain-dev/ai-employee-vault`.

## Research summary by area

### A. Gmail watcher (2nd watcher)
- Standard approach: Gmail API + OAuth2 (`google-api-python-client`, `google-auth-oauthlib`).
  `credentials.json` = client config; `token.json` = access token (**never commit**).
- Query pattern `is:unread is:important` (hackathon doc §"Gmail Watcher Implementation").
- Poll loop every ~120 s; create `Needs_Action/EMAIL_<id>.md` with YAML frontmatter
  (type/from/subject/received/priority/status) + snippet + suggested actions.
- Dedupe by tracking processed message IDs in a local cache file (e.g. `.gmail_cache.json`,
  gitignored) so re-polls don't duplicate action files.
- Reference implementations exist from other Hackathon 0 participants (e.g.
  `ucdexpert/hackathon0-FTE`, `akbarfarooq2006/Hackathon0_Digital_FTE`): pattern is
  `gmail_watcher.py` daemon + `authenticate.py` one-time OAuth helper.
- Live testing needs real Gmail OAuth credentials → verify with mock/dry-run where absent.

### B. LinkedIn auto-posting
- **Official LinkedIn API**: publishing endpoints only for approved enterprise partners;
  no self-service posting API. Native scheduler is manual.
- **Browser automation (Playwright)** is what the hackathon doc recommends (Playwright =
  "Computer Use"), but 2026 research: LinkedIn actively detects headless/automated browsers;
  ~40% of accounts using non-compliant automation saw restrictions in Q1 2026.
- Risk mitigation that fits the hackathon HITL requirement: draft the post → require human
  approval via `Pending_Approval/` → post only after approval, at human pace, low volume,
  on the user's own real logged-in session.
- Decision needed from user: real Playwright poster vs. approval-gated "post scheduler"
  that outputs the final ready-to-paste post (safe demo without account risk).

### C. MCP server for external action (sending email)
- Ecosystem: many Gmail MCP servers exist (`GongRzhe/Gmail-MCP-Server` ~1.2k★, `theposch/gmail-mcp`,
  official Google Gmail MCP). Options: (1) build our own small Python MCP server using Gmail
  API/SMTP, (2) wrap an existing npm server.
- Hackathon intent = build "The Hands (MCP)". Custom Python MCP server is most aligned and
  easiest to keep local + audit.
- MCP servers integrate with Claude Code via `.mcp.json` (project) or `~/.claude.json`.
  stdio transport, `send_email` / `draft_email` / `search_email` tools.
- Sending is a sensitive action → must sit behind the HITL approval workflow (doc §"Permission
  Boundaries": email to known contacts auto-ok, new contacts/bulk require approval).

### D. Claude reasoning loop → Plan.md files
- Doc: "Claude reasoning loop that creates Plan.md files" + §B Reasoning (Read → Think → Plan).
  Deliverable file format per doc §"End-to-End Invoice Flow": `/Plans/PLAN_<task>.md` with
  frontmatter (created, status) and checkbox steps.
- Ralph Wiggum (Stop-hook loop) is a **Gold** tier item; for Silver the requirement is the
  plan-creation loop itself, i.e. Claude processing `Needs_Action/` → writes `Plans/PLAN_*.md`
  → executes → updates → moves items to `Done/`.
- Implementable as a `plan-creator` skill + documented operating loop (doc §"How to Run").
  Claude Code 2.1 also ships `/goal` and `/loop` as lighter alternatives for the loop.

### E. HITL approval workflow
- Doc §"Human-in-the-Loop Pattern": Claude writes `Pending_Approval/<ACTION>_<target>.md`
  (frontmatter: type, action, target, reason, created, status) → human moves to `Approved/` or
  `Rejected/` → orchestrator triggers the MCP action, logs to `Logs/`.
- Add `Pending_Approval/`, `Approved/`, `Rejected/` folders + an `approval-workflow` skill.

### F. Scheduling (cron / Task Scheduler)
- This machine is Linux → cron. Ship `scheduler.py` (loop with interval + due-time checks) and
  a `crontab.example` running watchers + dashboard updater at defined intervals (doc §3
  Continuous vs Scheduled Operations: daily briefing 8:00 AM, continuous lead capture, etc.).

### G. Folders & files added for Silver (aligns with doc + Platinum layout)
`Plans/`, `Pending_Approval/`, `Approved/`, `Rejected/`, `Logs/`.

## Open questions / ambiguities (for Phase 3 interview)
1. Second watcher choice: Gmail (recommended) — confirm. WhatsApp would need Playwright + ToS risk.
2. LinkedIn: real browser poster (approval-gated) vs safe "draft → approval → ready post" without
   account risk?
3. Gmail credentials available for live testing, or build + dry-run/mock verification?
4. Email MCP: custom Python server (recommended) vs wrapping existing npm server?
5. Scheduling target: this Linux machine (cron) — confirm.
6. Scope of "Claude reasoning loop": implement as `plan-creator` skill + `/goal` operating loop
   (Ralph plugin itself is Gold tier).
