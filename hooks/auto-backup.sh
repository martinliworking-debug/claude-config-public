#!/usr/bin/env bash
# auto-backup.sh - SessionEnd hook: commit + push the ~/.claude config repo.
#
# Best-effort and non-blocking: every failure is swallowed so it never disrupts
# session teardown (always exits 0). Pairs with the SessionStart
# `git pull --rebase --autostash` hook, which keeps this machine current at start.
set +e

cd "$HOME/.claude" 2>/dev/null || exit 0

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

# Only operate on a real branch (skip detached HEAD / mid-rebase states).
branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null) || exit 0
[ -n "$branch" ] || exit 0

# Stage everything (respects .gitignore) and commit only if something changed.
git add -A 2>/dev/null

# Guard: never commit content that looks like a live credential. This script
# itself is excluded from the scan (it contains the patterns as literals).
if git diff --cached -- ':!hooks/auto-backup.sh' 2>/dev/null \
  | grep -qE 'github_pat_[A-Za-z0-9_]{8}|ghp_[A-Za-z0-9]{16}|sk-ant-|BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY'; then
  echo "auto-backup: BLOCKED - staged changes look like they contain a live secret; nothing committed. Review with: git -C ~/.claude diff --cached" >&2
  git reset -q 2>/dev/null
  exit 0
fi

if ! git diff --cached --quiet 2>/dev/null; then
  host="${HOSTNAME:-$(hostname 2>/dev/null)}"
  git commit -q -m "auto-backup: ${host} $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null
fi

# Push. If the remote has moved on (another machine), reconcile once and retry.
# On rebase conflict, abort and keep the local commit for a later manual sync.
if ! git push --quiet origin "$branch" 2>/dev/null; then
  if git pull --rebase --autostash --quiet 2>/dev/null; then
    git push --quiet origin "$branch" 2>/dev/null
  else
    git rebase --abort 2>/dev/null
  fi
fi

exit 0
