# Local development

## Prerequisites

- Docker Desktop with Compose
- Node.js 24 with Corepack (or another supported current Node runtime)
- Python 3.12–3.14 and `uv`

## Bootstrap

Copy `.env.example` to `.env` only if you need local overrides. The committed defaults are for the
local demo profile and must not be used in production.

```bash
make bootstrap
make dev
```

On Windows where GNU Make is not installed, run the equivalent commands:

```powershell
uv lock --project services/backend
uv sync --project services/backend --all-groups
corepack pnpm --dir apps/web install --frozen-lockfile
docker compose up --build
```

Open `http://localhost:3000`. API liveness is at `http://localhost:8000/api/v1/health/live`; API
readiness requires PostgreSQL, Redis, and MinIO and is at `/api/v1/health/ready`.

## Checks

```bash
make check
```

`make check` regenerates the OpenAPI TypeScript schema, lints, typechecks both Python and
TypeScript, runs unit tests, builds the web application, and fails when the checked-in generated
schema is stale. GitHub Actions additionally builds both containers and starts the production web
image for an HTTP smoke test.

## Phase 0 limitation

The platform contains no sessions, uploads, OCR, biomedical retrieval, agent plans or visualization
results yet. The UI intentionally states this rather than showing fabricated content.
