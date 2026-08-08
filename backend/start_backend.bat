 @echo off
:: Comparo Backend — Auto-restart watchdog
:: Starts the FastAPI backend and automatically restarts it if it crashes.
:: Restart delay: 10 seconds between each restart attempt.

set "PYTHON=C:\Users\user\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe"
set "BACKEND_DIR=c:\Users\user\Desktop\price wise\backend"
set "RESTART_DELAY=10"
set "LOG_FILE=%BACKEND_DIR%\backend_watchdog.log"

cd /d "%BACKEND_DIR%"

echo. >> "%LOG_FILE%"
echo =============================== >> "%LOG_FILE%"
echo Watchdog started: %DATE% %TIME% >> "%LOG_FILE%"
echo =============================== >> "%LOG_FILE%"

:LOOP
echo [%DATE% %TIME%] Starting Comparo backend... >> "%LOG_FILE%"
echo [%DATE% %TIME%] Starting Comparo backend...

"%PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 >> "%LOG_FILE%" 2>&1

echo [%DATE% %TIME%] Backend stopped. Restarting in %RESTART_DELAY% sec... >> "%LOG_FILE%"
echo [%DATE% %TIME%] Backend stopped. Restarting in %RESTART_DELAY% seconds...

timeout /t %RESTART_DELAY% /nobreak >nul

goto LOOP
