# Claude Code Config

A complete, working Claude Code setup: global instructions (`CLAUDE.md`), settings with lifecycle hooks, a custom multi-line statusline, orchestration subagents, 26 skills, and MCP server templates. Extracted from a daily-driver config used on Windows 11; most of it is OS-agnostic, the Windows-specific parts are called out below.

**This is an opinionated config.** Read `CLAUDE.md` before adopting it — it enforces Australian English spelling, strict Office-document rules (native charts only, verification read-backs), and a multi-agent orchestration workflow. Delete or adapt anything that does not match how you work.

## What's in here

| Path | Description |
|---|---|
| `settings.json` | Model pin, permission defaults, hooks, statusline wiring, auto-installed plugins |
| `CLAUDE.md` | Global instructions applied to every project |
| `agents/` | User-level subagents for the orchestration workflow: `deep-reasoner` and `fast-worker` (both pinned to `claude-opus-5`) |
| `hooks/` | `auto-backup.sh` (SessionEnd: commit+push this repo), `commit-reminder.ps1` (Stop: nudge on uncommitted changes), `validate-workbook.sh` (PostToolUse: Excel integrity check) |
| `scripts/switch-account.ps1` | Clears cached credentials so the next start prompts for login |
| `statusline.sh` | Multi-line status bar: session/dir/repo, model/effort/spend, context bar, rate-limit bars |
| `validate_workbook.py` | Workbook validation hook body (needs `openpyxl`; silently no-ops without it) |
| `skills/` | 26 skills — see the skills section |
| `skills/_tools/skill_lint.py` | Lints every `SKILL.md`: frontmatter parses, names match, referenced paths resolve |
| `mcp-servers.template.json` | Sanitised template of the MCP servers this config expects (no secrets) |

## First-time setup

### 1. Prerequisites

| Tool | Needed for | Install |
|---|---|---|
| **Node.js 18+** | Claude Code itself, `npx`-based MCP servers, the impeccable hook, archify renderers | [nodejs.org](https://nodejs.org) or `winget install OpenJS.NodeJS.LTS` |
| **Claude Code** | everything | `npm install -g @anthropic-ai/claude-code` |
| **Git** (with Git Bash on Windows) | sync hooks, statusline (`bash` scripts run via Git Bash on Windows) | `winget install Git.Git` |
| **Python 3** | statusline, workbook-validation hook, document skills | `winget install Python.Python.3.12` (or Anaconda; the hooks probe `C:\ProgramData\anaconda3` first, then PATH) |
| Python packages | document/Excel skills and hooks | `pip install openpyxl pandas python-docx python-pptx pyyaml pdf-inspector markitdown` |
| **poppler** *(optional)* | Claude's Read tool on scanned/image PDFs | `winget search poppler` then `winget install --id <id> --scope user` |
| **officecli** *(optional)* | the officecli skill + MCP server | Windows: `irm https://d.officecli.ai/install.ps1 \| iex` · macOS/Linux: `curl -fsSL https://d.officecli.ai/install.sh \| bash` |
| **Codex CLI** *(optional)* | the orchestration workflow's second-opinion peer | `npm install -g @openai/codex`, then `codex login` |

Everything runs without the optional rows — the related skills/hooks just stay dormant.

### 2. Install the config

Back up any existing `~/.claude` first, then either clone this repo as your config directory:

```bash
mv ~/.claude ~/.claude.bak 2>/dev/null
git clone <this-repo-url> ~/.claude
```

or cherry-pick files into your existing `~/.claude` (start with `CLAUDE.md`, `skills/`, `statusline.sh`).

### 3. Make the sync hooks yours (or remove them)

`settings.json` wires two hooks that assume `~/.claude` is a git repo **you can push to**:

- SessionStart: `git pull --rebase --autostash`
- SessionEnd: `hooks/auto-backup.sh` (commit + push, with a secret-pattern guard that blocks credential-looking diffs)

Fork this repo and point `origin` at your fork (`git -C ~/.claude remote set-url origin <your-fork>`), or delete the `SessionStart`/`SessionEnd` entries from `settings.json` if you don't want git-synced config.

### 4. Check the model pin

`settings.json` pins `"model": "claude-fable-5[1m]"` (Fable 5 with 1M context) and `"effortLevel": "xhigh"`. If your account doesn't have Fable 5 with 1M context, change or remove the `model` line, or Claude Code will fail to start a session.

### 5. Plugins and MCP servers

- **Plugins** auto-install on first launch from `enabledPlugins`: Karpathy coding guidelines, the Codex plugin, and Matt Pocock's skills. No action needed (the Codex *plugin* installs regardless; the Codex *CLI* login is only needed if you use it).
- **MCP servers** are NOT tracked (live config holds tokens and absolute paths). Recreate what you need from `mcp-servers.template.json` with `claude mcp add -s user ...`, supplying your own GitHub PAT etc. Verify with `claude mcp list`.

### 6. Start `claude`

Settings, skills, statusline, hooks, and agents are live immediately.

## Skills

Self-authored: `documents` (PDF/Office reading routes), `officecli` (Office CLI workflows), `brainstorming`, `planning-with-files`, `find-skills`, `skill-creator`, `skill-vetter`, `publish-to-web`, plus `_tools/skill_lint.py` for authoring hygiene.

Vendored third-party (kept under their own licences — see `THIRD-PARTY-NOTICES.md`):

- **Cloudflare family** (11 skills, Apache-2.0): `agents-sdk`, `cloudflare`, `cloudflare-email-service`, `cloudflare-one`, `cloudflare-one-migrations`, `durable-objects`, `sandbox-sdk`, `turnstile-spin`, `web-perf`, `workers-best-practices`, `wrangler`
- `archify` — architecture/sequence/dataflow diagrams (MIT)
- `frontend-slides` — HTML presentations (MIT)
- `impeccable` — frontend design review (Apache-2.0)
- `markitdown` — convert anything to Markdown (MIT, K-Dense)
- `playwright-cli` — Playwright CLI reference (Apache-2.0, Microsoft)
- `stop-slop` — de-AI-ify prose (MIT)
- `theme-factory` — artifact theming (Apache-2.0, Anthropic)

## Windows notes

- Hooks and the statusline are bash scripts; on Windows they run via Git Bash (bundled with Git for Windows). `commit-reminder.ps1` is PowerShell.
- The statusline needs a Python on PATH (or Anaconda at `C:\ProgramData\anaconda3`); without one it renders blank.
- If Claude Code's Chrome integration is enabled it regenerates its own native-host wrapper; nothing to configure here.

## Licence

Original content: MIT (see `LICENSE`). Vendored skills keep their upstream licences: `THIRD-PARTY-NOTICES.md`.
