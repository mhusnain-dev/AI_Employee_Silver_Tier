# AI Employee Vault — Bronze Tier

Local-first Obsidian vault powering a Personal AI Employee (Claude Code +
Obsidian), built to the "Personal AI Employee Hackathon 0" Bronze Tier brief.

## Directory Layout

- **Dashboard.md** – Real-time status and metrics (auto-regenerated).
- **Company_Handbook.md** – Mission, principles, and getting-started guide.
- **Inbox/** – Drop new items here.
- **Needs_Action/** – Items the watcher has moved here for processing.
- **Done/** – Completed items.
- **.claude/skills/** – Agent Skills (all AI functionality).

## Agent Skills

| Skill | Entry-point script | Purpose |
|-------|--------------------|---------|
| `filesystem-watcher` | `.claude/skills/filesystem-watcher/filesystem_watcher.py` | Watch `Inbox/`, move new files to `Needs_Action/`, log to `status.json`. |
| `dashboard-updater` | `.claude/skills/dashboard-updater/update_dashboard.py` | Regenerate `Dashboard.md` from current folder state + `status.json`. |
| `vault-sync` | `.claude/skills/vault-sync/vault_sync.py` | Prove vault read/write by appending a sync marker to `Dashboard.md`. |

## How to Run

1. **Install dependencies**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows   |   source .venv/bin/activate   # macOS/Linux
   pip install -r requirements.txt
   ```

2. **Start the watcher** (keeps running until stopped)

   ```bash
   python .claude/skills/filesystem-watcher/filesystem_watcher.py
   ```

3. **Create a test file** in `Inbox/` (e.g., `echo "Test" > Inbox/test.txt`).
   The watcher moves it to `Needs_Action/` and logs the event to `status.json`.

4. **Update the dashboard**

   ```bash
   python .claude/skills/dashboard-updater/update_dashboard.py
   ```

5. **Demonstrate vault read/write** (adds a sync marker to `Dashboard.md`)

   ```bash
   python .claude/skills/vault-sync/vault_sync.py
   ```

6. **Open `Dashboard.md`** in Obsidian to see the live dashboard.

## Status

- Bronze Tier: **complete** ✅ (all 5 requirements met)
  - Obsidian vault with `Dashboard.md` + `Company_Handbook.md`
  - Working filesystem watcher (Gmail can come at Silver Tier)
  - Claude Code read/write capability
  - `Inbox/`, `Needs_Action/`, `Done/` folder structure
  - All AI functionality as Agent Skills (`.claude/skills/`)
- Ready for Silver Tier: Gmail watcher, Plan.md files, MCP server, HITL
  approvals, scheduling.

## Security

- Credentials and runtime state never live in the vault: `.env`,
  `credentials.json`, `status.json` are gitignored.
- Sensitive external actions require human approval (per hackathon brief,
  Section 6).
