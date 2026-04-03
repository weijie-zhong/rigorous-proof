#!/bin/bash
echo "Starting orchestrator at $(date)"
echo "Working directory: C:\Users\wjzhong\OneDrive - Stanford\claude-skills\rigorous-proof"
echo
"C:\Users\wjzhong\anaconda3\python.exe" -u "C:\Users\wjzhong\OneDrive - Stanford\claude-skills\rigorous-proof\scripts\orchestrate.py" --work-dir "C:\Users\wjzhong\OneDrive - Stanford\claude-skills\rigorous-proof" 
EXIT_CODE=$?
echo
echo "Orchestrator exited with code: $EXIT_CODE"
echo
echo "Press any key to close..."
read -n 1 -s
