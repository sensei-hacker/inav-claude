# Agent Best Practices

Notes from Claude Code documentation for creating effective sub-agents.

**Sources:**
- [Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [Agent Skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [CLI reference - Claude Code Docs](https://code.claude.com/docs/en/cli-reference)

---

## Key Principles

### 1. Design Focused Agents
- Create agents with **single, clear responsibilities**
- Don't try to make one agent do everything
- Agents should be experts in one domain

### 2. Reference Internal Documentation
- Search `claude/developer/` for relevant docs, scripts, investigations
- Link to related documentation in agent file
- Include paths to relevant skills in `.claude/skills/`

### 3. Write Effective Descriptions
- Description field determines when Claude invokes the agent
- Include phrases like **"use PROACTIVELY"** or **"MUST BE USED"** to encourage automatic use
- Be specific about **when** to use the agent, not just what it does

### 4. Model Selection
- `haiku` - Fast, lightweight tasks (status checks, simple lookups)
- `sonnet` - Default, balanced (most agents)
- `opus` - Complex reasoning tasks
- `inherit` - Use same model as main conversation

### 5. Skills Don't Auto-Inherit
- Subagents do NOT automatically inherit Skills from main conversation
- Must explicitly list skills in the `skills` field if needed

### 6. Agents Cannot Spawn Agents
- Subagents cannot spawn other subagents
- Prevents infinite nesting
- Design agents to be self-contained

---

## What We Should Change in Our Agents

### Current Issues

1. **Descriptions are too long** - The description in YAML frontmatter is meant for Claude to decide when to use the agent, not for human documentation. Keep it concise.

2. **Model not always specified** - Should explicitly choose model based on task complexity.

3. **No skills field** - If agents need skills, must list them explicitly.

4. **Required context / paths not documented** - Agents should document what context callers must provide.

5. **Missing documentation references** - Agents should link to relevant docs in `claude/developer/`.

### Recommended Changes

| Agent | Current Model | Recommended | Notes |
|-------|---------------|-------------|-------|
| inav-builder | sonnet | sonnet | Add related docs links |
| sitl-operator | haiku | haiku | Add related docs links |
| test-engineer | sonnet | sonnet | Add related docs links |

### Description Format

**Current (too verbose):**
```yaml
description: "Compile INAV firmware targets including SITL and hardware boards. Use this agent for:\n\n**When to use:**\n- Building SITL for testing..."
```

**Better (concise, action-oriented):**
```yaml
description: "Build INAV firmware (SITL and hardware targets). Use PROACTIVELY when code changes need compilation verification. Returns build status and output paths."
```

---

## Agent Template

```yaml
---
name: agent-name
description: "One-sentence purpose. Use PROACTIVELY when [trigger condition]. Returns [output type]."
model: haiku|sonnet|opus
tools: ["Tool1", "Tool2"]
skills: ["skill-name"]
---

# Role statement (one paragraph)

## Responsibilities (3-5 bullet points)

## Available Scripts/Commands (with paths)

## Common Operations (step-by-step)

## Required Context

## Related Documentation

## Response Format (what to always include)

## Important Notes (gotchas, permissions)

---

## Self-Improvement: Lessons Learned

[Standard section for recording insights]

### Lessons

<!-- Add new lessons above this line -->
```

---

## Context Management

### Minimize Input Context
- Agent prompt should be self-contained
- Don't rely on conversation history
- Include all necessary paths and commands in the agent definition

### Minimize Output Context
- Return concise, structured responses
- Use standard response format
- Don't include verbose logs unless errors

### Use Indexes/Caches
- For large files (settings.yaml, MSP commands), consider pre-built indexes
- Agent can grep an index file rather than parse full source

---

## Checklist for New Agents

- [ ] Single, focused responsibility
- [ ] Concise description with PROACTIVELY trigger
- [ ] Appropriate model selected (haiku for simple, sonnet for complex)
- [ ] Skills explicitly listed if needed
- [ ] Required context section included
- [ ] Related documentation section with links to `claude/developer/`
- [ ] Self-improvement section included
- [ ] Response format defined
- [ ] Scripts/paths are relative to workspace root
