---
name: skill-vetter
description: Use when the user wants to review, evaluate, or improve an existing Claude Code skill. Checks skill files for quality, clarity, correct format, good descriptions, and effective instructions -- then suggests or applies improvements.
---

Review and improve a Claude Code skill file.

## Steps

### 1. Identify the skill to vet
- If a skill name or path is provided in $ARGUMENTS, read that skill file
- Otherwise, list all skills in `~/.claude/skills/` and `.claude/skills/` and ask the user which one to vet

### 2. Read the skill file
Use the Read tool to load the `SKILL.md` content.

### 3. Evaluate against these criteria

#### Frontmatter
- [ ] `name` is present and matches the directory name
- [ ] `description` is specific enough for Claude to know when to auto-invoke it
- [ ] `description` covers both WHAT it does and WHEN to use it
- [ ] Optional flags (`disable-model-invocation`, `allowed-tools`) are used appropriately

#### Instructions quality
- [ ] Steps are clear and actionable (not vague)
- [ ] Edge cases and failure modes are covered
- [ ] Output format is specified where relevant
- [ ] `$ARGUMENTS` is included so user input is passed through
- [ ] No contradictory or redundant instructions
- [ ] Instructions are concise -- no unnecessary padding

#### Scope
- [ ] The skill does one thing well (not trying to do too much)
- [ ] It is scoped appropriately (global vs project)

### 4. Report findings

Present a structured report:

```
## Skill Vet Report: /<skill-name>

### Passes
- ...

### Issues
- [CRITICAL] ...
- [MINOR] ...

### Suggestions
- ...

### Overall rating: Strong / Good / Needs work / Poor
```

### 5. Offer to fix
Ask the user if they want you to apply the suggested improvements directly to the skill file. If yes, use the Edit tool to update it.

## Severity levels
- **CRITICAL** -- will cause the skill to fail or behave unpredictably
- **MINOR** -- reduces quality or clarity but skill will still work
- **SUGGESTION** -- optional improvement

$ARGUMENTS
