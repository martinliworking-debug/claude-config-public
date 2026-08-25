# claude-team.ps1 - start ONE Claude Code session with experimental agent teams enabled.
#
# Teams stay OFF globally on purpose: while CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 is
# set, any subagent Claude names launches as a TEAMMATE (a fully independent session
# whose result never returns to the caller), so teams can form even when you didn't
# ask for one - which silently breaks the orchestration workflow's wait-on-results
# delegations (deep-reasoner / fast-worker). Enable per session, only when you
# actually want a team: parallel research/review with cross-challenge, or
# competing-hypothesis debugging.
#
# Windows runs teams in-process only (split panes need tmux or iTerm2). Drive the
# team from the agent panel: up/down select teammate, Enter view/message, Esc
# interrupt, x stop, Ctrl+T task list. Start with 3 teammates; token use is roughly
# 3-4x a single session and scales linearly per teammate.
#
# Usage: claude-team.ps1 [any normal claude args]
$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"
claude @args
