# BioScope backend

The backend provides private educational sessions/uploads, confirmation-gated demo evidence,
durable bounded workflows, source/claim provenance, SceneSpec validation, reliability reports with
null numeric scores, and feature-flagged non-diagnostic skin observation handling. It never makes
clinical diagnoses, treatment recommendations, dose changes, or patient-specific molecular claims.

Live biomedical-source release is not enabled: the shipped evidence fixture is explicitly
synthetic/testing-only.

Run from the repository root with `make dev`, or locally with:

```bash
uv sync --project services/backend --all-groups
uv run --project services/backend fastapi dev src/bioscope/main.py
```
