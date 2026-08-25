#!/usr/bin/env bash
input=$(cat)
skill_count=$(find ~/.claude/plugins -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')

PYTHON=""
for _py in /c/ProgramData/anaconda3/python.exe python3 python; do
    if "$_py" -c "print(1)" >/dev/null 2>&1; then
        PYTHON="$_py"
        break
    fi
done
[ -z "$PYTHON" ] && exit 0

cwd=$(echo "$input" | "$PYTHON" -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null)
github_repo=""
if [ -n "$cwd" ]; then
  remote=$(git -C "$cwd" remote get-url origin 2>/dev/null)
  if echo "$remote" | grep -q "github.com"; then
    github_repo=$(echo "$remote" | sed 's|.*github\.com[:/]\(.*\)\.git|\1|; s|.*github\.com[:/]\(.*\)|\1|')
  else
    repo_root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)
    [ -n "$repo_root" ] && github_repo=$(basename "$repo_root")
  fi
fi

"$PYTHON" - "$input" "$skill_count" "$github_repo" <<'PYEOF'
import sys, json, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = {}
try:
    data = json.loads(sys.argv[1])
except Exception:
    pass
skill_count  = sys.argv[2] if len(sys.argv) > 2 else ''
github_repo  = sys.argv[3] if len(sys.argv) > 3 else ''

import os
mcp_count = ''
settings_effort = ''
try:
    with open(os.path.expanduser('~/.claude/settings.json')) as _f:
        settings_effort = json.load(_f).get('effortLevel', '') or ''
except Exception:
    pass
try:
    # Live user-scope MCP servers are registered in ~/.claude.json, not settings.json.
    with open(os.path.expanduser('~/.claude.json')) as _f:
        mcp_count = str(len(json.load(_f).get('mcpServers', {})))
except Exception:
    pass

def get(path):
    keys = path.split('.')
    d = data
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return None
    return d

# ANSI codes
R   = '\033[0m'
B   = '\033[1m'
CYA = '\033[36m'
GRN = '\033[32m'
YLW = '\033[33m'
MAG = '\033[35m'
BLU = '\033[34m'
WHT = '\033[37m'
RED = '\033[31m'
DIM = '\033[2m'

def label(text, color):
    return f"{color}{B}{text}{R}"

def bar(pct, width=10):
    filled = max(0, min(width, round(float(pct) / 100 * width)))
    if pct >= 80:
        bar_color = RED
    elif pct >= 50:
        bar_color = YLW
    else:
        bar_color = GRN
    return f"{bar_color}{'█' * filled}{DIM}{'░' * (width - filled)}{R}"

def fmt_tokens(n):
    if n is None:
        return None
    n = int(n)
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)

# Terminal width, set by Claude Code in the COLUMNS env var. 0 => unknown, skip truncation.
try:
    COLS = int(os.environ.get('COLUMNS', '0'))
except (TypeError, ValueError):
    COLS = 0

ANSI_RE = re.compile(r'\033\[[0-9;]*m')

def visible_len(s):
    return len(ANSI_RE.sub('', s))

def truncate_ansi(s, width):
    # Trim to `width` visible columns, preserving ANSI codes, ellipsis on overflow.
    if width <= 0 or visible_len(s) <= width:
        return s
    limit = max(1, width - 1)  # reserve one column for the ellipsis
    out, count, i = [], 0, 0
    while i < len(s):
        m = ANSI_RE.match(s, i)
        if m:
            out.append(m.group())
            i = m.end()
            continue
        if count >= limit:
            break
        out.append(s[i])
        count += 1
        i += 1
    out.append('…')
    out.append(R)
    return ''.join(out)

line1 = []
line_meta = []   # model / agent / effort / spend -> second line
line2 = []
line3 = []

session_name = get('session_name')
if session_name:
    line1.append(f"{label('session', WHT)}:{session_name}")

cwd = get('cwd') or get('workspace.current_dir')
if cwd:
    line1.append(f"{label('dir', CYA)}:{cwd}")

if github_repo:
    line1.append(f"{label('gh', WHT)}:{github_repo}")

if skill_count:
    line1.append(f"{label('skills', BLU)}:{skill_count}")

if mcp_count:
    line1.append(f"{label('mcp', CYA)}:{mcp_count}")

wt_name = get('worktree.name')
if wt_name:
    wt_parts = [f"name:{wt_name}"]
    wt_path = get('worktree.path')
    wt_branch = get('worktree.branch')
    wt_orig_cwd = get('worktree.original_cwd')
    wt_orig_branch = get('worktree.original_branch')
    if wt_path: wt_parts.append(f"path:{wt_path}")
    if wt_branch: wt_parts.append(f"branch:{wt_branch}")
    if wt_orig_cwd: wt_parts.append(f"orig-dir:{wt_orig_cwd}")
    if wt_orig_branch: wt_parts.append(f"orig-branch:{wt_orig_branch}")
    line1.append(f"{label('worktree', WHT)}[{' '.join(wt_parts)}]")

model_id = get('model.id')
if model_id:
    line_meta.append(f"{label('model', GRN)}:{model_id}")

agent_name = get('agent.name')
if agent_name:
    line_meta.append(f"{label('agent', BLU)}:{agent_name}")

effort = get('effort') or get('effort_level') or settings_effort
if isinstance(effort, dict):
    effort = effort.get('level') or effort.get('effort') or ''
if effort:
    line_meta.append(f"{label('effort', MAG)}:{effort}")

cost_usd = get('cost.total_cost_usd')
if cost_usd is not None:
    try:
        line_meta.append(f"{label('spent', YLW)}:${float(cost_usd):.2f}")
    except (TypeError, ValueError):
        pass

used_pct = get('context_window.used_percentage')
input_tokens = get('context_window.current_usage.input_tokens')
output_tokens = get('context_window.current_usage.output_tokens')
if used_pct is not None:
    b = bar(used_pct)
    ctx_str = f"{b} {used_pct:.1f}%"
    extras = []
    if input_tokens: extras.append(f"in:{fmt_tokens(input_tokens)}")
    if output_tokens: extras.append(f"out:{fmt_tokens(output_tokens)}")
    if extras:
        ctx_str += " " + " ".join(extras)
    line2.append(f"{label('ctx', YLW)}[{ctx_str}]")

five_h_pct   = get('rate_limits.five_hour.used_percentage')
five_h_reset = get('rate_limits.five_hour.resets_at')
seven_d_pct  = get('rate_limits.seven_day.used_percentage')
seven_d_reset= get('rate_limits.seven_day.resets_at')
if five_h_pct is not None:
    b = bar(five_h_pct)
    s = f"5h:{b} {five_h_pct:.0f}%"
    if five_h_reset:
        from datetime import datetime, timezone
        try:
            t = datetime.fromtimestamp(five_h_reset, tz=timezone.utc).astimezone()
            s += f" resets:{t.strftime('%H:%M')}"
        except Exception:
            pass
    line3.append(s)
if seven_d_pct is not None:
    b = bar(seven_d_pct)
    s = f"7d:{b} {seven_d_pct:.0f}%"
    if seven_d_reset:
        from datetime import datetime, timezone
        try:
            t = datetime.fromtimestamp(seven_d_reset, tz=timezone.utc).astimezone()
            s += f" resets:{t.strftime('%Y-%m-%d')}"
        except Exception:
            pass
    line3.append(s)
if line3:
    line3 = [f"{label('limits', MAG)}[{' | '.join(line3)}]"]

# Reserve a small right-hand margin for Claude Code's own indicators.
wrap_at = COLS - 1 if COLS > 0 else 0
rows = [" | ".join(line1)]
if line_meta: rows.append(" | ".join(line_meta))
if line2: rows.append(" | ".join(line2))
if line3: rows.append(" | ".join(line3))
output = "\n".join(truncate_ansi(r, wrap_at) for r in rows)
print(output, end="")
PYEOF
