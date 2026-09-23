# Security Architecture

> Status: **not yet generated**. See
> [CODEBASE_INTELLIGENCE.md](CODEBASE_INTELLIGENCE.md) for refresh status.

## Authentication
_Trace: login request -> validation -> credential verification -> session/
token creation -> storage -> authenticated request, with real files._

## Authorization
_User -> identity -> org/tenant -> role -> permission -> resource -> action,
with real enforcement points (middleware, guards, service checks)._

## Tenancy / Data Isolation
_Tenant identifier, resolution, query scoping, authorization scoping,
background-job scoping. N/A if single-tenant._

## Confirmed Protections
_Security mechanisms actually found in code._

## Potential Weaknesses
_Evidence-supported concerns only._

## Unknowns
_Important controls that can't be established from available evidence, and
what evidence would resolve them._
