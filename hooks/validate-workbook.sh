#!/usr/bin/env bash
# validate-workbook.sh - PostToolUse hook wrapper for validate_workbook.py.
# Resolves python per machine (Anaconda preferred, then PATH); silently no-ops
# on machines with neither, so the shared settings.json works everywhere.
py="/c/ProgramData/anaconda3/python.exe"
if [ ! -x "$py" ]; then
  py=$(command -v python 2>/dev/null) || exit 0
fi
[ -n "$py" ] || exit 0
exec "$py" "$HOME/.claude/validate_workbook.py"
