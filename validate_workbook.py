#!/usr/bin/env python
"""PostToolUse hook: validate freshly written .xlsx deliverables.

Reads the hook payload (JSON) on stdin, finds any .xlsx path named in the
tool call, and checks it for spreadsheet error tokens (#REF!, #DIV/0!, ...).
Only files modified in the last few minutes are checked, so reading an old
input workbook never trips it.

On a clean file (or when no .xlsx is named) it prints nothing and exits 0.
On problems it emits PostToolUse JSON so the finding is shown to the user and
fed back into the model context to fix, without blocking the turn.

Scope (v1): error tokens only. Residual fills/borders are not yet checked.
"""

import json
import os
import re
import sys
import time

# Only validate files touched this recently (seconds), so input workbooks
# that were merely read are not flagged.
FRESH_SECONDS = 300

ERROR_TOKENS = (
    "#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NULL!", "#NUM!",
    "#SPILL!", "#CALC!", "#GETTING_DATA", "#FIELD!", "#BLOCKED!",
    "#CONNECT!", "#UNKNOWN!", "#PYTHON!",
)

# How many offending cells to list per file before summarising the rest.
MAX_CELLS_REPORTED = 15


def candidate_paths(tool_input):
    """Pull every .xlsx path named anywhere in the tool call."""
    paths = []

    # Direct path fields used by the Excel MCP tools and file tools.
    for key in ("fileAbsolutePath", "file_path", "path", "filename", "fileName"):
        val = tool_input.get(key)
        if isinstance(val, str):
            paths.append(val)

    # Shell commands (Bash / PowerShell): scrape .xlsx tokens out of the text.
    command = tool_input.get("command")
    if isinstance(command, str):
        # Quoted paths first (handles spaces, e.g. 'C:\My Files\book.xlsx').
        for m in re.findall(r"""['"]([^'"]+\.xlsx)['"]""", command, re.IGNORECASE):
            paths.append(m)
        # Then bare, unquoted tokens.
        for m in re.findall(r"""(?<!['"])(\S+\.xlsx)\b""", command, re.IGNORECASE):
            paths.append(m)

    # Catch-all: any other string value that points at an .xlsx.
    for val in tool_input.values():
        if isinstance(val, str) and val.lower().endswith(".xlsx"):
            paths.append(val)

    # Normalise, keep existing + recently written files, de-duplicate.
    seen, out = set(), []
    now = time.time()
    for p in paths:
        p = p.strip().strip("'\"")
        if not p.lower().endswith(".xlsx"):
            continue
        ap = os.path.abspath(p)
        if ap in seen or not os.path.isfile(ap):
            continue
        try:
            if now - os.path.getmtime(ap) > FRESH_SECONDS:
                continue
        except OSError:
            continue
        seen.add(ap)
        out.append(ap)
    return out


def scan_cells(ws):
    """Yield (coord, token) for cells holding an error token."""
    for row in ws.iter_rows():
        for cell in row:
            v = cell.value
            if v is None:
                continue
            s = str(v)
            if "#" not in s:
                continue
            for tok in ERROR_TOKENS:
                if tok in s:
                    yield cell.coordinate, tok
                    break


def validate(path):
    """Return a list of human-readable findings for one workbook."""
    import openpyxl

    findings = []
    # Pass 1: formula strings (openpyxl-written files keep no cached values).
    # Pass 2: cached values (files last saved by Excel surface errors here).
    for data_only in (False, True):
        try:
            wb = openpyxl.load_workbook(path, read_only=True, data_only=data_only)
        except Exception as exc:  # noqa: BLE001 - report, never crash the hook
            findings.append(f"could not open ({data_only=}): {exc}")
            continue
        try:
            for ws in wb.worksheets:
                for coord, tok in scan_cells(ws):
                    findings.append(f"{ws.title}!{coord}  {tok}")
        finally:
            wb.close()

    # De-duplicate across the two passes, preserve order.
    seen, out = set(), []
    for f in findings:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def main():
    try:
        # Read bytes and decode utf-8-sig so a leading BOM is stripped
        # cleanly (some shells prepend one when piping to a child process).
        raw = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace")
        payload = json.loads(raw)
    except Exception:
        return  # No usable payload: stay silent.

    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return

    problems = {}
    for path in candidate_paths(tool_input):
        findings = validate(path)
        if findings:
            problems[path] = findings

    if not problems:
        return  # Clean (or nothing to check): no output.

    lines = []
    total = 0
    for path, findings in problems.items():
        total += len(findings)
        name = os.path.basename(path)
        shown = findings[:MAX_CELLS_REPORTED]
        lines.append(f"{name}: {len(findings)} error cell(s)")
        lines.extend(f"  - {f}" for f in shown)
        if len(findings) > MAX_CELLS_REPORTED:
            lines.append(f"  - ... and {len(findings) - MAX_CELLS_REPORTED} more")

    detail = "\n".join(lines)
    summary = (
        f"Workbook validation FAILED: {total} error cell(s) across "
        f"{len(problems)} file(s). Fix before issuing."
    )
    out = {
        "systemMessage": summary,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "Excel workbook validation found spreadsheet error tokens "
                "(e.g. #REF!). These must be resolved before the file is "
                "treated as issue-ready:\n" + detail
            ),
        },
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
