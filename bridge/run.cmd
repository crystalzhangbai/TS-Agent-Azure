@echo off
setlocal
set SCRIPT_DIR=%~dp0
echo [info] Running popup preflight-check before launch (use -SkipPreflight to bypass)
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run.ps1" %*
endlocal
pause