# Implementation status

## Delivered scope: Phases 0–6

BioScope now provides a locally runnable, modular-monolith educational workflow from a private
session through explicit medicine confirmation, evidence provenance, a bounded workflow, safe
scene compilation, transparent reliability status, and opt-in non-diagnostic skin-photo handling.
The implementation deliberately keeps synthetic fixtures visible as `DEMO` and does not present
them as biomedical facts, diagnosis, medication advice, or calibrated reliability scores.

## Phase 1 — secure sessions, uploads, and confirmation

- Owner-scoped sessions, messages, assets, medicine candidates, and explicit confirmations are
  implemented in `services/backend/src/bioscope/modules/{sessions,uploads,medicines}`.
- Image uploads require consent, an opaque one-time token, content-type/byte validation, a
  private local object store, and an owner-scoped deletion path. Public responses never disclose
  the storage key.
- A deterministic filename-based OCR fixture is available only for clearly named demo files; it
  produces a `CANDIDATE`, never an auto-confirmed medicine.
- Session deletion removes private blobs and dependent session records, including messages,
  workflow state, scenes, reports, and medicine records.
- The workspace includes private-session creation, medicine confirmation, consented image upload,
  and actionable safe error states.

## Phase 2 — auditable evidence backbone

- Canonical entities, xrefs, sources, immutable snapshots, typed claims, claim evidence, and an
  outbox are persisted through migration `20261013_0003_evidence_provenance`.
- Each released fixture claim has a source, snapshot, citation, provenance label, and typed
  relationship. Association-to-causation promotion is rejected.
- The `ChEMBLClient` adapter is opt-in and fails transparently while disabled; no live-source data
  is silently fabricated or released. The currently releasable data path is the explicitly
  labelled synthetic fixture in `data/demo/fixture-manifest.json`.
- Source retraction marks dependent claims deprecated and dependent scenes `STALE`; stale scenes
  cannot be retrieved as active viewer content.

## Phase 3 — bounded workflows and safety gates

- `agent_workflows`, `skills`, and `safety` implement an allowlisted, deterministic plan/executor
  for the local fixture provider. User text cannot choose a skill, import code, call a shell, or
  bypass policy.
- Durable runs, task records, checkpoints, verification records, cancellation, replayable SSE
  events, and owner checks are included in migration `20261013_0004_workflow_runs`.
- Hard stops for breathing difficulty, concerning spreading/blistering rash, fever-associated
  rash, and facial swelling take precedence over the workflow. Requests for diagnosis, dosing,
  prescribing, or medication changes receive a limited educational response.
- This is not a live LLM or LangGraph deployment: the provider-neutral planner is a deterministic
  test adapter until a reviewed provider, source policy, and evaluation are approved.

## Phase 4 — validated scenes and accessible fallbacks

- Versioned `SceneSpec` JSON Schema, backend validation, compiler, persistence, and owner-scoped
  retrieval live in `packages/scene-schema`, `bioscope/scenes`, and
  `bioscope/modules/visualization`.
- The web renderer registry supports relation graphs, evidence-only tables, general skin-layer
  schematics, and a molecular evidence fallback. Graph relationships open claim provenance.
- General skin anatomy is separately labelled `CURATED_EDUCATIONAL_SCHEMATIC` and carries asset
  provenance; it is not treated as a patient image or a mechanism claim.
- The molecular renderer never invents a structure. For a future verified PDB reference it offers
  the authoritative RCSB record and evidence card. Bundling interactive Mol* remains deferred
  pending approval of its client dependency’s build-script policy.

## Phase 5 — reliability, quality, and lifecycle visibility

- `reliability_reports` persist a transparent `EVIDENCE_STATUS_ONLY` assessment. Every numeric
  probability and calibration-model field is structurally `null`.
- The report exposes identity status, evidence/source limitations, visual fidelity, per-claim
  verdicts, critical gaps, and a non-clinical disclaimer in both the API and workspace panel.
- `ENABLE_NUMERIC_CONFIDENCE=true` remains rejected at startup.

## Phase 6 — controlled complex input support

- `POST /api/v1/sessions/{session_id}/skin-observations` is feature-flagged by
  `ENABLE_SKIN_IMAGE_UPLOAD` (default `false`), owner-scoped, and requires a ready consented
  session asset.
- The current non-diagnostic implementation returns only `OBSERVATION_UNAVAILABLE` or a safety
  escalation. It performs no automated image description, diagnosis, treatment recommendation,
  or patient-specific molecular inference.
- The workspace exposes the opt-in upload and restricted observation flow, including its disabled
  and unavailable states.
- Localized content, regional medicine catalogs, reviewer tooling, and any classifier remain
  deferred because they require source licensing, governance, validation, and product/legal
  approval rather than placeholder implementations.

## Verification performed

| Command | Observed result |
| --- | --- |
| `uv run ruff check src tests` | passed |
| `uv run pyright` | passed, 0 errors / 0 warnings |
| `uv run pytest` | passed, 32 tests; one upstream Starlette deprecation warning |
| `DATABASE_URL=sqlite+aiosqlite:///../../artifacts/migration-phase6-check.db uv run alembic -c alembic.ini upgrade head` | passed through `20261013_0006` |
| `uv run bioscope-export-openapi --output ../../artifacts/openapi.json` | passed |
| `corepack pnpm --dir apps/web generate:api` | passed |
| `corepack pnpm --dir apps/web lint` | passed |
| `corepack pnpm --dir apps/web typecheck` | passed |
| `corepack pnpm --dir apps/web test` | passed, 1 test |
| `corepack pnpm --dir apps/web build` | passed; `/` and `/explore` statically generated |
| `PLAYWRIGHT_EXECUTABLE_PATH=<system Edge> corepack pnpm --dir apps/web test:e2e` | passed, 1 browser smoke test |
| `uv run pip-audit --requirement ../../artifacts/bioscope-requirements.txt` | passed; no known vulnerabilities |
| `corepack pnpm audit --prod --audit-level high` | passed; no known vulnerabilities |

## Production and scientific boundaries

- No source fixture in this repository is live biomedical evidence. Synthetic data is for software
  testing only and is visibly limited in APIs and UI.
- A source-license review, reviewed live adapter contract, factual evaluation set, privacy/legal
  review, authenticated production identity provider, encrypted production object store, and
  clinical/regulatory validation are required before production use.
- Phase 7 clinical/research extensions remain out of scope and require separate approval.
