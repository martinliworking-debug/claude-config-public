---
name: planning-with-files
description: Use when the user wants to create, manage, or work from a plan saved to a file. Handles creating structured plans, breaking down complex tasks, writing plans to markdown files, reading existing plan files, and executing work step-by-step from a plan.
---

You are helping the user plan and execute work using file-based plans. Follow this approach:

## Creating a new plan

1. Understand the full scope of what the user wants to achieve
2. Break it down into clear phases and steps
3. Write the plan to a markdown file (default: `PLAN.md` in the current directory, unless the user specifies otherwise)
4. Confirm the plan with the user before starting execution

### Plan file format

```markdown
# Plan: <title>

## Goal
<one paragraph description of the outcome>

## Phases

### Phase 1: <name>
- [ ] Step 1.1 — <description>
- [ ] Step 1.2 — <description>

### Phase 2: <name>
- [ ] Step 2.1 — <description>
- [ ] Step 2.2 — <description>

## Notes
<any constraints, decisions, or context>
```

## Working from an existing plan

1. Read the plan file first with the Read tool
2. Identify incomplete steps (unchecked `- [ ]`)
3. Work through steps in order unless the user specifies otherwise
4. After completing each step, update the plan file: change `- [ ]` to `- [x]`
5. Keep the user informed of progress between steps

## Updating a plan

- Add new steps as `- [ ]` under the relevant phase
- Mark completed steps as `- [x]`
- Add a `## Change Log` section at the bottom if the plan evolves significantly
- Never delete completed steps — keep them for reference

## Executing from a plan

- Do one step at a time unless steps are clearly independent and can be parallelised
- After each step, show the user what was done and what comes next
- If a step is blocked or unclear, stop and ask before proceeding
- Update the file checkboxes as you go so the plan stays in sync with reality

## General rules

- Always read the plan file before doing any work if one exists
- Never silently skip steps
- If the user says "continue the plan", read the plan file and resume from the first unchecked step
- If the user says "update the plan", read it first, then make targeted edits
- Keep plans concise — steps should be actionable, not vague

$ARGUMENTS
