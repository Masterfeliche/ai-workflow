# Agentic Workflow Specification (v2)

Unifies the v1.3 Jira-aligned state workflow with a Codebase Intelligence
layer. Supersedes v1.3 (archived at [docs/guides/legacy-v1.3](docs/guides/legacy-v1.3/)).

## 1. Core Mandates

### 1.1 Single Source of Truth (SSOT)
Each feature has exactly ONE state file: `docs/features/<TICKET-ID>/README.md`.
It holds human-readable analysis, plan, execution log, verification, and DoD.

### 1.2 Codebase Intelligence Is a Separate Layer
Persistent, repository-wide knowledge lives in `docs/architecture/` and
`docs/kb/`, not inside the feature SSOT. The SSOT only references it (see
`.ai-workflow.yaml: intelligence.artifacts`) and records a short per-feature
snapshot. Do not duplicate architecture docs into every ticket.

### 1.3 Evidence Before Progression
No phase may be approved by declaration alone. `scripts/ai-feature.py approve
<phase>` inspects the SSOT README for that phase's required sections and
refuses to advance if they are empty or still contain `{{placeholder}}`
tokens. This is mechanical text-presence checking, not correctness
verification -- a human/AI reviewer is still responsible for judging whether
the content is actually right (see Part 6, Evidence Gates below).

### 1.4 Jira-Style Task Management
Work is broken into Jira-style Tasks (`TASK-N`) and Subtasks (`SUB-N.M`)
inside the SSOT `Implementation Plan` section.

### 1.5 Single-Sentence Commit Rule
Commits are atomic and follow (enforced by `.git/hooks/commit-msg`):
- **Format**: `type(scope): description` (Conventional Commits).
- **Sentence**: exactly one sentence.
- **Imperative**: starts with a verb in imperative mood.
- **Length**: max 72 characters.
- **Punctuation**: no periods, semicolons, or colons in the description.

### 1.6 Analysis-First Protocol
No code changes until Intelligence, Analysis, and Plan phases are approved
(`ai-feature approve intelligence|analysis|plan`... intelligence uses
`ai-feature intelligence check|refresh|targeted` instead of `approve`, see
Part 2).

### 1.7 One Subtask at a Time
Execution is: Inspect -> Implement -> Test -> Verify -> update Execution Log
-> atomic commit -> next subtask. Never batch multiple subtasks into one
uncontrolled change.

### 1.8 Minimum Sufficient Context
Retrieve the smallest amount of repository context sufficient for a safe
engineering decision -- not the smallest amount possible, and not the whole
repository "to be safe." Route to existing `docs/architecture/`/`docs/kb/`
knowledge before opening source files, match investigation depth to task
size, and stop once the Feature Analysis section's questions are answered.
See [docs/guides/CONTEXT_RETRIEVAL.md](docs/guides/CONTEXT_RETRIEVAL.md).
This is retrieval behavior, not a mechanical gate -- nothing in
`ai-feature.py` checks it, the same way nothing checks analysis correctness.

---

## 2. The Workflow Lifecycle

```text
IDLE
  |
INTELLIGENCE          <- ai-feature start <TICKET>, then intelligence check
  |    (ready / refresh_required / stale -> refresh or targeted review)
ANALYSIS               <- ai-feature analyze
  |    (Feature Analysis section filled: execution path, affected files,
  |     dependencies, data/security/integration/test impact, blast radius,
  |     risks, assumptions, unknowns)
  v  ai-feature approve analysis
PLAN
  |    (Implementation Plan section filled with SUB-x.y subtasks)
  v  ai-feature approve plan
EXECUTE
  |    (per subtask: next-subtask -> code+test -> complete-subtask -> commit)
  v  ai-feature approve execute
VERIFY
  |    (regression run, DoD reviewed)
  v  ai-feature approve verify
FINAL
     (ai-feature finalize: DoD fully checked, PR description generated)
```

### Phase 0: Intelligence
Check whether existing Codebase Intelligence (`docs/architecture/`,
`docs/kb/`) is READY, STALE, or REFRESH REQUIRED for the area this feature
touches. Do a full refresh only for the triggers in
`.ai-workflow.yaml: intelligence.policy.full_refresh_triggers`; otherwise do
a targeted review of just the affected module and record it in the SSOT
Codebase Intelligence Snapshot section.

### Phase 1: Analysis
Trace the actual execution path for this feature through real files/symbols.
Fill in the Feature Analysis section (execution path, affected files,
dependencies, data/security/integration/test impact, blast radius, risks,
assumptions, unknowns) in the SSOT README.

### Phase 2: Planning
Break the feature into Jira-style Tasks/Subtasks in the Implementation Plan
section, each with acceptance criteria.

### Phase 3: Execution
One subtask at a time: code, test, verify, update the Execution Log, commit.

### Phase 4: Verify
Run regression. Confirm acceptance criteria and security impact (if any)
were actually verified, not just planned.

### Phase 5: Final
Confirm every Definition of Done item is checked, then generate the PR
description from the SSOT README.

---

## 3. Codebase Intelligence

Codebase Intelligence is persistent, repository-wide knowledge, separate
from any one feature. It answers "how does this system actually work" so
that Analysis does not start from a guess.

- `docs/architecture/CODEBASE_INTELLIGENCE.md` -- system mental model, entry
  points, component map, navigation.
- `docs/architecture/SYSTEM_ARCHITECTURE.md` -- architecture pattern,
  execution model, diagrams.
- `docs/architecture/DATA_ARCHITECTURE.md` -- data model, storage, state.
- `docs/architecture/SECURITY_ARCHITECTURE.md` -- auth, authorization,
  tenancy, security controls.
- `docs/kb/TECHNOLOGY_MAP.md` -- stack, dependencies, learning bridge.
- `docs/kb/DEVELOPMENT_GUIDE.md` -- build/test/run commands actually
  supported by this repo.
- `docs/kb/GOTCHAS.md` -- non-obvious behavior discovered while working here.

Every conclusion in these files must be tagged **Confirmed**, **Strongly
Inferred**, or **Uncertain**, per the evidence rules in
[docs/guides/CODEBASE_INTELLIGENCE_ENGINE.md](docs/guides/CODEBASE_INTELLIGENCE_ENGINE.md).
Never invent files, routes, dependencies, or architecture that isn't there.

### Freshness
`ai-feature intelligence check` compares the repository revision recorded at
last refresh against current `git rev-parse --short HEAD` and checks the
core artifacts exist. It reports READY, STALE (revision moved), or REFRESH
REQUIRED (artifacts missing). This is a mechanical proxy, not a semantic
diff -- new commits that don't touch architecture will show as STALE even
though nothing meaningful changed; use judgment, do a targeted review
instead of a full one when that's the case, then run
`ai-feature intelligence targeted`.

### Continuous Learning (Feedback Loop)
Before finalizing a feature, check the DoD item: did this change alter
architecture, dependencies, the data model, auth/authorization, or
integrations? If yes, update the relevant `docs/architecture/` or
`docs/kb/` file as part of the same feature (not a separate ticket) and
note it in the Execution Log.

---

## 4. Tooling & Automation

### 4.1 State Management (`scripts/ai-feature.py`)
Stdlib-only Python (no third-party deps), works identically on Windows via
Git for Windows / native Python and on Linux/macOS. Tracks ticket, phase,
intelligence status, current/completed subtasks, approvals, and repository
revision in `.ai-workflow-state.json`. Commands:

```
start <TICKET-ID>          provision SSOT from template, enter intelligence phase
status                      print current state
intelligence check          READY / STALE / REFRESH REQUIRED
intelligence refresh        record a full intelligence refresh
intelligence targeted       record a targeted review
analyze                     intelligence -> analysis (requires intelligence READY)
approve <phase>             evidence-gated transition to the next phase
next-subtask <SUB-KEY>      set current subtask during execute
complete-subtask <SUB-KEY>  mark a subtask done
verify                      confirm in verify phase
finalize                    check DoD, confirm ready to ship
reset                       clear state (does not touch SSOT files)
```

### 4.2 Cross-Platform Commit Hook (`.git/hooks/commit-msg`)
Python-based, enforces the single-sentence commit rule. Not committed to git
by default (hooks live in `.git/`, which is not versioned) -- install it
after cloning with:

```bash
python scripts/install-hooks.py
```

which copies `docs/guides/legacy-v1.3/commit-msg` forward (or the canonical
copy tracked in this repo) into `.git/hooks/commit-msg` and marks it
executable. See Part 22 gap analysis in
[docs/guides/MIGRATION.md](docs/guides/MIGRATION.md) for why this must be an
explicit install step, not silent magic.

---

## 5. Repository Structure

```text
/
├── .ai-workflow.yaml              configuration (matches runtime behavior)
├── AGENTS.md                      this file
├── docs/
│   ├── architecture/               persistent codebase intelligence
│   │   ├── CODEBASE_INTELLIGENCE.md
│   │   ├── SYSTEM_ARCHITECTURE.md
│   │   ├── DATA_ARCHITECTURE.md
│   │   └── SECURITY_ARCHITECTURE.md
│   ├── kb/                         technology & developer knowledge
│   │   ├── TECHNOLOGY_MAP.md
│   │   ├── DEVELOPMENT_GUIDE.md
│   │   └── GOTCHAS.md
│   ├── features/
│   │   ├── template/README.md      feature SSOT template
│   │   └── <TICKET-ID>/README.md   feature SSOT (per ticket)
│   ├── guides/
│   │   ├── TRIGGER_PROMPT.md       master AI trigger prompt
│   │   ├── CODEBASE_INTELLIGENCE_ENGINE.md
│   │   ├── CONTEXT_RETRIEVAL.md    retrieval discipline (Part 1.8)
│   │   ├── MIGRATION.md
│   │   └── legacy-v1.3/            archived v1.3 files
│   └── api/
└── scripts/
    ├── ai-feature.py               state management CLI
    └── install-hooks.py            installs the commit-msg hook
```

---

## 6. Evidence Gates Summary

| Gate | Verifies | How |
|---|---|---|
| Intelligence | Core architecture docs exist and revision is current | `intelligence check` |
| Analysis | All 11 analysis subsections non-empty in SSOT | `approve analysis` |
| Plan | Implementation Plan has at least one filled-in `SUB-x.y` row | `approve plan` |
| Execute | Execution Log has at least one checked entry | `approve execute` |
| Verify | Every DoD checkbox is checked | `approve verify` / `finalize` |

These are presence/shape checks, not correctness checks. They catch "phase
skipped" and "section left as a template placeholder," not "the analysis is
wrong." Correctness remains a human/AI review responsibility -- see
[docs/guides/MIGRATION.md](docs/guides/MIGRATION.md) Part 21 for what is and
isn't automatable here.
