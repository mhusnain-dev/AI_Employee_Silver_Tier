---
name: scheduler
description: Run watchers (filesystem + Gmail) and dashboard updater on a schedule. Supports one-shot (--once) or repeated intervals (--interval). Provides Linux cron and Windows Task Scheduler examples. Use to automate the AI Employee's perception and dashboard refresh cycles.
---

# Scheduler (Agent Skill)

Automates the AI Employee's continuous operation (hackathon doc §3 Continuous vs Scheduled Operations).

## What it does

- Runs `filesystem-watcher` (and `gmail-watcher` if `credentials.json` exists) to populate `Needs_Action/`.
- Runs `dashboard-updater` to regenerate `Dashboard.md` with current counts.
- Can run once (`--once`) or on a recurring interval (`--interval SECONDS`).

## Usage

```bash
# One-shot: run watchers + dashboard once (good for testing or cron)
python .claude/skills/scheduler/scheduler.py --once

# Continuous: run every 5 minutes (300s)
python .claude/skills/scheduler/scheduler.py --interval 300

# Watchers only (no dashboard)
python .claude/skills/scheduler/scheduler.py --interval 60 --watchers-only

# Dashboard only
python .claude/skills/scheduler/scheduler.py --dashboard-only
```

## Linux cron (verified)

Edit your crontab (`crontab -e`) and add:

```cron
# Every 5 minutes: run watchers + dashboard
*/5 * * * * /home/you/ai-employee-vault/.venv/bin/python /home/you/ai-employee-vault/.claude/skills/scheduler/scheduler.py --once >> /home/you/ai-employee-vault/Logs/scheduler.log 2>&1

# Daily briefing at 8:00 AM (doc §3)
0 8 * * * /home/you/ai-employee-vault/.venv/bin/python /home/you/ai-employee-vault/.claude/skills/scheduler/scheduler.py --once >> /home/you/ai-employee-vault/Logs/scheduler.log 2>&1
```

Replace `/home/you/ai-employee-vault` with your actual vault path.

## Windows Task Scheduler (example)

Save as `task-scheduler.ps1` and run in PowerShell as Administrator, or create tasks manually:

```powershell
# 1. Create the task action
$action = New-ScheduledTaskAction -Execute "python.exe" `
  -Argument ".claude/skills/scheduler/scheduler.py --once" `
  -WorkingDirectory "C:\path\to\ai-employee-vault"

# 2. Create a trigger (every 5 minutes)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)

# 3. Register
Register-ScheduledTask -TaskName "AIEmployee_Scheduler" -Action $action -Trigger $trigger -User "SYSTEM" -RunLevel Highest
```

Or use Task Scheduler GUI:
- Action: Start a Program → `python.exe`
- Arguments: `.claude/skills/scheduler/scheduler.py --once`
- Start in: `C:\path\to\ai-employee-vault`
- Trigger: Daily, repeat every 5 minutes indefinitely.

## For Claude Code

The scheduler is typically run externally (cron/Task Scheduler). Claude Code can invoke it for one-shot operations:

```
/goal Run the scheduler once to process any new items in Inbox and update the dashboard.
```

Then Claude will run the scheduler skill with `--once`, process any `Needs_Action/` items via `plan-creator`, and refresh `Dashboard.md`.