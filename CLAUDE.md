# Bronze → Silver Transition Plan

## Goal
Implement Silver‑Tier features building on the Bronze foundation: real‑time Gmail integration, richer dashboard metrics, automated scheduling, unit tests, etc.

## Completed Bronze Milestones
- ✅ Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- ✅ Working filesystem watcher that moves files from `Inbox` → `Needs_Action` and logs to `status.json`
- ✅ Claude Code can read/write the vault (`vault_sync.py`)
- ✅ Basic folder structure (`Inbox/`, `Needs_Action/`, `Done/`)
- ✅ All AI functionality packaged as agent skills in `Skills/`
- ✅ Git commit initialized (`bronze-setup`) with proper documentation

## Next Steps (Silver Tier)
1. **Gmail OAuth Setup**
   - Add `credentials.json` in `watchers/gmail/`.
   - Install `google-api-python-client` in `requirements.txt`.
   - Extend `filesystem_watcher.py` (or create `email_watcher.py`) to poll Gmail API for new messages.
   - Parse relevant fields (subject, sender, body) and store in `status.json` or a dedicated `email.json`.

2. **Enhanced Dashboard**
   - Update `update_dashboard.py` to aggregate email data and compute additional metrics (e.g., email volume, response time).
   - Add visual indicators (markdown tables or simple ASCII charts).
   - Persist historical data in `vault/metrics.json`.

3. **Scheduler / Cron**
   - Create a lightweight scheduler script (`scripts/scheduler.py`) that runs the watcher and dashboard updater at defined intervals.
   - Optionally integrate with Windows Task Scheduler or `cron` via WSL.

4. **Unit Tests**
   - Add `tests/` directory with `pytest` tests for each skill.
   - Mock API calls to ensure deterministic behavior.

5. **Documentation & Versioning**
   - Update `README.md` with Silver‑Tier setup instructions.
   - Tag the release as `silver-v1` and push.

6. **Optional Enhancements**
   - Add Slack/Discord notifications for high‑priority items.
   - Implement natural‑language summarisation using Claude Code’s RL‑hf capabilities.
   - Build a simple UI component in Obsidian (e.g., daily note template) that auto‑populates from the dashboard.

## Reference Files
- `AI_Employee_Vault/` – repository root.
- `Skills/` – all agent scripts.
- `Task #2` – Bronze Tier: Initialize Vault Structure (completed).
- `CLAUDE.md` – this file.

## Success Criteria
- Silver‑Tier scripts run without errors and produce updated `Dashboard.md`.
- All new unit tests pass.
- Documentation reflects the extended architecture and usage instructions.