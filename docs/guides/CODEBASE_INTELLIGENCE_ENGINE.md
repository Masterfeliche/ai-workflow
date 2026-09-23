# Codebase Intelligence Engine (reference)

How to build and refresh `docs/architecture/` and `docs/kb/`. Loaded during
Step 1 (Intelligence) of [TRIGGER_PROMPT.md](TRIGGER_PROMPT.md). This is a
compressed operating reference, not the full investigation checklist --
apply the sections that are relevant to the current full-refresh or
targeted-review scope.

## Operating principles

1. **Evidence over assumption.** Every conclusion is **Confirmed** (seen in
   code/config), **Strongly Inferred** (supported by multiple related
   pieces of evidence but not stated outright), or **Uncertain**
   (insufficient evidence -- say what evidence would resolve it).
2. **Never invent** files, routes, dependencies, tables, services, or
   patterns that aren't actually in the repository.
3. **Follow the implementation**, not the framework's defaults. Trace real
   routes -> functions -> services -> repositories -> database, not "this
   framework usually does X."
4. **Reuse, don't rediscover.** If `docs/architecture/*` is READY (see
   `ai-feature intelligence check`), read it instead of re-deriving it.
5. **Scope to what's needed.** A full pass covers the whole repo (only for
   the triggers in `.ai-workflow.yaml: intelligence.policy.full_refresh_triggers`).
   A targeted review covers just the module/area a feature touches.

## What to establish (full pass)

Work through these, writing findings straight into the matching artifact
file. Skip a topic that plainly doesn't apply to this repo (e.g. no
database) rather than inventing content for it.

| Topic | Goes in |
|---|---|
| Repository inventory (apps/services/libs/scripts boundaries), system purpose, entry points, component map, execution model | `CODEBASE_INTELLIGENCE.md` |
| Architecture pattern + evidence, diagrams, separation of concerns, dependency map, critical paths | `SYSTEM_ARCHITECTURE.md` |
| Data model, database/state analysis, state beyond the DB (cache, queue, sessions, storage) | `DATA_ARCHITECTURE.md` |
| Authentication, authorization, tenancy, confirmed protections / potential weaknesses / unknowns | `SECURITY_ARCHITECTURE.md` |
| Technology stack table, dependency table, learning bridge, cross-technology concept mapping | `TECHNOLOGY_MAP.md` |
| Install/run/test/build commands actually supported by the repo, CI/CD pipeline, developer navigation map | `DEVELOPMENT_GUIDE.md` |
| Non-obvious behavior: initialization side effects, env-dependent behavior, legacy workarounds, hidden dependencies | `GOTCHAS.md` |

For each finding worth remembering, keep it auditable: what's the claim,
what's the evidence, what's the confidence.

## Targeted review (most common case)

For a feature entering an already-documented codebase:

1. Read the existing `docs/architecture/*` and `docs/kb/*` relevant to the
   feature's area.
2. Trace the actual execution path for *this* feature specifically (entry
   point -> middleware -> handler -> service -> persistence -> response),
   citing real files/symbols. This trace goes into the feature's own SSOT
   Feature Analysis section, not into the persistent docs.
3. If the trace reveals something the persistent docs got wrong or never
   covered, patch just that section of the relevant `docs/architecture/` or
   `docs/kb/` file. Don't rewrite the whole file.
4. Run `python scripts/ai-feature.py intelligence targeted`.

## Security as cross-cutting, not a checkbox

For any feature with a Security Impact, walk: who can initiate this? which
tenant/org is involved? what permissions are required? what data is
touched? what validation exists? what's logged/audited? Answer from code,
not from what the framework "should" enforce.

## Change impact (blast radius)

Format for the SSOT's Blast Radius field:

```text
Impact: Low / Medium / High / Critical
Direct: <components/files that change>
Indirect: <consumers, dependent modules, background jobs>
Data: <schema/migration impact, or none>
API: <contract changes, or none>
Security: <auth/authz/tenancy impact, or none>
Tests Required: <suites/areas that must run>
```

## Freshness

`ai-feature intelligence check` is a mechanical proxy: it checks the core
artifact files exist and compares the recorded repository revision to
current HEAD. It cannot tell whether a commit that changed the revision
actually invalidated the intelligence content -- use judgment. If the
change was unrelated to architecture (e.g. a copy tweak), a targeted review
of the touched area is enough; don't force a full refresh for every commit.

## Continuous learning

Before finalizing a feature, ask: did this change architecture, add a
dependency, add a module, change the data model, change auth/authz, add an
integration, or reveal a gotcha? If yes, update the matching artifact as
part of the same feature and note it in the Execution Log -- this is what
keeps the intelligence layer from going stale between refreshes.
