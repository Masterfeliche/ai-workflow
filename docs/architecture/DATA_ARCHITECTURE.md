# Data Architecture

> Status: **not yet generated**. See
> [CODEBASE_INTELLIGENCE.md](CODEBASE_INTELLIGENCE.md) for refresh status.

## Data Model
_Simplified domain model (entities + relationships), only what's evidenced._

## Database Analysis
_Engine, ORM, tables/collections, keys, indexes, constraints, transactions,
migrations, where queries are executed._

## State Beyond the Database
| Store | What's Stored | Why | Writer | Reader | Lifetime | If Lost |
|---|---|---|---|---|---|---|
| | | | | | | |

## Evidence-Supported Risks
_N+1 patterns, missing indexes, unsafe raw SQL, transaction-boundary
issues -- only with a concrete file/line pointing at it._
