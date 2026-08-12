<#
.SYNOPSIS
    Register AI Employee Scheduler as a Windows Scheduled Task.

.DESCRIPTION
    Creates a task that runs the scheduler every 5 minutes (repeating).
    Run this script in PowerShell as Administrator.

.NOTES
    Adjust VAULT_PATH to your actual vault location.
    Requires Python in PATH and .venv activated, or use full python path.
#>

$VAULT_PATH = "C:\path\to\ai-employee-vault"
$PYTHON = "$VAULT_PATH\.venv\Scripts\python.exe"
$SCHEDULER = "$VAULT_PATH\.claude\skills\scheduler\scheduler.py"
$LOG = "$VAULT_PATH\Logs\scheduler.log"

# Verify paths
if (-not (Test-Path $PYTHON)) {
    Write-Error "Python not found at $PYTHON. Activate venv or fix path."
    exit 1
}
if (-not (Test-Path $SCHEDULER)) {
    Write-Error "Scheduler not found at $SCHEDULER."
    exit 1
}

# Action: run scheduler once
$action = New-ScheduledTaskAction `
    -Execute $PYTHON `
    -Argument "`"$SCHEDULER`" --once" `
    -WorkingDirectory $VAULT_PATH

# Trigger: start now, repeat every 5 minutes indefinitely
$trigger = New-ScheduledTaskTrigger `
    -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

# Settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Principal: run as SYSTEM (or current user with -User $env:USERNAME)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register
$taskName = "AIEmployee_Scheduler"
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Write-Host "Task $taskName exists. Updating..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Runs AI Employee watchers and dashboard updater every 5 minutes."

Write-Host "Registered $taskName. It will run every 5 minutes."

# Optional: also create daily briefing at 8 AM
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At "08:00"
$dailyTaskName = "AIEmployee_DailyBriefing"
if (Get-ScheduledTask -TaskName $dailyTaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $dailyTaskName -Confirm:$false
}
Register-ScheduledTask `
    -TaskName $dailyTaskName `
    -Action $action `
    -Trigger $dailyTrigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Runs AI Employee daily briefing at 8:00 AM."

Write-Host "Registered $dailyTaskName for 8:00 AM daily."