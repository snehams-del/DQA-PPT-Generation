# AGENTS.md — routing for this project

This file tells your AI coding agent (Claude Code / Gemini CLI / Codex /
Cursor / Aider / …) which installed skill drives the conversation, and
which skills handle mechanics underneath.

## Skill routing (managed by install-vertical-skill)

**Retail skills installed:** {{SKILL_LIST}}
**Most recently installed (primary):** `{{SKILL_NAME}}`
**Skill files placed at:** {{SKILL_DIRS}} (every agent's expected location)

When the user describes a retail / e-commerce / product search / virtual
try-on / product recommendation / product content request:

- **The retail skill drives the QUESTION FLOW.** Question wording, defaults,
  mode selection (Quick / Full), order of steps, and conversation tone
  come from whichever installed retail skill matches the user's intent
  (one of: {{SKILL_LIST}}).
- **DO NOT use `google-agents-cli-*` skills to drive the question flow.**
  Those skills handle mechanics — scaffold/enhance commands, eval
  methodology, deploy, publish, observability — which the retail skill
  *delegates to* once the user's answers are gathered.

### Phase ownership

| Phase | Skill in charge |
|---|---|
| Q-MODE selection (Quick vs Full) | the matching retail skill ({{SKILL_LIST}}) |
| Domain interview | the matching retail skill |
| Project scaffold mechanics (`agents-cli scaffold enhance .`) | `google-agents-cli-scaffold` (executes commands the retail skill issues) |
| Evaluation methodology | `google-agents-cli-eval` |
| Deployment | `google-agents-cli-deploy` |
| Gemini Enterprise registration | `google-agents-cli-publish` |
| Observability | `google-agents-cli-observability` |

### Required first response (per skill)

These rules apply to **every** AI coding agent reading this file, even
those that don't load skill files separately (Codex, Cursor, Aider, etc.).
The first response below replaces any default behavior from other active
skills.

{{FIRST_RESPONSE_SECTION}}

### After the first response

Once Q-MODE is answered, follow the active retail skill's full instructions
from its SKILL.md (at {{SKILL_DIRS}}). Specifically: ask one question at a
time, format every question as `Q: <question>? [default: <value>]`, and
accept empty input as "use the default." Never bundle multiple questions
into a numbered list.

### Why this routing exists

Lightweight disambiguation while the agents-cli team and the retail-skills
team coordinate on a shared skill-precedence mechanism. You can edit
anything in this file *outside* the marker block to add project-specific
guidance. Anything *between* the markers is overwritten on re-install.

Skills source: {{SOURCE_BASE}}
