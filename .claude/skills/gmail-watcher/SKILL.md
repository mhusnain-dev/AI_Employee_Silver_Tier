---
name: gmail-watcher
description: Monitor Gmail for new unread/important emails and create Needs_Action/EMAIL_*.md action files for the AI Employee to process. Uses the Gmail API (OAuth2) with keyword filtering and duplicate protection. Includes a --mock mode for testing without credentials. Use whenever email monitoring is needed.
---

# Gmail Watcher (Agent Skill)

The AI Employee's second sense (Bronze had filesystem). Polls Gmail for
unread/important messages matching business keywords and turns each into a
`Needs_Action/EMAIL_<id>.md` action file.

## Setup (once)

1. Enable the **Gmail API** and create an OAuth client (Desktop app) at
   https://console.cloud.google.com/apis/credentials
2. Save the client JSON as `credentials.json` in the vault root (gitignored).
3. Authenticate once:
   ```bash
   python .claude/skills/gmail-watcher/authenticate.py
   ```
   This opens a browser and writes `token.json` (gitignored).

## Run

```bash
# Poll forever every 120s (default)
python .claude/skills/gmail-watcher/gmail_watcher.py

# Custom interval
python .claude/skills/gmail-watcher/gmail_watcher.py --interval 60

# Verification without credentials (sample emails)
python .claude/skills/gmail-watcher/gmail_watcher.py --mock --once
```

## What it creates

`Needs_Action/EMAIL_<gmail_id>.md`:

```markdown
---
type: email
from: client@example.com
subject: Urgent: Invoice request for January
received: <iso timestamp>
priority: high
status: pending
gmail_id: <id>
---

## Email Content
...

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Behaviour

- Query: `is:unread is:important`; emails must also match a business keyword
  (`urgent`, `invoice`, `payment`, `help`, `pricing`, …).
- Priority: `high` if subject contains urgent/asap/emergency or
  invoice/payment/billing; else `normal`.
- **No duplicates:** processed message IDs are kept in `.gmail_cache.json`
  (gitignored). Re-polls never recreate an action file.
- API errors, expired tokens, or missing credentials are logged; the watcher
  keeps running and never deletes existing files.
- `--dry-run` logs intended files without writing.

## Troubleshooting

- "credentials.json not found" → download it and place in vault root.
- "401/token expired" → re-run `authenticate.py`.
- Not seeing emails → broaden `KEYWORDS` or the query in the script.
