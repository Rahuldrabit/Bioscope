# BioScope AI

BioScope is an evidence-grounded biomedical education application in phased development. Its target
architecture deliberately separates general science explanation from diagnosis, treatment advice,
and unvalidated confidence scores.

## Current implementation: Phase 0

The repository now includes a bootable development platform:

- Next.js App Router web shell with an accessible landing page and `/explore` workspace preview.
- FastAPI liveness plus PostgreSQL/Redis/MinIO readiness and privacy-safe standardized error
  envelopes.
- Validated environment settings, async SQLAlchemy boundary, Alembic baseline migration, and local
  PostgreSQL/Redis/MinIO Docker Compose stack.
- OpenAPI export plus a checked-in schema and typed `openapi-fetch` client.
- Backend/frontend tests, static type checks, dependency audits, browser/container smoke CI, and
  ADRs 001–003.

No user sessions, uploads, OCR, medical identity resolution, scientific retrieval, agent workflows,
or visualization results have been implemented. The demo-style banner indicates platform state; it
does not stand for medical demo output.

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
