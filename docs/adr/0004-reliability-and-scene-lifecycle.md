# ADR-004: Reliability is evidence status, and invalidated sources stale scenes

- Status: accepted
- Date: 2026-10-13

## Context

The first runnable workflow uses deterministic synthetic fixtures while live-source licensing,
scientific review, and calibration evaluation are incomplete. A percentage would imply an
unavailable validation process. A previously compiled visualization can also become misleading if
its backing source is retracted or deprecated.

## Decision

Persist a per-run reliability report in `EVIDENCE_STATUS_ONLY` mode. Numeric probability and
calibration model version are `null` by contract, and startup rejects the numeric-confidence flag.
Expose named dimensions, per-claim evidence status, critical gaps, and a fixed educational
disclaimer instead.

When a source is retracted, mark dependent claims `DEPRECATED` and dependent scenes `STALE`.
The scene list exposes the stale state, but scene retrieval refuses to release stale content.

## Consequences

Users see an explicit limited result rather than a fabricated confidence number. Source lifecycle
operations have an observable effect on existing renderings. A future calibrated task estimator
requires a separate ADR, held-out evaluation evidence, monitoring, and a narrowly defined task;
it cannot be enabled by changing a display string.
