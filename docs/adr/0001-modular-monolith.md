# ADR-001: Modular monolith for the first product stages

- Status: accepted
- Date: 2026-10-12

## Context

BioScope needs web, API, worker, evidence and visualization capabilities with strict safety
boundaries. Early independent services would multiply deployment and contract complexity before
the bounded domains are proven.

## Decision

Use a Next.js web application and a FastAPI API/worker that import the same Python modular
codebase. Backend modules follow domain, application, infrastructure and API boundaries. The web,
API and worker may be separate processes, but they are not separate domain services.

## Consequences

The application can be developed and tested locally as one system while preserving clear seams for
future extraction. HTTP handlers, domain rules and infrastructure adapters remain separated, so a
future extraction does not require untangling direct database or provider access.
