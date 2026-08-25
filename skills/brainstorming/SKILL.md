---
name: brainstorming
description: Use when the user wants to brainstorm ideas, explore possibilities, think through a problem creatively, or generate options. Facilitates structured creative thinking, divergent ideation, and idea evaluation.
---

Help the user brainstorm effectively. Adapt your approach based on the topic and what they need.

## Default approach

1. **Clarify the goal** -- confirm what they are trying to solve or explore (skip if clear from $ARGUMENTS)
2. **Diverge** -- generate a wide range of ideas without filtering, including unconventional ones
3. **Organise** -- group ideas into themes or categories
4. **Evaluate** -- highlight the most promising ideas with brief reasoning
5. **Next steps** -- suggest how to develop the top ideas further

## Brainstorming techniques (pick the most appropriate, or combine)

### Quantity first
Generate at least 10 ideas before evaluating any. Quantity breeds quality -- no idea is too wild at this stage.

### "How might we..."
Reframe the problem as "How might we [achieve X]?" to open up solution space.

### Reverse brainstorming
Ask "How could we make this worse / fail?" then flip each answer into a solution.

### SCAMPER
Apply each lens to the topic:
- **S**ubstitute -- what could be replaced?
- **C**ombine -- what could be merged?
- **A**dapt -- what could be borrowed from elsewhere?
- **M**odify / Magnify -- what could be changed or amplified?
- **P**ut to other uses -- what else could this be used for?
- **E**liminate -- what could be removed?
- **R**earrange / Reverse -- what could be reordered or flipped?

### First principles
Break the problem down to its fundamental truths, then build back up from scratch.

### Analogies
"How does nature / another industry / a completely different field solve this?"

## Output format

Present ideas clearly:

```
## Ideas

### Theme 1: <name>
- Idea A -- brief explanation
- Idea B -- brief explanation

### Theme 2: <name>
- Idea C -- brief explanation

## Top picks
1. **Idea X** -- why this is promising
2. **Idea Y** -- why this is promising

## Suggested next steps
- ...
```

## Rules
- Never shut down an idea during divergence phase
- Push beyond the obvious -- aim for at least one surprising idea per theme
- If the user says "more" or "keep going", generate another round without repeating previous ideas
- If the user picks an idea, help them develop it in detail

$ARGUMENTS
