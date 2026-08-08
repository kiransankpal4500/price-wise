# Comparo Backend - Windows Task Scheduler Setup
# Run this script ONCE to register the backend as an auto-start task.

$TaskName    = "ComparoBackend"
$BackendDir  = "c:\Users\user\Desktop\price wise\backend"
$ScriptPath  = Join-Path $BackendDir "start_backend.bat"

# Remove existing task with same name
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task."
}

# Action: run the watchdog batch file
$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$ScriptPath`"" `
    -WorkingDirectory $BackendDir

# Trigger: run at logon
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Settings
$Settings = New-ScheduledTaskSettingsSet `
    -Hidden `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 9999 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

# Principal
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

# Register
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Comparo FastAPI backend watchdog - auto-starts at login and restarts on crash." `
    -Force

Write-Host ""
Write-Host "Task registered: $TaskName"
Write-Host "Starting backend now..."
Start-ScheduledTask -TaskName $TaskName
Write-Host "Backend started. Check http://localhost:8000 in a few seconds."
