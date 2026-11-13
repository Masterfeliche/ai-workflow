# Architecture and System Design Review

- **Review key / date:**
- **Project / feature:**
- **EDD/HLD/LLD revision:**
- **Codebase revision:**
- **Reviewers:**
- **Outcome:** Approved | Approved with conditions | Rework required

## 1. Requirements fit

Are business objectives, actors, domain invariants, functional requirements and NFRs addressed?

## 2. Architecture boundaries

Are responsibilities, ownership, interfaces, coupling and trust boundaries explicit? Is the design
the simplest suitable architecture for the actual constraints?

## 3. Data and consistency

Are data ownership, lifecycle, migration, consistency, concurrency and integrity addressed?

## 4. Security and privacy

Are authentication, authorization, tenant isolation, secrets, sensitive data, threat scenarios and
audit needs covered?

## 5. Resilience and operations

Are timeouts, retries, failure isolation, recovery, observability, deployment and rollback addressed?

## 6. Performance and cost

Are workload assumptions explicit? Are bottlenecks and capacity assumptions measurable and
validated at a proportionate level?

## 7. Alternatives and reversibility

Were viable alternatives evaluated? Are high-cost or difficult-to-reverse choices justified?

## 8. Learning and maintainability

Can an engineer trace the design to requirements, code ownership, tests and operational behavior?

## 9. Findings

| Severity | Finding | Evidence | Required action | Owner | Status |
|---|---|---|---|---|---|

## 10. Approval conditions

List conditions that must be satisfied before implementation or release. High-risk decisions
require explicit human approval and a record of who approved which revision.
