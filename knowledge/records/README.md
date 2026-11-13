# Canonical Knowledge Records

Place curated, versioned JSON knowledge records in this directory.

- Use the schema in `schemas/knowledge-item.schema.json`.
- Every record needs a stable lowercase ID, type, scope, version, lifecycle status,
  provenance, source references and access classification.
- Project/repository/feature/sprint records must include `project_id`.
- Records with `status: approved` must include a named human reviewer and review timestamp.
- Draft and under-review records are not authoritative. They can be included in search only when
  the caller explicitly opts into drafts.
- Records marked `restricted` are excluded from the local index.
- Never add credentials, secrets, personal data or unredacted production data.

Markdown project documents are indexed as under-review reference material. To promote a reusable
concept to approved knowledge, create a curated record with evidence and have it reviewed.
