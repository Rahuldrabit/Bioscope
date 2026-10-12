# BioScope backend

The Phase 0 backend provides configuration validation, health endpoints, a standard API
error envelope, the SQLAlchemy async database boundary, and an Alembic migration baseline.
It does not retrieve biomedical evidence or make medical inferences.

Run from the repository root with `make dev`, or locally with:

```bash
uv sync --project services/backend --all-groups
uv run --project services/backend fastapi dev src/bioscope/main.py
```
