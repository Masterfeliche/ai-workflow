# Architecture Governance

## 1. Two architecture views

This repository intentionally separates two document sets:

- **As-built/current state:** `docs/architecture/` records what source code, configuration,
  infrastructure and runtime evidence show today.
- **Approved target state:** `docs/design/` records the design approved for future implementation.

Neither view silently overwrites the other.

## 2. Authority order

1. Approved business requirements and domain invariants establish what must be achieved.
2. Accepted EDD/HLD/LLD and ADRs establish the approved target design.
3. Feature SSOTs translate approved design into implementation scope and evidence.
4. Source code, tests, deployment configuration and runtime telemetry establish what exists.
5. Current-state intelligence is updated from implementation evidence.

When documents conflict, stop and record the conflict. Do not choose whichever document is newest
without checking approval, scope and supersession.

## 3. Architecture drift categories

| Category | Definition | Treatment |
|---|---|---|
| Approved evolution | Implementation differs from an older design under an accepted replacement ADR | Update links and mark old decision superseded |
| Undocumented drift | Code or infrastructure differs from accepted design without approved rationale | Record finding and propose corrective action or ADR |
| Documentation drift | Actual implementation changed but current-state docs were not updated | Update as-built intelligence |
| Intentional deviation | Temporary implementation exception with owner, reason and expiry/review date | Track as an explicit exception |
| Obsolete design | Requirements or constraints changed so target design is no longer suitable | Reassess and issue revised EDD/ADR |

## 4. Review procedure

1. Select approved EDD/ADR revisions and source commit under review.
2. Inspect code, dependencies, schemas, APIs, integrations, infrastructure, tests and relevant
   operational evidence.
3. Compare each material design invariant with implementation evidence.
4. Separate approved changes from undocumented deviations.
5. Record severity, affected paths, impact, recommended action and verification test.
6. Propose document changes. Do not modify approved decisions without review.
7. Re-run the review after corrective work and preserve the evidence.

## 5. Severity

- **Critical:** active or imminent risk of data loss, security compromise, financial corruption or
  severe service failure.
- **High:** material violation of an important invariant, trust boundary, contract or availability
  requirement.
- **Medium:** maintainability, observability, performance or compatibility weakness with bounded
  impact.
- **Low:** documentation, consistency or minor design deviation with limited operational impact.

## 6. Approval and traceability

Record repository revision, EDD/ADR revisions, reviewer, timestamp, findings and review outcome.
High-risk exceptions require human approval. A clean review means no drift was found within the
reviewed scope; it does not prove the entire system is defect-free.
