# ADR-002: PostgreSQL is the canonical evidence store

- Status: accepted
- Date: 2026-10-12

## Context

Biomedical claims require immutable provenance, review status and transactional consistency.
Graph traversal is useful, but maintaining two writable stores risks conflicting scientific truth.

## Decision

PostgreSQL is the canonical store for entities, sources, claims, evidence, approvals and scenes.
Neo4j, when introduced, is a rebuildable read projection fed from transactional outbox events.

## Consequences

Phase 0 starts with an Alembic-controlled PostgreSQL baseline. A later graph projection must carry
its applied version and must fall back to canonical data if it is stale.
