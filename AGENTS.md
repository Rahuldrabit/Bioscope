# AGENTS.md — Mandatory Instructions for Coding Agents

## Mission and scope

Implement BioScope AI according to `docs/BIOSCOPE_MASTER_ARCHITECTURE.md`. The repository should grow as a **testable, modular, evidence-grounded educational biomedical application**. Current spec describes a target architecture; do not claim unfinished components are implemented. Do not silently turn educational features into diagnosis, personalized medication advice, or unvalidated clinical classification.

**Read order:** master architecture → this file → `prompts/CODEX_IMPLEMENTATION_PLAN.md` → relevant module docs and tests. The master architecture resolves disagreements.

## Non-negotiable engineering principles

1. Favor a modular monolith: Next.js web + FastAPI/worker using the same Python module codebase. Do not create independent deployment services for each agent.
2. Organize code by bounded domain; each module has `domain`, `application`, `infrastructure`, `api` as appropriate. Add folders/files as features are implemented; avoid empty scaffolding explosion.
3. **Dependency rule:** domain depends on nothing external; application depends on domain and ports; infrastructure depends on ports/domain; HTTP handlers depend on application use cases. Never import from infrastructure into domain.
4. HTTP endpoint has no raw SQL, LLM call, OCR, or connector parsing. These belong to application services/skills/adapters.
5. Frontend has feature-specific components, hooks, state and API wrappers. Generic UI primitives are domain-free. Renderer plugins are isolated per engine.
6. Keep pure transformations deterministic and tested. Prefer explicit typed DTOs; no mega-service functions or single-file “entire application.”
7. PostgreSQL is canonical for claims/identity/reports; Neo4j only a rebuildable approved-edge projection. Do not maintain independent conflicting truths.
8. Scientific claims must have typed relationships, source IDs, scope and evidence status. No source-supported claim may be inferred merely from network distance or protein co-occurrence.
9. Every generated visualization passes SceneSpec JSON Schema and claim-reference validation. No generated code execution, untrusted imports, SVG/script injection or remote arbitrary resource URL fetching.
10. Agent skill names, arguments, outputs and permissions are allowlisted and schema-validated. No LLM shell, unrestricted HTTP, runtime package installation or direct database mutation.
11. A hard safety gate has precedence over planner instructions and reliability heuristics. In v1, skin-photo analysis is observational/educational only.
12. Do not generate a confidence percentage from a model's opinion. Only evidence status labels until a calibrated, independently evaluated estimator exists.
13. Keep sensitive health data private: never log raw photos, prescription text or identifiable medical question payloads; avoid PHI in traces and fixtures.
14. Use generated TypeScript API types from backend OpenAPI, not duplicate hand-maintained interfaces. Update client when backend schema changes.
15. Do not fabricate live API results, successful image analysis, drug interactions, molecular structures or medical explanations. Demo fixtures must visibly carry `DEMO` provenance and be off by default in production.
16. Documentation, tests and empty/error states are part of implementation, not optional post-work.

## How to implement a vertical slice

For each feature, use the following sequence:

1. Read acceptance requirements and define boundaries.
2. Implement immutable domain types/invariants and explicit error codes.
3. Define Pydantic request/response and application input/output contracts.
4. Implement use case against injected ports, with fake/stub implementations for tests.
5. Add infrastructure adapters and persistence migrations only when needed.
6. Expose API endpoint, including auth/scope/error handling; update OpenAPI.
7. Regenerate TS API client, implement feature-local hooks/component(s), add accessible states.
8. Add unit, contract and integration/E2E tests for happy, ambiguous, unavailable, unsafe and unauthorized paths.
9. Run format, lint, typecheck, tests and security checks; update docs and ADR if architecture changed.
10. Report exact files changed, commands run, test outputs, implemented vs mocked features and remaining limitations.

## Mandatory code conventions

### Python backend

- Use typed Python and Pydantic v2 for boundary DTOs. Use Python `Protocol` for ports when abstraction actually helps testing/replaceability.
- Prefer methods/functions with one responsibility. Keep business rules pure where possible. No circular imports.
- Use async for network/DB operations and concurrency controls for external APIs. Manage client lifetime, timeouts and resource closure explicitly.
- Use SQLAlchemy 2.x patterns with repository and Unit of Work. DB transactions surround coherent business operations; no half-persisted claim approvals.
- Use `structlog` or standard structured logging with a privacy redaction layer; no full prompts in logs.
- Use Ruff, static type checking, pytest. Define settings via validated environment model; no embedded secrets.
- Use specific errors (`EntityAmbiguous`, `EvidenceInsufficient`, `PolicyRestricted`) and map to stable API error codes.

### TypeScript frontend

- Strict TypeScript: no widespread `any`, unchecked JSON casts, or duplicated DTO definitions.
- Use React components with accessible semantics, strong prop interfaces, error boundaries and keyboard alternatives.
- Server data via generated API client; state synchronized by TanStack Query or equivalent. Keep React contexts narrow.
- Lazy-load heavy WebGL visualization engines with SSR disabled only for client-only renderers.
- Share renderer interface, not concrete UI implementations. A renderer must only use approved `SceneSpec` data.
- Always include `EvidenceOnlyScene` safe fallback and clear `experimental/predicted/schematic` labels.

### Test quality

- Do not skip or delete failing tests to obtain green CI.
- Any positive biomedical fixture must include real source metadata **or** explicitly state synthetic/testing-only status.
- Test invalid, ambiguous, user-cancelled, provider-outage and safety-blocked cases.
- Every privacy-sensitive read/write has a cross-user authorization test.
- Every agent skill has a schema validation test and an injected-instruction resistance test.
- Every scene renderer has an unsupported schema/fallback test.
- Tests should be deterministic by default; separate optional online integration tests.

## Common traps to avoid

- Creating a `medical_ai_agent.py` containing OCR, RxNorm, graphs, safety and rendering logic.
- Building 15 agent classes that all send full conversation history to a provider.
- Writing an LLM prompt to decide clinical safety without deterministic blocking rules.
- Calling a structure viewer with a generated fictional PDB identifier.
- Mapping all biomedical relations into a generic `RELATED_TO` edge.
- Calling ambiguous drug OCR a confirmed medication.
- Giving invented probabilities for patient skin-image diagnoses or answer reliability.
- Storing raw uploaded images in Postgres JSON or logging them in traceback output.
- Compiling arbitrary model output as TSX/JavaScript.
- Adding open-ended “search the web” tools without source selection, limits and provenance.
- Pre-creating hundreds of empty classes; implement per phase with real tests.

## Codex workflow control

- Implement **one phase at a time** from the plan, and stop at its acceptance gate. Do not leap ahead and mark later features completed.
- Before changing architecture, add/update an ADR with rationale, alternatives and migration impact.
- If an external key, dataset license or validation approval is missing: use a clearly labeled demo/stub feature under `DEMO_MODE`, document it, and do not claim live production integration.
- After each phase, append `docs/implementation-status.md` with:
  - implemented components and exact paths;
  - tests and observed command output;
  - fixture vs live integrations;
  - unresolved requirements, safety blockers and next phase.
- Use simple, locally runnable defaults and supply `make bootstrap`, `make dev`, `make test`, `make check` targets.

## Completion criteria

The codebase is **not** complete merely because folders and components exist. Completion means the documented user journeys work against real verified or transparently demo data; evidence validation and safety gates enforce restrictions; provider outages and ambiguous identities fail safely; users can view evidence-backed scenes; automated tests and local developer bootstrap work; and known production/legal limitations are documented.
