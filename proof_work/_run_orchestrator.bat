@echo off
chcp 65001 >nul 2>&1
title Rigorous Proof Orchestrator
echo Starting orchestrator at %date% %time%
echo Working directory: "C:\Users\wjzhong\OneDrive - Stanford\claude-skills\rigorous-proof"
echo.
"C:\ProgramData\anaconda3\python.exe" -u "C:\Users\wjzhong\OneDrive - Stanford\claude-skills\rigorous-proof\scripts\orchestrate.py" --work-dir "C:\Users\wjzhong\OneDrive - Stanford\claude-skills\rigorous-proof" --no-terminal --max-effort
echo.
echo Orchestrator exited with code: %ERRORLEVEL%
echo.
pause
