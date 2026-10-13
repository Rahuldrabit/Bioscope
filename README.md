# BioScope AI

BioScope is an evidence-grounded biomedical education application in phased development. Its target
architecture deliberately separates general science explanation from diagnosis, treatment advice,
and unvalidated confidence scores.

## Current implementation: Phases 0–6 core path

- Private owner-scoped sessions, consented image uploads, explicit medicine-candidate confirmation,
  user deletion, and a clearly labelled deterministic OCR fixture.
- Canonical evidence/source/snapshot/claim records, typed relationship checks, transparent source
  lifecycle invalidation, and a disabled-by-default ChEMBL adapter.
- Allowlisted deterministic workflow DAGs, durable events and cancellation, safety gates, scene
  validation, provenance cards, evidence/graph/anatomy renderers, and reliability reports with no
  fabricated numeric score.
- Feature-flagged skin-photo handling that only returns an unavailable observation or urgent safety
  escalation. It does not diagnose images or infer patient-specific biology.

The currently released science path uses synthetic software-test fixtures only. Every such result
is marked `DEMO`; no live biomedical evidence or clinical conclusion is claimed. See the detailed
[implementation status](docs/implementation-status.md) for completed checks and remaining release
requirements.

## Run locally

See [local development instructions](docs/runbooks/local-dev.md). The short path is:

```bash
make bootstrap
make dev
```

Then visit `http://localhost:3000`. The API liveness endpoint is
`http://localhost:8000/api/v1/health/live`.

## Safety posture

BioScope is educational software. It does not diagnose skin conditions, make personalized
medication recommendations, recommend dosing, or provide numeric diagnosis/reliability estimates.
These boundaries are enforced by the architecture and will remain in place through subsequent
phases.

## Architecture references

1. [Master architecture](docs/BIOSCOPE_MASTER_ARCHITECTURE.md)
2. [Agent engineering rules](AGENTS.md)
3. [Module contracts](docs/MODULE_CONTRACTS.md)
4. [Implementation status](docs/implementation-status.md)
