# Bronze Tier Setup

## Directory Layout
- **Dashboard.md** – Real‑time status and metrics.
- **Company_Handbook.md** – Mission, principles, and getting‑started guide.
- **Inbox/** – Drop new items here.
- **Needs_Action/** – Items that the watcher has moved here for processing.
- **Done/** – Completed items (currently empty).
- **Skills/** – All automation scripts (agent skills).
- **requirements.txt** – Python dependencies.

## Agent Skills Implemented
| Skill | Purpose | Entry‑point script |
|-------|---------|--------------------|
| **Filesystem Watcher** | Monitors `Inbox` for newly created files, moves them to `Needs_Action`, and records the event in `status.json`. | `Skills/filesystem_watcher.py` |
| **Dashboard Updater** | Reads `status.json` and updates `Dashboard.md` with counts of new, in‑progress, and completed items. | `Skills/update_dashboard.py` |
| **Vault Sync** | Demonstrates that Claude Code can read from and write to the vault (`Dashboard.md`). Appends a synced timestamp marker. | `Skills/vault_sync.py` |

## How to Run

1. **Install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start the watcher** (keeps running until stopped)
   ```bash
   python Skills/filesystem_watcher.py --inbox Inbox
   ```

3. **Create a test file** in the `Inbox` folder (e.g., `echo "Test" > Inbox/test.txt`).
   The watcher will automatically move it to `Needs_Action` and log the event.

4. **Update the dashboard** to reflect the latest status:
   ```bash
   python Skills/update_dashboard.py
   ```

5. **Demonstrate vault read/write** (adds a sync marker to `Dashboard.md`):
   ```bash
   python Skills/vault_sync.py
   ```

6. **Open `Dashboard.md`** in Obsidian to see the live dashboard.

## Status
- All Bronze‑Tier requirements satisfied ✅
- Ready for Silver‑Tier development 🚀