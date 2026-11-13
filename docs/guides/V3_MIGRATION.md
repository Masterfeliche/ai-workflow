# V2 to V3 Migration Guide

## Goals

V3 evolves the v2 workflow without discarding feature SSOTs, Codebase Intelligence, Jira-style
subtasks, context retrieval discipline or atomic commit approach.

## What changes

- Feature lifecycle adds Design and Learn gates.
- Target-state design documents live in `docs/design/`; current-state intelligence stays in
  `docs/architecture/`.
- EDD and ADR templates govern material architecture changes.
- Sprint records aggregate multiple feature outcomes and generate learning packs.
- Knowledge records gain scope, provenance, version, status and review governance.
- Feature state is stored per ticket under `.ai-workflow/state/features/`; the legacy active
  state file remains an active-ticket pointer and migration source.
- New CLI tools manage sprint artifacts and validate knowledge deltas.

## Migration steps

1. Back up the repository and commit all v2 work.
2. Pull/merge the v3 branch after review.
3. Run `python scripts/ai-feature.py validate-config`.
4. Install/update the commit hook: `python scripts/install-hooks.py`.
5. Run `python -m unittest discover -s tests -v`.
6. Existing v2 feature SSOTs remain readable. For an in-flight ticket, add the System Design
   Assessment and Learning & Knowledge Capture sections from the v3 template.
7. Existing active state in `.ai-workflow-state.json` is loaded as legacy state and written to
   per-feature state on the next save.
8. If a feature was already at Verify or Final, review actual test evidence and learning notes
   before moving it through the v3 Learn gate. Do not fabricate past learning evidence.
9. Create sprint records only for actual sprint work; do not assign features retroactively without
   an explicit project decision.
10. Start new work with the v3 trigger prompt.

## Compatibility and limitations

- No existing project technology stack is changed or prescribed.
- No runtime service, vector database, graph database or LLM provider is installed by migration.
- CLI evidence checks validate document shape and traceability, not semantic truth.
- Sprint finalization validates local artifacts and linked feature DoD; it does not prove external
  CI, PR merge or production deployment.
- Human approval remains mandatory for high-risk decisions.

## Rollback

Keep the v2 branch and tag before migration. Revert the v3 merge if necessary. Do not delete the
per-feature state directory during rollback; export or retain it as migration evidence.
