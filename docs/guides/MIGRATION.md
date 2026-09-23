# Migration: v1.3 -> Unified Workflow v2

## 1. Audit of v1.3 (what was actually implemented)

| Artifact | Documented rule | Actually did | Gap |
|---|---|---|---|
| `AGENTS.md` | 4-phase gated lifecycle (analysis/plan/execute/final), Jira tasks, SSOT | Prose description only | No enforcement mechanism existed anywhere in the repo |
| `.ai-workflow.yaml` | "Configuration-driven behavior" | `scripts/ai-feature.py` never read this file at all | 100% decorative -- changing it changed nothing |
| `scripts/ai-feature.py` | Tracks phase/ticket, "auto-provisions feature manifests" | `start`/`status`/`approve`/`reset` only; `approve` just advanced a dict key `{"analysis":"plan","plan":"execute","execute":"final"}` with **no check of anything** | "Approval" was a label change, not a gate -- an agent could call `approve` four times in a row from a freshly-provisioned template and land on `final` with every section still `{{placeholder}}` |
| Feature template | Jira-style tasks/subtasks, Execution Log, DoD | Present as a Markdown skeleton | Nothing forced it to be filled in before advancing |
| `.git/hooks/commit-msg` | "Cross-platform commit hook" enforcing single-sentence rule | Real, working Python hook -- format, length, punctuation all checked | Correct, but **not installed automatically** on clone (`.git/hooks` isn't versioned) and not itself tracked in the repo as a file, so it could be lost/edited with no diff history |
| `docs/architecture`, `docs/kb` | Implied by `AGENTS.md` repo structure | Empty `.gitkeep` directories | No codebase intelligence existed; nothing prevented an agent from planning against a codebase it had never actually inspected |

**State machine as actually implemented**: `idle -> analysis -> plan -> execute -> final`, one unconditional edge per node, no guard conditions, no way to go backward, no way to represent "intelligence" or "verify," no persisted evidence of *why* a transition happened. It was a labeled counter, not a workflow engine.

## 2. What was preserved (Preservation Matrix)

| Capability | Preserve | Modify | Remove | Reason |
|---|---|---|---|---|
| Feature SSOT | ✅ | expanded sections | | Good idea, just needed real content requirements |
| Jira-style tasks/subtasks | ✅ | | | Works, keep the `SUB-x.y` convention |
| Analysis-first | ✅ | now evidence-gated | | The *principle* was right, the *enforcement* was missing |
| State management script | | ✅ rewritten | | Kept `start/status/approve/reset`, added the commands needed for the real lifecycle |
| Commit hook | ✅ | now installed via script, source tracked in `scripts/commit-msg.py` | | Logic was already correct |
| Cross-platform support | ✅ | | | `pathlib` + stdlib-only was already right, kept it (no PyYAML added) |
| Execution Log | ✅ | | | Kept, now a gate checks it has entries |
| DoD | ✅ | added intelligence-update item | | Kept, now a gate checks every box is ticked |
| Codebase Intelligence | | | | did not exist -- added |
| Learning Bridge | | | | did not exist -- added (per-feature, in SSOT) |
| Change Impact / Blast Radius | | | | did not exist -- added to Feature Analysis |

## 3. What changed and why

- **State machine gained states and real guards.** `intelligence` is now a
  first-class phase before `analysis`; `verify` is now distinct from
  `execute` (so "the code compiles" and "the code was actually verified
  against regressions" aren't conflated). Every `approve` call now runs an
  evidence check against the SSOT file before mutating state -- see
  `scripts/ai-feature.py: check_*_evidence`.
- **`.ai-workflow.yaml` now maps 1:1 to what the script reads/enforces**
  (commit rule constants, required analysis sections, artifact paths). It
  is documentation of runtime behavior, not aspirational config -- if a key
  here stops corresponding to an actual check, that's a bug to fix, not an
  acceptable drift.
- **Codebase Intelligence added as a separate persistent layer**
  (`docs/architecture/`, `docs/kb/`) distinct from any one feature's SSOT,
  so analysis starts from an evidence-based model of the repo instead of a
  fresh guess every time. Freshness is tracked mechanically (file
  existence + git revision comparison) -- explicitly documented as a
  proxy, not a semantic guarantee.
- **Evidence gates are real but honest about their limits.** They check
  that sections are non-empty and template placeholders are gone; they do
  **not** verify the analysis is *correct*. That remains a human/AI review
  responsibility, called out explicitly in `AGENTS.md` Part 6 so nobody
  mistakes "gate passed" for "content verified."
- **Git hook installation is now explicit and versioned.** The hook logic
  lives in `scripts/commit-msg.py` (tracked, diffable); `.git/hooks/commit-msg`
  is a copy installed by `scripts/install-hooks.py`, run once per clone.

## 4. Migration steps for an existing v1.3 checkout

1. Pull the updated `AGENTS.md`, `.ai-workflow.yaml`, `scripts/ai-feature.py`,
   `docs/features/template/README.md`, and the new `docs/architecture/`,
   `docs/kb/`, `docs/guides/` files.
2. Run `python scripts/install-hooks.py` (hooks aren't versioned, so this
   is required even if you had the old hook installed).
3. Any in-flight feature under `docs/features/<TICKET-ID>/README.md`
   written against the v1.3 template keeps working as a document, but its
   phase in `.ai-workflow-state.json` predates the new `intelligence` and
   `verify` states. Run `python scripts/ai-feature.py status`; if phase is
   `analysis`, `plan`, `execute`, or `final`, migrate the SSOT manually to
   the new section headings (Feature Analysis subsections, Verification)
   before the next `approve` call, since the evidence checkers look for the
   new headings.
4. New features: use `python scripts/ai-feature.py start <TICKET-ID>` as
   before -- it now provisions from the v2 template and starts in
   `intelligence` phase instead of `analysis`.
5. The old v1.3 files are archived at
   [docs/guides/legacy-v1.3/](legacy-v1.3/) for reference; they are inert
   (not read by any script).

## 5. Known limitations (documented, not hidden)

- Evidence gates are text-presence checks, not semantic validation. An
  agent can still write a shallow one-line "analysis" that technically
  passes the gate. The gate stops *phase-skipping*, not *bad analysis*.
- Intelligence freshness is revision-pointer based; it can report STALE on
  a commit that didn't actually touch architecture, or (less likely) miss
  a change that did if the artifact files happen to exist but weren't
  actually updated to reflect it. Judgment is still required, as stated in
  `AGENTS.md` Section 3.
- The commit-msg hook only validates the first line of the message; it
  does not (and by design of "single sentence" need not) inspect a commit
  body.
