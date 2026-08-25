---
name: find-skills
description: Use when the user wants to find, list, browse, or search their installed Claude Code skills. Lists all skills in global and project skill directories, shows descriptions, and helps the user discover what slash commands are available.
---

Help the user discover their installed Claude Code skills.

## Steps

1. List all skills in the global skills directory:
   ```
   ~/.claude/skills/
   ```
2. List all skills in the current project skills directory (if it exists):
   ```
   .claude/skills/
   ```
3. For each skill found, read its `SKILL.md` frontmatter to extract the `name` and `description`
4. Present the results in a clean table grouped by scope (Global / Project)

## Output format

```
### Global Skills (~/.claude/skills/)

| Skill | Description |
|-------|-------------|
| /skill-name | What it does |

### Project Skills (.claude/skills/)

| Skill | Description |
|-------|-------------|
| /skill-name | What it does |
```

## If the user provides a search term

Filter the results to skills whose name or description contains the search term (case-insensitive).

## If no skills are found

Tell the user that no skills are installed yet and explain that skills go in `~/.claude/skills/<skill-name>/SKILL.md` for global scope or `.claude/skills/<skill-name>/SKILL.md` for project scope.

$ARGUMENTS
