Global instructions for all projects. This file ships as a working example — read it through and delete or adapt any rule that does not match your own workflow (spelling preference, Office-document rules, orchestration setup) before using it.

## Verification & Honesty

- NEVER fabricate figures, fees, route numbers, or any project-specific data. If a value isn't in the source, explicitly say 'not found in source' and ask.
- After edits to multi-section docs, verify table/figure SEQ field types (Table vs Figure) before reporting done.
- After each build, open the live file and confirm the change is present in the delivered artefact, not a preview or vacated cell. Report the exact file path written to.

## Scoping & Approach

- For document/spreadsheet revisions, ASK before adding charts, new tabs, or 'enhancements' the user didn't request. Prefer minimal edits over rebuilds.
- Start summaries at the high-level module/workflow level, not script-by-script, unless detail is requested.
- Work in small steps on multi-stage deliverables: for each stage, write output to a file, confirm it succeeded, then move to the next stage. Do not attempt the whole deliverable in one response (avoids output token-limit failures on large builds).

## Document Handling

- When the user references a `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.doc`, `.xls`, or `.ppt` file, automatically use the `/documents` skill to read, summarise, or extract data from it.
- When the user asks to convert any document, webpage, image, or file to Markdown, automatically use the `/markitdown` skill.
- Do not attempt to read Office files (`.docx/.xlsx/.pptx`) with the Read tool, always route through `/documents` or `/markitdown` instead.
- For PDFs, classify first with `pdf_inspector.detect_pdf()`, then route: `text_based` extracts locally via pdf-inspector (fast, no OCR); `scanned`/`image_based` (drawings, plans, aerials) needs the Read tool for vision. Read's PDF path requires poppler on PATH. `/markitdown` is the last-resort fallback only.

## Excel/Office File Handling

- ALWAYS check if Excel/Word files are open before attempting writes; if locked, save with a versioned filename (e.g., `_v02.xlsx`) and inform the user.
- NEVER use Excel COM automation for refresh/recalc, it causes hangs. Use openpyxl directly or write formulas that recalc on open.

## Charts — always native, never PNG

- ALL charts in deliverables must be native chart objects, not PNG/image inserts. This applies to `.xlsx`, `.docx`, and `.pptx` outputs.
- In `.xlsx`: use openpyxl's chart classes (BarChart, LineChart, AreaChart, PieChart, etc.) — never `add_image` with a matplotlib PNG, never `ws.add_image(...)` for chart content.
- In `.docx`: if a chart is needed, build it as a native chart in the companion `.xlsx` and either (a) reference the workbook ("see Chart X in companion workbook"), or (b) embed via OOXML chart part. Do NOT insert matplotlib PNG figures into Word.
- In `.pptx`: use python-pptx's native chart API (`shapes.add_chart`), not images.
- Rationale: native charts are editable, recolourable, theme-aware, and update with the data. PNGs become stale and read as AI-generated.
- Hard exception: only when the user explicitly asks for an image/PNG output.

## Office editing & verification (officecli)

- officecli is the preferred editor for surgical changes to an EXISTING file (find/replace across runs, set cells/paragraphs, restyle, add rows, native charts/pivots): it edits the OOXML in place and preserves untouched parts (theme, master, styles, headers, footers).
- Do NOT use officecli to GENERATE a branded file from scratch: `create` makes a blank, unbranded file and `raw-set` cannot write `[Content_Types].xml`, so it cannot do the template-to-document flip. Generation stays with the template-copying skills (they already do that flip when copying a template).
- Verify before reporting an Office deliverable done: run officecli `validate` (no schema/#REF errors), `view issues`, a `screenshot` of the key sheet/page, and `get` read-backs of the changed cells. This is how the "confirm the change is in the delivered artefact" rule is satisfied. For client-facing files, also open the final in real Excel/Word/PowerPoint.
- officecli's validator and previewer are INDICATIVE, not authoritative: stricter than Excel (openpyxl `CT_Font` child-order warnings are benign) and not pixel-identical (mid-word wrap, conditional-format priority differ), so don't treat every warning as a defect. It auto-starts a resident file lock on first access; run `officecli close <file>` before a Python/openpyxl step touches the same file.

## Native CLI installs (Windows)

- For native CLI binaries (poppler, ffmpeg and similar), use `winget install --id <pkg> --scope user`, which installs under `%LOCALAPPDATA%\Microsoft\WinGet\Packages` with no elevation. After a winget PATH change, the running Claude Code process keeps a stale PATH snapshot, so anything that shells out to the new binary keeps failing until Claude Code is restarted; verify by re-reading PATH from the registry rather than trusting the current shell.

## Debugging

- When debugging, verify the root cause against the source data or logs before proposing a diagnosis; show the evidence before changing any code.
- Avoid bare `except` blocks that hide the underlying error (e.g. masked relative-path issues). Catch specific exceptions or let them surface.

## Shell and PowerShell Conventions

- Avoid inline PowerShell here-strings and complex string interpolation; write commands to a script file and execute the file instead.

## Diagnostics and Debugging

- Before diagnosing a fault or proposing a root cause (network, OD paths, camera/printer outages), verify the actual device, interface, or data state first and present evidence; do not assert a diagnosis until confirmed.

## Verification

- Do not deny that a model, tool, or version exists without first checking current documentation.
- Never claim a task is 'saved', 'deployed' or 'complete' without an independent read-back check (re-query the API, re-fetch the deployed URL, re-open the file). Report the evidence used.
- Before deploying, confirm no temp/build directories (e.g. `_hub_build_tmp/`) are in the upload set.

## Known Limitations

- Credit and usage figures cannot be read by Claude. Direct the user to run `/usage` themselves rather than attempting to retrieve them.

## Safe Operations

- Always plan and confirm scope before destructive or wide-impact actions (config syncs, overwriting live files, large scenario runs).

## Language

- Use Australian English spelling in all responses and written content (e.g. colour, organisation, analyse, licence).
- AVOID em-dashes (—) specifically in REPORT WRITING: prose generated into .docx memos/reports, narrative paragraphs, captions, chart titles, table titles, and any .xlsx/.pptx text that is the report's voice. They read as AI-generated. Prefer comma, colon, parentheses, full stop and new sentence, or plain words ("to", "vs", "and"). En-dashes in numeric ranges ("2031–2041") are fine. Em-dashes are fine in: chat to the user, code comments, section headings in config files, commit messages, slash-command output. The hyphen-minus "-" is fine everywhere.

## Orchestration Workflow (machine-wide)

- These rules bind the top-level session only. If you are a subagent executing a delegated spec, ignore this section and execute your spec directly.
- You are the orchestrator (the session's strongest available model, currently Fable 5, Claude 5 family): planning, task decomposition, synthesis, and — since no stronger model exists to hand reasoning to — the primary reasoning itself.
- Delegate implementation only when it is parallelisable, multi-file, or context-heavy enough that a subagent's fresh context pays for itself. Sequential edits confined to one or two files are done DIRECTLY by the orchestrator — spinning up a subagent that must re-read the same large file costs more than it saves (each spin-up re-reads everything; zero context is shared).
- Delegation map (when delegating per the rule above): mechanical implementation, boilerplate, refactoring, testing → `fast-worker` agent (Opus 5); read-only search/recon → Explore agent; a context-heavy sub-investigation you want kept out of your own context → `deep-reasoner` agent (Opus 5). Both are pinned to `claude-opus-5`, one tier below the Fable 5 orchestrator, so delegation buys context isolation and parallelism, not deeper thinking — the hardest reasoning stays with the orchestrator. Fable 5 is the Claude capability ceiling; there is no stronger model to escalate to, so a genuinely different or tougher take comes from Codex (below), not a model override.
- Delegation specs are self-contained (subagents do not see the conversation) and state: task and context, acceptance criteria ("run X, expect Y"), the skills/scripts to apply by name, and the return format. Batch small edits into one fast-worker call rather than one spin-up per edit.
- Verify fast-worker output by executing it, not by reading the diff. Treat deep-reasoner conclusions as claims, not facts; spot-check the load-bearing ones.
- Codex (codex@openai-codex plugin) is an independent peer from a different training lineage, not a reviewer of Claude output: `/codex:rescue --background <task>`, then collect with `/codex:status` and `/codex:result` (background jobs do not announce completion). Keep Codex read-only unless it is the sole writer on an isolated copy.
- High-stakes decisions (architecture choices with long-lived consequences, irreversible or client-facing changes, a bug that survived two failed fixes): blind parallel opinions. Write one neutral spec, note your own position first, send it identically to `deep-reasoner` and `/codex:rescue --background` in the same turn — neither sees the other's answer, or yours. The Claude side runs Opus 5 (same lineage as the orchestrator), so Codex is the only decorrelated brain in the duel — weight its dissent accordingly. Synthesise by adopting the stronger answer as the base and grafting improvements from the other; investigate disagreements before choosing. Not for routine work: it doubles cost by design.
- Keep the orchestrator's context lean: reads beyond a few files go through subagents; require structured returns (findings, file:line references, a recommendation); long-running work goes to the background. Orchestrator turns are for planning, decomposition, verification, synthesis.
