# Codex implementation execution plan

## How to use

Place this file, `AGENTS.md`, and `docs/BIOSCOPE_MASTER_ARCHITECTURE.md` in the root of a new repository. Ask Codex to read all three and implement **Phase 0 only** first. Approve next phase after verifying working tests. The phases below are ordered by actual dependencies, not by marketing appeal.

### Bootstrap prompt to paste into Codex

> You are implementing BioScope AI, a modular, evidence-grounded, agentic biomedical educational explorer. Read `docs/BIOSCOPE_MASTER_ARCHITECTURE.md` completely, then `AGENTS.md`, then this plan. Implement **Phase 0 only** with actual running Next.js and FastAPI code, Postgres/Redis/object-storage local services, basic migrations, contract-first OpenAPI generated TS client, CI and tests. Follow vertical slices and clean dependency direction. Do not fabricate source retrieval, clinical results, or visualization content. Use `DEMO_MODE` for clearly labeled fixtures. Run test/check commands and provide a precise report of created files, pass/fail results and limitations. Stop after the Phase 0 acceptance gate.

### Subsequent phase prompt template

> Implement Phase N from `prompts/CODEX_IMPLEMENTATION_PLAN.md`, using the master architecture and `AGENTS.md` as normative contracts. Start by inspecting current source and implementation-status.md. Produce a short checklist, implement real code in appropriate small cohesive files, add tests for success/failure/security, run `make check`, update docs and implementation-status.md, and report the exact unresolved limitations. Stop at the phase gate; do not silently implement features beyond scope.

## Phase 0: Architecture and development platform

### Deliverables

- [ ] `apps/web` Next.js App Router + strict TS + responsive layout shell.
- [ ] `services/backend` FastAPI app with `bootstrap/settings`, health routes and standardized error envelope.
- [ ] `docker-compose.yml` for PostgreSQL/Redis/local object storage and API/web/worker (one consistent approach; documented).
- [ ] `pyproject.toml`/uv lock and package.json/pnpm lock; pinned compatible versions.
- [ ] Alembic migration base, DB connection, Unit of Work port, test DB.
- [ ] OpenAPI export and generated frontend SDK script.
- [ ] `Makefile` with `bootstrap/dev/lint/test/check`.
- [ ] `.env.example`, `.gitignore`, `.editorconfig`, useful README.
- [ ] CI for typecheck, lint, unit and minimal browser smoke.
- [ ] ADR-001..003 copied from master into meaningful decision records.

### Tests

- [ ] API `/health/live`, `/health/ready`, JSON error envelope.
- [ ] Web root loads and links to `/explore`.
- [ ] Incorrect configuration fails startup visibly.
- [ ] DB migration runs in clean environment.
- [ ] Generated client contract roundtrip.

### Phase gate

A fresh clone runs the documented bootstrap/dev/check path. Neither UI nor API pretends to perform biomedical inference.

## Phase 1: Input and secure session flow

### Deliverables

- [ ] Session module domain/application/infrastructure/api, auth abstraction and local dev auth strategy.
- [ ] Owner-only session creation/list/read/delete.
- [ ] Uploaded assets with upload-intent/complete, file restrictions, private storage, consent and expiry.
- [ ] Medicine text-list editor with individual item identity status.
- [ ] OCR adapter port and `FakeOCR` fixture (visibly demo); optional real OCR behind off-by-default feature flag.
- [ ] Entity candidate/confirmation DTOs and UI; ambiguous items require explicit selection.
- [ ] SSE/run state scaffolding but no unimplemented fake “research success.”
- [ ] Minimal secure deletion and cleanup worker path.

### Tests

- [ ] Ambiguous photo stays unresolved.
- [ ] Combination medicine retains multiple active ingredients.
- [ ] Another user cannot view/upload/delete the owner's assets.
- [ ] Upload reject wrong MIME, oversized and malformed images.
- [ ] No sensitive contents appear in logs/traces.
- [ ] Full text medicine-list and confirmed-candidate UI flow works in browser.

### Phase gate

Inputs are secure, confirmed state is distinguishable from extracted guesses, and users can delete their data.

## Phase 2: Biomedical evidence data plane

### Deliverables

- [ ] Canonical entity/xref/source/source snapshot/claim/claim-evidence schema and migrations.
- [ ] Evidence type ontology, scientific context and provenance.
- [ ] One medicine identity adapter (choose based on available data terms), plus ChEMBL and Reactome adapters as appropriate; adapters isolated and contract-tested.
- [ ] Configurable source allowlist, timeouts, rate limits, retries, caching and immutable snapshots.
- [ ] `EvidenceService` for query, claim creation, evidence mapping and typed relationship validation.
- [ ] Evidence source and claim detail API/UI cards.
- [ ] Only after necessary: outbox and optional Neo4j read projection; no dual writable truth.

### Tests

- [ ] `ASSOCIATED_WITH` is not automatically `CAUSES`.
- [ ] Source record version and DOI/URL are preserved.
- [ ] Outage does not create fabricated evidence.
- [ ] Cross-species or context mismatches are flagged.
- [ ] Every released claim has source refs.
- [ ] Demo fixture is labeled `DEMO`, never confused with live data.

### Phase gate

The application can retrieve and present source-grounded evidence with auditable identifiers, even with no LLM.

## Phase 3: Agent workflow engine

### Deliverables

- [ ] `SkillDescriptor`, registry and deterministic allowlisted executor.
- [ ] Typed TaskPlan DAG, dependency/cycle validator, budgets and permissions.
- [ ] `LLMGateway` port with fake model for deterministic tests; one real provider adapter only when configured.
- [ ] LangGraph runner and versioned checkpoints with run status/events.
- [ ] Minimal planner, drug specialist, molecular/pathway specialist, verifier, explanation agent.
- [ ] Deterministic safety gates before/after workflow, bounded replanning, cancellation.
- [ ] No numeric reliability score, but verification verdict objects.
- [ ] SSE run progress and UI phase labels.

### Tests

- [ ] Unknown skills, DAG cycles, invalid DTOs blocked.
- [ ] Uploaded text prompt injection cannot trigger import/command/unapproved URL.
- [ ] Task timeout and retry limits honored.
- [ ] Planner cannot bypass a safety-blocked request.
- [ ] Two independent retrieval tasks run without racing state writes.
- [ ] Waiting-for-confirmation and resumed plan maintain correct state.
- [ ] Deliberate missing evidence results in limited answer.

### Phase gate

A previously unseen combination of supported tasks composes into a safe plan, and the emitted scientific claims have verifier decisions.

## Phase 4: Scientific scene engine

### Deliverables

- [ ] Versioned `SceneSpec` JSON Schema and compiler with strict provenance validation.
- [ ] Renderer registry and `SceneHost` with lazy imports.
- [ ] Interaction graph (Cytoscape), evidence-only fallback.
- [ ] Molecular renderer (Mol*) restricted to verified structure IDs.
- [ ] One reviewed anatomy/skin schematic asset with citation and illustration label.
- [ ] Scene inspector, evidence drawer, scale navigator, responsive mobile viewer.
- [ ] Interactive entity selection and follow-up context.

### Tests

- [ ] Unknown renderer/version falls back without crashing.
- [ ] Missing claim ID or unsupported causal edge blocked before rendering.
- [ ] Schematic cannot be mislabeled experimental patient image.
- [ ] Sample real structure ID renders only with corresponding structure data.
- [ ] Interaction graph displays edge predicate and evidence card.
- [ ] Basic keyboard controls, alt text and reduced motion.

### Phase gate

The user can select an evidence-backed scene and inspect why each relationship is shown.

## Phase 5: Reliability and safety beta

### Deliverables

- [ ] `VerificationReport`, `ReliabilityReport`, evidence status/freshness and coverage panels.
- [ ] Separate quality dimensions; `overall_probability=null` unless calibrated.
- [ ] Independent release policy for text and scene validity; safety and privacy tests.
- [ ] Golden workflows and negative/ambiguous benchmark cases.
- [ ] Trace and observability redaction, data deletion checks, source-version invalidation.
- [ ] Reviewer documentation for evidence curation (no unvetted clinical claims).

### Tests

- [ ] LLM cannot self-assign arbitrary percentages.
- [ ] One unsafe critical claim blocks release even if other claims are supported.
- [ ] Reliability panel differentiates known general mechanism vs unknown patient relevance.
- [ ] Required hard-stop cases pass.
- [ ] Source retraction/update marks dependent scene stale or subject to re-review.

### Phase gate

Beta clearly explains limitations, uncertainty and scientific provenance without false precision.

## Phase 6: Optional multimodal expansions

### Deliverables

- [ ] Skin-image observation pipeline with strict non-diagnostic posture and contextual red-flag messaging.
- [ ] Combined skin photograph + medicine list flow and context-aware viewer selection.
- [ ] Regional catalogs, license reviews, localization and broader scene collection.
- [ ] Additional reader modes for educational lab reports and complex research questions only after risk review.

### Tests

- [ ] Skin photograph cannot trigger unauthorized diagnosis mode.
- [ ] User image does not imply actual personalized gene expression or molecular state.
- [ ] Mixed-modal combined task maintains per-claim uncertainty.
- [ ] Image quality and source-unavailable states are handled.

### Phase gate

Extended workflows compose safely from existing skills and introduce no unsupported personalized claims.

## Reporting format after every phase

```text
PHASE N — IMPLEMENTATION REPORT
1. What now works end-to-end (tested evidence)
2. Exact created/changed files grouped by domain
3. Commands run + observed outputs
4. Schema migrations and API changes
5. External adapters LIVE vs MOCK/DEMO vs NOT IMPLEMENTED
6. Security/privacy/safety checks and known gaps
7. Current architecture divergences + ADR links
8. Next eligible phase (do not start automatically)
```

## Definition of “complete project”

Do not report completion until all committed phases meet gates. Architecture documents, generated folder trees and a visually convincing demo do not constitute a scientifically validated product. Clinical features that require further evidence, expert review, data rights or regulatory assessment remain disabled with explicit documentation.
