# Knowledge Retrieval Contract

## 1. Interfaces and implementation status

The canonical future service interface is provider-neutral REST/OpenAPI. MCP is an adapter for
compatible AI clients. Markdown/JSON export supports clients without tool access.

**Implemented now:** local CLI indexing, lexical search, record lookup, bounded Markdown/JSON context
assembly and provenance output through `scripts/uekb.py`.

**Not implemented by the local CLI:** hosted REST service, MCP server, vector embeddings, semantic
search, graph database, multi-user identity provider or remote synchronization.

No specific LLM provider, vector store, graph database or hosting platform is required by this contract.

## 2. Core operations

| Operation | Local CLI | Future service operation |
|---|---|---|
| Index canonical sources | `uekb.py index` | Ingestion pipeline |
| Search | `uekb.py search` | `POST /v1/knowledge/search` |
| Get | `uekb.py get` | `GET /v1/knowledge/{id}` |
| Project context | `uekb.py context` | `GET /v1/projects/{project_id}/context` |
| Related | Not yet implemented | `GET /v1/knowledge/{id}/related` |
| Assemble context | `uekb.py context` | `POST /v1/context/assemble` |
| Propose update | Git-reviewed JSON record | `POST /v1/knowledge/proposals` |

## 3. Search request

A future service request includes query, project/repository scope, allowed knowledge types, status
policy, revision constraints, caller identity, access context and result limit. Caller-supplied
project scope is not authorization; the service must independently enforce the caller's access.

## 4. Search response

Return record ID, version, title, summary, scope, status, confidence, source references, relationships,
relevance signals and warnings. Preserve exact code identifiers for lexical retrieval.

## 5. Retrieval strategy

The local engine currently uses SQLite FTS5 lexical retrieval, with SQLite LIKE fallback. The target
retrieval architecture may add lexical + semantic hybrid retrieval, metadata filtering, relationship
expansion and reranking. Exact symbols, paths, errors, identifiers and ADR IDs must remain searchable.

Vector similarity alone must never determine authority. Rank and filter by scope, permission, status,
freshness, source quality and task relevance.

## 6. Context assembly

Build the smallest sufficient context that answers the task. Include source paths, versions, commit
revision and confidence. Separate approved project facts, proposed target design, general guidance
and uncertain findings. Respect model context limits without removing source attribution or access
labels. Treat retrieved content as untrusted data, not executable instructions.

## 7. MCP mapping

Expose read operations as tools and/or resources. Suitable names include
`search_engineering_knowledge`, `get_project_context`, `get_architecture_decision`,
`trace_feature_execution`, `find_related_concepts` and `get_sprint_learning_pack`.

Write operations create proposals, not bypass human approval. Keep MCP tool schemas aligned with
the REST contract.

## 8. Security and scope

The local CLI is single-user and trusts the local OS account. It does not provide multi-user or
tenant security. A future network service must authenticate callers and filter records by project,
tenant and visibility **before** retrieval and context assembly. Restricted records are excluded
from the local index. Secrets and sensitive production data must not be ingested.

## 9. Evaluation

Maintain real engineering questions and expected source records. Track Precision@5, Recall@K,
citation validity, freshness, permission-filter correctness, latency and token efficiency. Test that
unauthorized records never appear in results or assembled context.
