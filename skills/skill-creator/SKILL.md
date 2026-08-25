---
name: skill-creator
description: Use when the user wants to create a new Claude Code skill (slash command). Guides through naming, writing the description and instructions, and saves the skill to the correct directory.
---

Help the user create and install a new Claude Code skill.

## Steps

### 1. Gather requirements
Ask the user (or infer from $ARGUMENTS):
- What should the skill be called? (becomes the slash command, e.g. `my-skill` → `/my-skill`)
- What should it do? (one sentence)
- Should it be **global** (all projects) or **project-only** (current project)?
- Any specific tools it should be restricted to? (optional)
- Should only the user be able to invoke it, not Claude automatically? (use `disable-model-invocation: true`)

### 2. Determine install path
- **Global**: `~/.claude/skills/<skill-name>/SKILL.md`
- **Project**: `.claude/skills/<skill-name>/SKILL.md`

Default to global unless the user specifies otherwise.

### 3. Write the skill file

Use this structure:

```markdown
---
name: skill-name
description: Clear description of what this skill does and when to use it
---

Instructions for Claude when this skill is invoked...

$ARGUMENTS
```

Guidelines for writing good skill instructions:
- Be specific about what Claude should do step by step
- Include output format expectations if relevant
- Cover edge cases and failure modes
- Keep instructions actionable, not vague
- Include `$ARGUMENTS` at the end so user input is passed through

### 4. Create the file
- Create the directory: `~/.claude/skills/<skill-name>/`
- Write `SKILL.md` using the Write tool

### 5. Confirm
Tell the user:
- Where the skill was installed
- How to invoke it (`/<skill-name>`)
- That Claude Code needs to be restarted to pick up the new skill

## Example skill names and descriptions
- `code-review` — Review code for bugs, security issues, and style
- `explain` — Explain a piece of code in plain language
- `git-summary` — Summarise recent git changes
- `refactor` — Refactor selected code for clarity and performance

$ARGUMENTS
