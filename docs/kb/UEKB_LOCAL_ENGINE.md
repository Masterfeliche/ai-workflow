# UEKB Local Retrieval Engine

## What is implemented

`scripts/uekb.py` builds and queries a local, rebuildable SQLite search index from canonical
engineering documents and curated JSON knowledge records.

The canonical sources remain in Git:

- Markdown: project README, AGENTS instructions and configured documentation directories.
- Curated JSON: `knowledge/records/*.json`, validated using `schemas/knowledge-item.schema.json`.

The SQLite file is a derived cache at `.ai-workflow/cache/knowledge.sqlite3`. It is ignored by Git
and can be deleted/rebuilt at any time.

## Quick start

Run from the repository root:

```bash
python scripts/uekb.py index --project-id my-project
python scripts/uekb.py status
python scripts/uekb.py search "system design architecture"
python scripts/uekb.py search "ADR idempotency" --format json
python scripts/uekb.py get <knowledge-id>
python scripts/uekb.py context "how does feature execution work" --max-chars 12000
python scripts/uekb.py context "payment failure handling" --format json --output .ai-workflow/payment-context.json
```

Use `--source path/to/docs` to add a repository-local Markdown source directory for one indexing
run. Use `--root /path/to/repository` before the subcommand to index another checkout.

## Indexing behavior

- Configured Markdown sources are chunked by headings and bounded character size.
- Templates, legacy guides, generated caches, common dependency/build directories and symlinks are
  excluded.
- Files larger than 1 MB and files matching conservative credential-detection patterns are skipped
  with a warning.
- Curated JSON records are schema-validated before indexing.
- Restricted records are excluded.
- Project/repository documents are indexed as `under_review`, confidence `uncertain`. This is
  intentional: ingestion does not prove that a document is correct or approved.
- Draft records are excluded from normal search unless `--include-drafts` is supplied.
- Deprecated/superseded records are excluded unless the search option explicitly includes them.
- Index rebuild uses a temporary database and atomic replacement. The canonical documents are never
  modified by indexing.

## Retrieval behavior

SQLite FTS5 is used when available, with a built-in SQLite LIKE fallback. This release implements
lexical retrieval only. It does not claim vector embeddings, semantic search, reranking models or a
knowledge graph. These can be added behind the same retrieval contract after a benchmark and
technology evaluation.

Search is restricted to global records plus the active project by default. Records marked restricted
are never returned by this local CLI. This is a local, single-user tool: the local operating-system
user is trusted. It is not a security boundary for multiple users or tenants. A future REST/MCP
service must authenticate the caller and enforce project/tenant permissions before querying or
assembling context.

## Context packages

The `context` command emits Markdown or JSON with:

- project and repository revision;
- record ID, type, scope, status, confidence and version;
- source paths/URIs and source revision;
- content and related source references.

Only records explicitly marked Approved are labeled authoritative. Markdown-ingested records are
reference-only until a human reviews and promotes a curated JSON record.

## Operational limits

- The index is local to one checkout/project and is not shared across machines automatically.
- No HTTP server, REST endpoint or MCP server is shipped by this CLI.
- Do not index secrets or sensitive production/customer data.
- For multi-project or multi-tenant use, implement a service with authenticated identities, access
  controls, audit logging, retention policy and permission-filter tests before exposing the index.
