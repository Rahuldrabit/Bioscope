#!/usr/bin/env sh
set -eu

uv run --project services/backend bioscope-export-openapi --output artifacts/openapi.json
corepack pnpm --dir apps/web generate:api
