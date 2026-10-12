# Implementation status

## Phase 0 — architecture and development platform

Status: implemented and locally verified where the host environment permits. This is a platform
foundation only; it does **not** implement sessions, uploads, OCR, identity confirmation, source
retrieval, agent workflows, claims, scenes, or biomedical inference.

### 1. What works end-to-end

- The Next.js App Router serves an accessible landing page at `/` and an explicit, non-functional
  Phase 0 workspace preview at `/explore`. The preview states that it is waiting for verified
  evidence and disables unavailable input rather than simulating medical results.
- The FastAPI application serves `/api/v1/health/live` and readiness checks for PostgreSQL, Redis,
  and S3-compatible storage at `/api/v1/health/ready`. It emits a stable privacy-safe error
  envelope with a consistently correlated opaque trace ID.
- Validated settings reject malformed dependency URLs, local/default credentials outside local
  environments, insecure production object storage, production demo mode, and the uncalibrated
  numeric-confidence feature flag.
- `alembic upgrade head` applies a clean baseline migration; OpenAPI exports to JSON and
  `openapi-typescript` generates the checked-in frontend API schema, which backs an
  `openapi-fetch` runtime client.

### 2. Created/changed components

| Area | Paths |
| --- | --- |
| Web | `apps/web/src/app`, `apps/web/src/shared`, `apps/web/src/tests`, `apps/web/package.json`, `apps/web/{Dockerfile,next.config.ts,playwright.config.ts,vitest.config.ts}` |
| API | `services/backend/src/bioscope/{bootstrap,shared,modules/platform,scripts,workers}`, `services/backend/tests` |
| Persistence | `services/backend/alembic`, `services/backend/alembic.ini`, `services/backend/uv.lock` |
| Developer platform | `.env.example`, `.editorconfig`, `.gitignore`, `docker-compose.yml`, `Makefile`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `scripts/generate-client.*` |
| Governance and docs | `.github/workflows`, `docs/adr/0001-*` through `0003-*`, `docs/api/errors.md`, `docs/runbooks/local-dev.md`, `README.md` |

### 3. Verification commands and observed results

| Command | Result |
| --- | --- |
| `uv lock --project services/backend` | passed; created a pinned `uv.lock` |
| `uv sync --project services/backend --all-groups --frozen` | passed |
| `corepack pnpm --dir apps/web install` | passed; created root `pnpm-lock.yaml` |
| `uv run --project services/backend ruff check services/backend/src services/backend/tests` | passed |
| `uv run --project services/backend pyright --project services/backend/pyproject.toml` | passed; 0 errors and 0 warnings |
| `uv run --project services/backend pytest services/backend/tests` | **14 passed**; one upstream Starlette deprecation warning |
| `corepack pnpm --dir apps/web lint` | passed |
| `corepack pnpm --dir apps/web typecheck` | passed |
| `corepack pnpm --dir apps/web test` | **1 passed** |
| `corepack pnpm --dir apps/web build` | passed; `/` and `/explore` statically generated |
| `PLAYWRIGHT_EXECUTABLE_PATH=<system Edge> corepack pnpm --dir apps/web test:e2e` | **1 passed**; root page loaded and navigated to `/explore` |
| `DATABASE_URL=sqlite+aiosqlite:///:memory: uv run --project services/backend alembic -c services/backend/alembic.ini upgrade head` | passed; baseline migration applied |
| `docker compose config --quiet` | passed |
| `uv run --project services/backend pip-audit --requirement <export>` | passed; no known vulnerabilities |
| `corepack pnpm audit --prod --audit-level moderate` | passed; no known vulnerabilities |
| `node node_modules/next/dist/bin/next --version` from `apps/web` | passed; runtime entrypoint resolved as Next.js 15.5.27 |

### 4. Schema migrations and API changes

- Migration `20261012_0001_platform_baseline` creates the `platform_metadata` baseline table.
- OpenAPI declares liveness/readiness and standard `ErrorEnvelope` for dependency-unavailable
  readiness responses. Generated types live in `apps/web/src/shared/api/generated/schema.ts`, and
  the typed runtime client is `apps/web/src/shared/api/client.ts`.

### 5. Integrations

- **Local infrastructure configured:** PostgreSQL, Redis and MinIO through Docker Compose.
- **Live biomedical adapters:** not implemented.
- **Mock/demo biomedical results:** not implemented; the visible demo label only describes the
  platform environment, not health data.

### 6. Safety, privacy and known gaps

- No biomedical output is generated, so no diagnosis, treatment, medication or confidence claim is
  made. Uncalibrated numeric confidence is rejected by configuration.
- The API error layer avoids request payloads and stack traces; the UI clearly identifies unavailable
  features.
- Docker Desktop was not running on the implementation host, so image and full Compose runtime
  checks could not execute locally. Compose syntax, the corrected production entrypoint, a clean
  migration, and browser behavior were independently verified. CI builds both images and starts the
  production web container for an HTTP smoke test.

### 7. Architecture divergence

None. Phase 0 intentionally leaves future bounded domains absent rather than mass-creating empty
module folders.

### 8. Next eligible phase

Phase 1: secure session flow, owner-scoped uploads, medicine-list editing, explicit candidate
confirmation and clearly labeled demo OCR fixtures. Do not start it automatically.
