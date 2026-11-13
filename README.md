# AI Engineering Workflow

**Framework version: 3.0.0**

A technology-independent, evidence-oriented workflow for AI-assisted software engineering.

V3 preserves the v2 feature SSOT and Codebase Intelligence approach, and adds proportionate
System Design Intelligence, EDD/ADR governance, sprint-level developer learning and a governed
knowledge model.

## What it does

- Understand the existing repository before changing it.
- Translate requirements into proportionate system designs.
- Record significant architectural decisions and implementation-ready EDDs.
- Plan and execute small, verifiable feature subtasks.
- Generate sprint learning artifacts grounded in code, tests and approved decisions.
- Maintain project knowledge in versioned, reviewable source documents.
- Define provider-independent REST, MCP and export contracts for future knowledge services.

The repository is a workflow specification and local CLI/tooling foundation. It is **not** a hosted
multi-agent orchestrator or a deployed vector/graph knowledge service.

## Quick start

Requirements: Python 3.10+ and Git. No third-party Python packages are required by the CLI.

```bash
git clone https://github.com/Masterfeliche/ai-workflow.git
cd ai-workflow
python scripts/install-hooks.py
python scripts/ai-feature.py validate-config
python scripts/ai-feature.py start DEMO-001
```

Follow `AGENTS.md` and `docs/guides/TRIGGER_PROMPT.md` for the full workflow.

## Core lifecycle

```text
INTELLIGENCE -> ANALYSIS -> DESIGN -> PLAN -> EXECUTE -> VERIFY -> LEARN -> FINAL
```

A design assessment is required for each feature. It may be Full, Targeted, Existing Design Reuse
or Not Required, with a reason. Sprint learning is aggregated separately from feature execution.

## Documentation map

- `AGENTS.md`: governing instructions and lifecycle.
- `.ai-workflow.yaml`: runtime policy configuration.
- `docs/architecture/`: evidence-based current-state repository intelligence.
- `docs/design/`: target-state HLD, LLD, EDD and ADR templates.
- `docs/features/`: feature SSOT template and feature records.
- `docs/sprints/`: sprint plan, summary and learning-pack templates.
- `docs/kb/`: project knowledge model, governance and retrieval contract.
- `schemas/`: machine-readable JSON contracts.
- `scripts/`: dependency-free CLI utilities.
- `tests/`: standard-library regression tests.

## Principles

1. Evidence before decisions.
2. Design proportionately; no unnecessary ceremony.
3. Technology follows project needs.
4. Keep current-state and target-state architecture distinct.
5. Capture rationale, not private chain-of-thought.
6. Human-review high-risk decisions.
7. Git is canonical; indexes are derived.
8. Knowledge retrieval must respect project scope and access controls.

## Validation

```bash
python -m unittest discover -s tests -v
python scripts/ai-feature.py validate-config
```
