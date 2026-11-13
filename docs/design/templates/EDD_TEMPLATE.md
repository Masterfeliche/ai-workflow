# Engineering Design Document (EDD) + Architecture Decision Record (ADR) Hybrid

- **Feature / System Key:**
- **Document Version:** MAJOR.MINOR.PATCH; bump MAJOR for breaking schema/API/contract change.
- **Status:** Draft | In Review | Approved | Superseded
- **Owner / Reviewers:**
- **Related Requirements / Feature SSOT:**
- **Target Technology:** selected only after project-specific evaluation; include material versions.

> Technology-independent template. Populate applicable sections and explicitly mark non-applicable
> areas with a reason. Do not invent transactions, services or infrastructure. Trace claims to a
> requirement, decision, experiment or source. All money, if any, requires deterministic precision
> and rounding rules.

## 1. Executive Summary & Phased Delivery Scope

### Objective and technical challenge
Describe the problem, actors, core workflows and business invariants.

### Phased boundary table

| Phase | Scope | Schema / contract future-proofing | Exit criteria |
|---|---|---|---|
| Phase 1 | Immediate minimum safe scope | Nullable/extensible fields or reserved states only when justified | Measurable acceptance criteria |
| Phase 2 | Planned extension | Compatibility and migration approach | Measurable acceptance criteria |
| Phase 3 | Longer-term capability | Compatibility and operational implications | Measurable acceptance criteria |

Explicitly identify fields/status values added now solely to avoid future breaking migrations.
Do not add speculative columns or states without a documented use case.

## 2. System Topology & Integration Boundaries

Provide a Mermaid flowchart with clients, gateways/BFFs where applicable, domain components,
datastores, shared libraries, outbox/bus and downstream systems where they exist.

Label each edge as synchronous (protocol, timeout, retry/circuit-breaker policy), asynchronous
(outbox/event/consumer) or polling/eventual consistency. Do not force microservices or a message bus.

## 3. Data Architecture & Entity Modeling

Provide an ER diagram when relational entities are relevant. For each persistence object specify
columns/fields, types, nullability, defaults, key/relationship constraints, indexes and justification,
retention/archive/delete strategy, migration and rollback plan.

Specify snapshot rules for business values that must not drift after submission where applicable.
Store source identifiers/versions alongside immutable snapshots. Money calculations, where relevant,
must be deterministic and side-effect free, with documented decimal precision and rounding policy.

## 4. State Machines, Workflows & Concurrency Control

Separate record lifecycle, workflow orchestration and operational domain state where these concepts
exist. Include state diagrams, legal transitions, guards, invariants and terminal states.

Specify optimistic concurrency, distributed locking and idempotency only where needed. Define lock
key, timeout, duplicate-submission protection and race-condition tests.

## 5. Architectural Decision Records

Use the companion ADR template for each consequential choice. Include consistency model,
transaction strategy, calculation placement, data/storage, currency/precision, integration,
deployment and security decisions when applicable. Alternatives must be credible and rejection
reasons concrete.

## 6. Distributed Transactions, Failure Modes & Resilience

Identify transaction boundaries and classify each workflow as local ACID, asynchronous/outbox,
saga/compensation or no distributed transaction required. Define failure matrix, retry policy,
dead-letter/reconciliation behavior, idempotent consumer and compensation/reversal where applicable.

Include sequence diagrams for critical failure paths. Do not introduce 2PC, sagas or outbox simply
because a generic template mentions them.

## 7. Discovery Spikes & Verification Checklist

Use actionable checks only:

- [ ] (verify): capability / constraint, evidence required and impact if false.

Include integration contract stability, vendor SLAs, access/security assumptions, performance,
migration and operational unknowns relevant to this design.

## 8. Non-Functional Requirements (NFRs) & Telemetry

State measurable targets for latency, throughput, payload, query cost, availability, recovery,
security, accessibility and cost where relevant.

Specify structured log fields, traces, metrics and concrete alerts. Targets must be justified by
expected workload or product needs, not copied from unrelated examples.

## 9. Code & Implementation Traceability

Map components to realistic repository paths and distinguish existing from proposed files.
List migration, domain, application, infrastructure, worker, integration/contract, unit, load and
chaos-test locations as applicable.

Identify pure deterministic functions, invariants and critical branches requiring exhaustive or
property-based tests. Map design elements to feature tasks and acceptance criteria.

## 10. ADR Register and Approval

| ADR | Decision | Status | Consequence / superseded by |
|---|---|---|---|

Record design reviewers, unresolved risks, human approvals and the commit/document revision approved.

## 11. Change, Migration and Rollback Strategy

Describe expand/contract migrations, compatibility window, deployment ordering, data backfill,
feature flags, rollback constraints and recovery. Mark not applicable with rationale when no
migration or operational rollout is involved.

## 12. Design Validation Evidence

Link prototypes, spikes, benchmarks, threat analysis, contract tests, load tests, failure tests and
review records. Distinguish planned evidence from completed evidence.
