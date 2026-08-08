# Comparo Backend Watchdog
# Runs uvicorn in an infinite loop. Restarts the backend automatically if it exits.
# Runs silently in the background. Logs to backend_watchdog.log.

$BackendDir = "c:\Users\user\Desktop\price wise\backend"
$Python     = "C:\Users\user\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe"
$LogFile    = Join-Path $BackendDir "backend_watchdog.log"
$RestartDelay = 10  # seconds to wait before restarting after a crash

Set-Location $BackendDir

function Write-Log($msg) {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$ts] $msg"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

Write-Log "=== Comparo Watchdog Started ==="

while ($true) {
    Write-Log "Starting backend (uvicorn)..."

    $proc = Start-Process -FilePath $Python `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" `
        -WorkingDirectory $BackendDir `
        -NoNewWindow `
        -PassThru `
        -RedirectStandardOutput "$BackendDir\backend_stdout.log" `
        -RedirectStandardError  "$BackendDir\backend_stderr.log"

    Write-Log "Backend running as PID $($proc.Id)"

    # Wait for the process to exit
    $proc.WaitForExit()
    $exitCode = $proc.ExitCode

    Write-Log "Backend exited with code $exitCode. Restarting in $RestartDelay seconds..."
    Start-Sleep -Seconds $RestartDelay
}
