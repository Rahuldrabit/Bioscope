# ADR-003: Agent capabilities are allowlisted and schema-validated

- Status: accepted
- Date: 2026-10-12

## Context

Uploaded images, OCR text and retrieved documents are untrusted. A planner or model must not turn
them into shell commands, arbitrary imports, unrestricted network access or direct database writes.

## Decision

Future workflows will select only server-owned skill IDs from a startup registry. Every skill has
input/output schemas, permissions, budgets and a fixed implementation binding. Safety gates have
precedence over planner output.

## Consequences

Phase 0 does not expose any agent skills. Subsequent phases must prove unknown skills, malformed
arguments and instruction-injection attempts fail safely before the capability is released.
