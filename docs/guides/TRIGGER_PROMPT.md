# Master AI Trigger Prompt (v2)

Copy-paste this to start work on a feature.

```text
ACT AS A SENIOR ENGINEER FOLLOWING THIS EXACT PROCESS.

FEATURE REQUEST: {user story or ticket summary}
TICKET ID: {TICKET-123}

STEP 0 - LOAD RULES AND STATE
- Read AGENTS.md and .ai-workflow.yaml.
- Run `python scripts/ai-feature.py status`. If no ticket is active, run
  `python scripts/ai-feature.py start {TICKET-123}`.

STEP 1 - INTELLIGENCE CHECK
- Run `python scripts/ai-feature.py intelligence check`.
- READY -> read only the docs/architecture/ and docs/kb/ files relevant to
  the area this feature touches (see docs/guides/CONTEXT_RETRIEVAL.md for
  routing/depth discipline -- match effort to task size), proceed to Step 2.
- REFRESH REQUIRED -> perform a full Codebase Intelligence pass per
  docs/guides/CODEBASE_INTELLIGENCE_ENGINE.md, write/update the artifacts in
  docs/architecture/ and docs/kb/, then run
  `python scripts/ai-feature.py intelligence refresh`.
- STALE or the feature touches an undocumented/unfamiliar area -> do a
  targeted review of just that area (same engine, narrower scope), update
  the relevant artifact, then run
  `python scripts/ai-feature.py intelligence targeted`.
- Never guess architecture. Every claim is Confirmed, Strongly Inferred, or
  Uncertain -- state which.

STEP 2 - FEATURE ANALYSIS
- Run `python scripts/ai-feature.py analyze`.
- Retrieve targeted context only: the entry point, its direct dependencies,
  and their tests (docs/guides/CONTEXT_RETRIEVAL.md levels 1-2). Escalate to
  a deeper read only for architectural uncertainty or a security-sensitive
  path -- don't default to reading the whole subsystem.
- Trace the actual execution path for this feature through real files and
  symbols (entry point -> ... -> response).
- Fill in the SSOT's Feature Analysis section: execution path, affected
  files, dependencies, data impact, security impact, integration impact,
  test impact, blast radius, risks, assumptions, unknowns.
- If the feature touches unfamiliar technology, fill in the Technology
  Learning Bridge table: what it is, where/why used here, minimum knowledge
  needed to change it safely.
- Run `python scripts/ai-feature.py approve analysis`. Fix any reported gap
  and re-run if it fails.

STEP 3 - PLAN
- Break the feature into Jira-style Tasks/Subtasks (SUB-x.y) with
  acceptance criteria in the SSOT Implementation Plan section.
- Run `python scripts/ai-feature.py approve plan`.

STEP 4 - EXECUTE (one subtask at a time)
- `python scripts/ai-feature.py next-subtask SUB-x.y`
- Inspect the relevant code -> implement -> write/run tests -> verify.
- Update the Execution Log with the result and commit hash.
- `python scripts/ai-feature.py complete-subtask SUB-x.y`
- Commit: single sentence, imperative, Conventional Commits, <=72 chars, no
  trailing punctuation in the description (enforced by the commit-msg hook
  -- run `python scripts/install-hooks.py` once per clone if not installed).
- Repeat for every subtask, then
  `python scripts/ai-feature.py approve execute`.

STEP 5 - VERIFY
- Run the full regression/test suite. Confirm acceptance criteria are met
  and, if Security Impact was non-empty in Step 2, confirm it was actually
  verified (not just planned).
- Record results in the Verification section.
- `python scripts/ai-feature.py approve verify`.

STEP 6 - FINAL + LEARN
- Check every Definition of Done item.
- Did this feature change architecture, dependencies, the data model,
  auth/authorization, or integrations? If yes, update the relevant
  docs/architecture/ or docs/kb/ file now, in this same feature.
- `python scripts/ai-feature.py finalize`.
- Generate the PR description from the SSOT README's DoD/summary.

RULE: never jump straight from a request to code. The path is always
EVIDENCE -> UNDERSTAND -> PLAN -> CHANGE -> TEST -> VERIFY -> LEARN.
```
