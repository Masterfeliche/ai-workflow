# Context Retrieval Discipline (reference)

How the agent should retrieve repository context during Intelligence,
Analysis, and Execution -- so investigation stays *sufficient*, not
*exhaustive*. Complements
[CODEBASE_INTELLIGENCE_ENGINE.md](CODEBASE_INTELLIGENCE_ENGINE.md) (which
governs *what* to document) and [TRIGGER_PROMPT.md](TRIGGER_PROMPT.md)
Steps 1-2 (which govern *when* this applies). This is behavioral guidance
for the agent, not a mechanical gate -- nothing in `scripts/ai-feature.py`
checks retrieval efficiency, the same way nothing checks analysis
correctness (see AGENTS.md Part 6).

## Operating principle

Optimize for **minimum sufficient context**, not minimum context. Retrieving
too little produces wrong conclusions; retrieving everything produces slow,
expensive ones that are no more correct. Stop as soon as the question is
answered, not when files run out.

## Route before exploring

For any request, try to answer these from existing intelligence
(`docs/architecture/`, `docs/kb/`, the feature's own SSOT) before opening
source files:

1. What subsystem/domain is this?
2. What entry point is likely involved?
3. What does the architecture/KB docs already say about this area?
4. What's genuinely unknown that only source inspection can resolve?

If 1-3 already answer the question -- e.g. `SECURITY_ARCHITECTURE.md`
already states "JWT auth lives in `auth/dependencies.py`" -- don't re-derive
that by reading the whole auth subsystem for an unrelated UI change.

## Task-size routing

Match investigation depth to change size. This is what keeps a one-file bug
fix from requiring a full architecture re-read (see the "Scenario 8" note in
[MIGRATION.md](MIGRATION.md)'s known limitations):

| Size | Examples | Depth |
|---|---|---|
| Small | copy/text change, isolated UI tweak, config value, simple bug fix | The specific file and function -- nothing else |
| Medium | new endpoint, business rule, DB field, component interaction | Feature trace + direct dependencies + their tests |
| Large | auth redesign, payment flow, migration, architectural refactor | Full targeted (or full) Intelligence review + change impact |

Never spend Large-task retrieval budget on a Small task.

## Three retrieval levels

1. **Metadata** -- filenames, directory structure, manifests, imports,
   routes. Enough to locate the subsystem. Grep/Glob, not full reads.
2. **Targeted context** -- the specific file(s), function(s), direct
   dependencies, and directly relevant tests. Most tasks stop here.
3. **Deep investigation** -- only for architectural uncertainty,
   security-sensitive changes, migrations, or genuinely unexplained
   behavior. Don't default here.

## Context budget

For anything beyond a Small task, state explicitly before retrieving
(this can live in scratch/task notes, not necessarily the SSOT):

```text
Goal:      what must be understood
Known:     what's already established (intelligence docs, earlier in this task)
Unknown:   what retrieval must resolve
Evidence:  what's sufficient to resolve it
Stop when: <condition>
```

Stop once every Unknown has evidence -- not because more files exist to read.

## The context packet is the SSOT's Feature Analysis section

There is no separate "context packet" artifact to maintain. The Feature
Analysis section already written during the Analysis phase (Execution Path,
Affected Files, Dependencies, Data/Security/Integration/Test Impact, Blast
Radius, Risks, Assumptions, Unknowns) *is* the packet. Plan, Execute, and
Verify should work from that section rather than re-reading the repository
from scratch at each phase.

## Phase-specific scope

Each phase reads only what it needs:

| Phase | Reads |
|---|---|
| Intelligence | repo structure, technology map, relevant architecture doc(s) |
| Analysis | the above + execution path, dependencies, data/security/test impact |
| Plan | the Feature Analysis section already written -- not raw source again |
| Execute | current subtask + its affected files + its tests |
| Verify | changed files (git diff) + acceptance criteria + tests + security impact |

## Change-aware retrieval

When there's a diff to work from (mid-execution, or reviewing prior work),
prioritize: changed files -> their direct dependencies -> their tests ->
their callers. Don't scan untouched areas just because they're nearby.

## Stop conditions

Stop investigating once: the execution path is understood, affected files
are identified, dependencies are known, security/data impact is understood,
relevant tests are identified, and every listed Unknown has evidence.
Re-reading a file already read this task is justified only if: it changed,
the earlier read was insufficient, or the task moved into a new execution
path through it.

## Anti-pattern

```text
READ EVERYTHING -> HOPE THE ANSWER IS SOMEWHERE
```

is not a retrieval strategy. The loop is always:

```text
MAP -> ROUTE -> RETRIEVE -> TRACE -> STOP
```
