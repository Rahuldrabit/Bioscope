.PHONY: bootstrap dev down migrate generate-api lint typecheck test check

bootstrap:
	uv lock --project services/backend
	uv sync --project services/backend --all-groups
	corepack pnpm --dir apps/web install --frozen-lockfile

dev:
	docker compose up --build

down:
	docker compose down

migrate:
	uv run --project services/backend alembic -c services/backend/alembic.ini upgrade head

generate-api:
	uv run --project services/backend bioscope-export-openapi --output artifacts/openapi.json
	corepack pnpm --dir apps/web generate:api

lint:
	uv run --project services/backend ruff check services/backend/src services/backend/tests
	corepack pnpm --dir apps/web lint

typecheck:
	uv run --project services/backend pyright --project services/backend/pyproject.toml
	corepack pnpm --dir apps/web typecheck

test:
	uv run --project services/backend pytest services/backend/tests
	corepack pnpm --dir apps/web test

check: generate-api lint typecheck test
	corepack pnpm --dir apps/web build
	@if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		git diff --exit-code -- apps/web/src/shared/api/generated/schema.ts; \
	else \
		echo "Generated API client verified; Git drift check skipped outside a Git worktree."; \
	fi
