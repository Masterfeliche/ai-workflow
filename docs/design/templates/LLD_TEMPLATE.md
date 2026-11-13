# Low-Level Design (LLD)

- **System / Module:**
- **Feature Key:**
- **Version / Status:**
- **Related HLD / EDD / ADR:**
- **Owner / Reviewers:**

## 1. Responsibility and boundaries

State what this module owns and explicitly what it does not own.

## 2. Interfaces and contracts

Define public interfaces, inputs, outputs, errors, validation, authentication/authorization and
compatibility expectations. Link API/event schemas rather than duplicating them.

## 3. Internal components

Describe modules, classes, functions or equivalent constructs only as appropriate to the selected
technology. Include dependency direction and ownership.

## 4. Data structures and persistence

Define entities, constraints, indexes, transactions, data access patterns, migrations and
consistency requirements. Identify immutable snapshots and audit needs where applicable.

## 5. Algorithms and business rules

Specify deterministic rules, edge cases, ordering, rounding/precision where relevant and
side-effect boundaries.

## 6. State and concurrency

Define lifecycle states, valid transitions, guards, optimistic concurrency, idempotency and locking
only where needed.

## 7. Execution sequence

Include sequence/activity diagrams for normal and critical failure flows.

## 8. Error handling and resilience

Define timeouts, retries, backoff, circuit breaking, deduplication, compensation and recovery.

## 9. Security and privacy

Define trust boundaries, input validation, authorization enforcement, secrets handling, logging
redaction and data access rules.

## 10. Observability

Define logs, traces, metrics, alerts and correlation identifiers needed to operate the module.

## 11. Testing strategy

Specify unit, integration, contract, property-based, security, performance and failure tests as
applicable. Map tests to requirements and invariants.

## 12. Implementation traceability

Map components to actual or proposed repository paths. Mark proposed paths as proposed, not
confirmed. Link feature tasks and acceptance criteria.

## 13. Open questions and approval

Record unresolved questions, discovery spikes, reviewers and approval.
