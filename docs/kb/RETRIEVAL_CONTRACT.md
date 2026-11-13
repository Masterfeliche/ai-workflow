# Knowledge Retrieval Contract

## Supported interfaces

The canonical service interface is provider-neutral REST/OpenAPI. MCP is an adapter for compatible
AI clients. Markdown/JSON export is the fallback for clients without tool access.

No specific LLM provider, vector store, graph database or hosting platform is required by this contract.

## Core operations

| Operation | Meaning |
|---|---|
| Search | Hybrid search over authorized records |
| Get | Fetch one record by stable ID and version |
| Project context | Retrieve approved project context for a task |
| Related | Follow typed relationships from a record |
| Assemble context | Return a bounded, task-specific evidence package |
| Propose update | Submit a draft knowledge delta for review |

Suggested REST paths:

- `POST /v1/knowledge/search`
- `GET /v1/knowledge/{id}`
- `GET /v1/projects/{project_id}/context`
- `GET /v1/knowledge/{id}/related`
- `POST /v1/context/assemble`
- `POST /v1/knowledge/proposals`

## Search request

Include query, project/repository scope, allowed knowledge types, status policy, revision constraints,
caller identity, access context and result limit. Caller-supplied scope is not authorization; the
service independently enforces access.

## Search response

Return record ID, version, title, summary, scope, status, confidence, source references, relationships,
relevance signals and warnings. Preserve exact code identifiers for lexical retrieval.

## Retrieval strategy

Use lexical search for exact symbols, paths, errors, identifiers and ADR IDs. Use semantic search
for concepts and natural-language questions. Apply metadata and permission filters before ranking.
Expand typed relationships only within authorized scope. Rerank with authority, freshness, source
quality and task relevance. Vector similarity alone never determines authority.

## Context assembly

Build the smallest sufficient context that answers the task. Include source paths, versions, commit
revision and confidence. Separate approved project facts, proposed target design, general guidance
and uncertain findings. Respect model context limits without removing source attribution or access
labels. Never expose hidden internal reasoning.

## MCP mapping

Expose read operations as tools and/or resources. Suitable tool names include
search_engineering_knowledge, get_project_context, get_architecture_decision,
trace_feature_execution, find_related_concepts and get_sprint_learning_pack.

Write operations create proposals, not bypass human approval. Keep MCP tool schemas aligned with
the REST contract.

## Evaluation

Maintain real engineering questions and expected source records. Track Precision@5, Recall@K,
citation validity, freshness, permission-filter correctness, latency and token efficiency. Test that
unauthorized records never appear in results or assembled context.
