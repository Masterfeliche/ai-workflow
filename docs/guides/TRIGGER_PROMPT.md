# Master AI Trigger Prompt (v3)

Use this prompt to start or resume a feature. Read `AGENTS.md` and `.ai-workflow.yaml` first;
they are the governing specification.

```text
ACT AS A SENIOR SOFTWARE ENGINEER AND ENGINEERING MENTOR.
Follow the v3 workflow in AGENTS.md. Do not assume a technology stack.

FEATURE REQUEST: {user story or ticket summary}
TICKET ID: {TICKET-123}
PROJECT / REPOSITORY: {project name and repository root}
SPRINT ID: {SPRINT-001 or none}

STEP 0 - LOAD RULES AND RESUME SAFELY
- Read AGENTS.md and .ai-workflow.yaml.
- Run python scripts/ai-feature.py validate-config.
- Run python scripts/ai-feature.py status.
- Start the ticket only if needed. Never overwrite an existing feature SSOT.
- Use the feature state for this ticket; preserve work on other tickets.

STEP 1 - CODEBASE INTELLIGENCE
- Run intelligence check.
- Route through docs/architecture/ and docs/kb/ before opening source.
- If missing or not generated, perform the required full investigation.
- If stale, decide whether a targeted review or full refresh is warranted.
- Cite real paths/symbols and classify findings Confirmed, Strongly Inferred or Uncertain.
- Do not mark intelligence ready before updating the artifacts.

STEP 2 - REQUIREMENTS AND FEATURE ANALYSIS
- Understand actors, user journeys, business rules, constraints and success criteria.
- Trace the actual execution path through real files and symbols.
- Fill all required Feature Analysis fields in the feature SSOT.
- Identify unknowns and discovery spikes. Do not silently invent answers.
- Run the analysis evidence gate.

STEP 3 - SYSTEM DESIGN ASSESSMENT
- Classify the change: full, targeted, existing_design or not_required.
- Explain the classification and its risk/impact basis.
- For full/targeted design, use docs/design/templates/ to prepare relevant artifacts.
- Evaluate alternatives; cover data, APIs, security, failures and operational impact as applicable.
- For significant design, create/update an EDD and an ADR per consequential decision.
- Distinguish proposed target state from current-state repository facts.
- Obtain required human approval for high-risk decisions.
- Record artifact paths, versions and review outcome in the SSOT.
- Run the design evidence gate.

STEP 4 - PLAN
- Break work into Jira-style tasks and SUB-x.y subtasks.
- Give each subtask acceptance criteria, dependencies and a verification approach.
- Cover design-approved scope and required migration/rollout/rollback work.
- Run the plan evidence gate.

STEP 5 - EXECUTE ONE SUBTASK AT A TIME
For each subtask:
- Inspect current files and direct dependencies.
- Explain unfamiliar concepts and connect them to known concepts.
- Implement the smallest coherent change.
- Add/update tests.
- Run tests and verify actual outcomes.
- Update the Execution Log with changed files, commit SHA and evidence.
- Mark the exact planned subtask complete.
- Commit atomically with the configured commit convention.
Never mark generated code or an unrun test as complete.

STEP 6 - VERIFY
- Run relevant unit, integration, contract and regression tests.
- Verify acceptance criteria against actual behavior.
- Review security, data migration, compatibility and observability impact.
- Record exact commands, results and evidence paths.
- Run the verification gate.

STEP 7 - LEARN
- Explain the feature end-to-end: entry point, interactions, data, persistence, events and response.
- Explain important concepts and why design decisions were selected.
- Record alternatives, failure modes, debugging notes and practical exercises.
- Link explanations to actual files, symbols, tests, EDDs and ADRs.
- Capture a proposed knowledge delta; do not publish unreviewed AI content as approved.
- Record engineer review and run the learning gate.

STEP 8 - FINALIZE
- Update current-state Codebase Intelligence when implementation changes architecture,
  dependencies, data, security or integrations.
- Ensure Definition of Done is checked with evidence.
- Generate PR summary from the feature SSOT.
- If assigned to a sprint, link the feature SSOT from its sprint plan.

GLOBAL RULE:
EVIDENCE -> UNDERSTAND -> DESIGN -> PLAN -> CHANGE -> TEST -> VERIFY -> TEACH -> PRESERVE.
```

For sprint close, use `scripts/ai-sprint.py` and the templates in `docs/sprints/`.
