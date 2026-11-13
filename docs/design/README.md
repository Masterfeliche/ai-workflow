# System Design and Architecture Documents

This directory contains **target-state** design records. It is separate from
`docs/architecture/`, which describes the implementation that currently exists.

## Design workflow

1. Understand requirements and current-state constraints.
2. Classify design depth: Full, Targeted, Existing Design Reuse or Not Required.
3. Model the domain and system boundaries.
4. Produce an HLD and only the LLD/diagrams needed to implement safely.
5. Generate an EDD for significant features or subsystems.
6. Record consequential choices in ADRs.
7. Review security, data, failure, migration, operational and NFR implications.
8. Obtain required approval before implementation.
9. Update design records when implementation reveals a necessary change.

## Document ownership

| Document | Purpose | Typical scope |
|---|---|---|
| HLD | System context, containers, major components and interactions | Product/system |
| LLD | Internal component behavior, interfaces, algorithms and state | Module/feature |
| EDD | Implementation-ready design specification | Significant feature/subsystem |
| ADR | One significant architecture decision and its consequences | Decision |
| Architecture review | Independent challenge and approval record | Proposed design |

## Technology neutrality

Templates contain no predetermined language, framework, database, queue, cloud provider or AI model.
Select technology only after requirements, constraints, existing capabilities and trade-offs are known.

## Status and versioning

Design records declare status, owner, version, reviewers, dates and related feature keys.
Accepted documents change through reviewed revisions. An accepted ADR is never silently edited to
erase the historical decision; create a superseding ADR where the decision changes.

## Applicability

Not every feature requires every diagram or document. Record why an artifact is applicable or
not applicable. A trivial change may reuse an approved design or select Not Required with a
concrete rationale. High-risk or cross-boundary changes require deeper review.
