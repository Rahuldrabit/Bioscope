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

## Local/demo limitation

The local workflow runs only deterministic, clearly labelled synthetic fixtures. The ChEMBL adapter
and skin observation feature are opt-in (`ENABLE_EXTERNAL_SOURCES=false` and
`ENABLE_SKIN_IMAGE_UPLOAD=false` by default). Do not treat a local demo result as biomedical
evidence, diagnosis, medication advice, or a calibrated reliability score.
