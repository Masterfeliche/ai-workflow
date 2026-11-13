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
- Index engineering documents and curated knowledge records in a local SQLite search cache.
- Assemble provider-neutral, source-cited context for compatible LLM clients.

The local UEKB CLI is implemented. A hosted REST service, MCP server, vector search backend and
multi-tenant authorization service are not yet included.

## Quick start

Requirements: Python 3.10+ and Git. No third-party Python packages are required by the CLI.

```bash
git clone https://github.com/Masterfeliche/ai-workflow.git
cd ai-workflow
python scripts/install-hooks.py
python scripts/ai-feature.py validate-config
python scripts/ai-feature.py start DEMO-001
```

## Local knowledge base

Build the local derived index and query it:

```bash
python scripts/uekb.py index --project-id my-project
python scripts/uekb.py status
python scripts/uekb.py search "system design architecture"
python scripts/uekb.py context "how does this feature execute" --max-chars 12000
```

Canonical sources remain in Git-versioned Markdown and JSON. The SQLite index is ignored by Git
and can be rebuilt. Markdown source chunks are marked Under Review; only reviewed canonical
records can be marked Approved. See `docs/kb/UEKB_LOCAL_ENGINE.md`.

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
- `docs/kb/`: project knowledge model, governance, retrieval contract and local UEKB guide.
- `knowledge/records/`: canonical curated JSON knowledge records.
- `schemas/`: machine-readable JSON contracts.
- `scripts/`: dependency-free workflow and UEKB CLI utilities.
- `tests/`: standard-library regression tests.

## Principles

1. Evidence before decisions.
2. Design proportionately; no unnecessary ceremony.
3. Technology follows project needs.
4. Keep current-state and target-state architecture distinct.
5. Capture rationale, not private chain-of-thought.
6. Human-review high-risk decisions and approved knowledge.
7. Git is canonical; indexes are derived.
8. Knowledge retrieval must respect project scope and access controls.

## Validation

```bash
python -m unittest discover -s tests -v
python scripts/ai-feature.py validate-config
python scripts/uekb.py index --project-id ai-workflow
python scripts/uekb.py search "system design"
```
