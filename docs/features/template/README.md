# Feature: {{ticket_id}} - {{summary}}

> Single Source of Truth for this feature. One state file per ticket.
> Phases: intelligence -> analysis -> plan -> execute -> verify -> final.
> Do not skip a section -- `ai-feature approve <phase>` checks it is filled in.

## 0. Codebase Intelligence Snapshot

**Repository revision used**:
**Intelligence status at start** (ready / refreshed / targeted review):
**Relevant architecture docs consulted**:
-

**Relevant technology** (unfamiliar tech only -- see Technology Learning Bridge below):
-

---

## 1. Feature Analysis

**Execution Path** (entry point -> ... -> response, actual files/symbols):
-

**Affected Files**:
-

**Dependencies** (modules/packages this touches or relies on):
-

**Data Impact** (schema, migrations, stored state):
-

**Security Impact** (auth, authorization, tenancy, sensitive data):
-

**Integration Impact** (external systems, webhooks, events):
-

**Test Impact** (existing tests affected, new tests required):
-

**Blast Radius** (Low / Medium / High / Critical, with direct + indirect impact):
-

**Risks**:
-

**Assumptions**:
-

**Unknowns**:
-

**Jira Tasks**:
| Key | Summary |
|-----|---------|
| TASK-1 | |

---

## 2. Technology Learning Bridge

_Only fill in for technology that is unfamiliar to the implementer. Skip if none._

| Technology | Where Used Here | Why It's Used Here | Minimum Knowledge Needed |
|------------|------------------|---------------------|---------------------------|
| | | | |

---

## 3. Implementation Plan

| Subtask Key | Summary | Acceptance Criteria | Est. | Status |
|-------------|---------|----------------------|------|--------|
| SUB-1.1 | | | | [ ] |

---

## 4. Execution Log

- [ ] SUB-1.1: (commit hash, test result)

---

## 5. Verification

**Regression run**:
**Security verification** (if security impact was non-empty above):
**Acceptance criteria met**:

---

## 6. Definition of Done (DoD)

- [ ] Code is written and passes all local tests/lints
- [ ] Single-sentence commit rule followed for all commits
- [ ] SSOT README is fully updated
- [ ] Regression verified
- [ ] Codebase Intelligence updated if this feature changed architecture, dependencies, data model, auth, or integrations (see Part 18 feedback loop in AGENTS.md)
- [ ] PR description generated from this checklist
