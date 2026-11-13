# Knowledge Governance

## Lifecycle

Draft -> UnderReview -> Approved -> Deprecated or Superseded.

- Draft: newly generated or ingested; not authoritative.
- UnderReview: awaiting technical/domain/security review.
- Approved: reviewed and safe to retrieve as authoritative within its scope.
- Deprecated: historically useful but no longer recommended.
- Superseded: replaced by a newer record; retain the replacement link.

## Approval

Approved records require a named reviewer, review date, source evidence and version. Security,
financial, legal, customer or production-impacting content requires the relevant domain owner.
AI agents may propose updates but cannot self-approve them.

## Change management

Use semantic versioning for record content. A change to meaning or contract increments MAJOR;
backward-compatible additions increment MINOR; clarifications/typos increment PATCH. Preserve
previous versions and supersession links.

## Provenance

Capture source type, repository/document URI, commit or version, extraction time and confidence.
External material needs attribution and license/usage review. Do not ingest secrets, private keys,
access tokens, personal data or unredacted production records.

## Access control

Filter by tenant/project/repository permissions before retrieval and before context assembly.
Never retrieve broadly and rely on the model to ignore unauthorized records. Do not share private
project knowledge across projects by default.

## Quality and freshness

Revalidate references against source revisions. Mark missing paths, deleted symbols and outdated
contracts as stale. Do not automatically change an approved claim when source code changes; create
a review proposal.

## Conflict resolution

When records conflict, prefer neither solely by vector score or timestamp. Check scope, status,
source revision, owner and supersession. Return the conflict and request an authoritative decision
when unresolved.

## Audit

Record ingestion, changes, approvals, deprecation, retrieval source IDs and access decisions in the
future service. Keep canonical records in version control.
