# Universal Engineering Knowledge Model

## Purpose

Define a provider-independent record model for validated engineering knowledge across projects.
This repository defines the model and contracts; it does not ship a hosted knowledge database.

## Scopes

- **global:** reviewed reusable engineering principles and patterns.
- **project:** requirements, domain language, accepted architecture and project constraints.
- **repository:** current codebase structure, symbols, dependencies and technical behavior.
- **feature:** feature-specific implementation and decision knowledge.
- **sprint:** sprint outcomes, learning and validated lessons.
- **learning:** tutorials, concept explanations and exercises.

Scope is part of identity and access control. A global record must not contain confidential project
data or project-specific assumptions presented as universal facts.

## Record fields

Every canonical record includes stable ID, type, scope, project/repository identifiers where
applicable, title, summary, content, semantic version, status, provenance, source references,
relationships, access classification, timestamps, review metadata and content hash.

See `schemas/knowledge-item.schema.json` for the machine-readable contract.

## Provenance and evidence

Source types include source_code, test, adr, edd, requirement, sprint_learning, reviewed_reference
and human_observation. Each source should include a stable path/URI and revision where available.

Label claims as Confirmed, Strongly Inferred, Proposed or Uncertain when that affects correctness.
A proposed design is not evidence that an implementation exists.

## Relationships

Relationships are typed, for example: implements, decided_by, verified_by, depends_on, explains,
supersedes, contradicts, part_of and related_to. Store relationships as data; do not rely on vector
similarity to infer authority.

## Canonical and derived stores

Git-versioned Markdown/JSON documents are canonical for project engineering records. A future
knowledge service may index them in lexical, vector and graph stores. Those indexes are derived,
rebuildable and must retain source IDs, versions, hashes, scopes and access labels.

## Model independence

The knowledge record is model-neutral. Context assembly adapts retrieved records to a model's
context window and tool capabilities without changing the underlying source or authority.
