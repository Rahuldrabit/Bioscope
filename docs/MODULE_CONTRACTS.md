# BioScope AI — Module Ownership and Interface Contracts

**Companion to:** `BIOSCOPE_MASTER_ARCHITECTURE.md`  
**Purpose:** Reduce AI-generated-code coupling by assigning explicit ownership, dependencies, public use cases, persistent records, and test suites to each module.  
**Interpretation:** These are suggested file names / module interfaces. Implement incrementally as Phase gates require. Do not mass-create empty modules.

## 1. Backend domain-module template

A domain module can be implemented as:

```text
modules/<domain>/
  domain/
    models.py             # pure aggregates/value objects, invariants
    events.py             # typed domain events (if needed)
    errors.py             # domain-specific failure conditions
  application/
    commands.py           # command DTOs
    queries.py            # query DTOs
    ports.py              # required external interfaces
    use_cases.py          # boundary operations; may split by use case
  infrastructure/
    repository.py         # SQLAlchemy mapped repository
    mapping.py            # persistence-to-domain conversion
  api/
    router.py             # FastAPI routes, auth dependencies
    schemas.py            # Pydantic transport DTOs
  tests/                  # actual tests live in service's central tests tree
```

A **port** describes a required capability; an adapter implements it. Example:

```python
from typing import Protocol

class MedicineCatalog(Protocol):
    async def search(self, query: str, *, limit: int) -> list["MedicineCandidate"]: ...
    async def get_product(self, product_id: str) -> "MedicineProduct | None": ...

class ConfirmMedication:
    def __init__(self, repo: "MedicineRepository", catalog: MedicineCatalog):
        self.repo = repo
        self.catalog = catalog

    async def execute(self, cmd: "ConfirmMedicationCommand") -> "ConfirmedMedication":
        # validate owner/confirmation and store via Unit of Work; implementation TBD
        ...
```

Do **not** have `ConfirmMedication` fetch OCR directly; OCR is handled by the upload/extraction workflow and outputs candidates.

## 2. Ownership matrix

| Module | Owns data | Public application use cases | Emits | Forbidden direct dependency |
|---|---|---|---|---|
| `accounts` | owner identity, consent record metadata | GetUser, UpdateConsent, DeleteAccountRequest | ConsentUpdated | raw biomedical claims |
| `sessions` | session, message, selected entity/scene pointers | CreateSession, AddMessage, GetSession, DeleteSession | SessionDeleted, MessageAdded | external biomedical APIs |
| `uploads` | asset metadata, sanitization, retention | CreateUploadIntent, CompleteUpload, GetAsset, DeleteAsset | UploadValidated, AssetDeleted | drug-confirmation business logic |
| `medicines` | candidate and confirmed medicine records | RecognizeCandidates, ConfirmMedication, ListMedicationItems | MedicationConfirmed | cross-domain ORM tables |
| `biomedical_knowledge` | canonical entities, identifiers, relationship ontology | ResolveEntity, SearchKnownRelations, GetEntityGraph | EntityNormalized | unrestricted inference from graph path |
| `evidence` | sources, snapshots, claims, link provenance, adjudication | FetchSource, ProposeClaim, VerifyLink, GetClaim | EvidenceApproved, EvidenceDeprecated | scene renderer implementation |
| `agent_workflows` | plans, tasks, checkpoints, run metadata | StartRun, CancelRun, GetRun, StreamEvents | RunAdvanced, RunCompleted | concrete provider SDK in domain logic |
| `safety` | policy versions, safety verdict records | Preflight, PreRelease, AuthorizeSkill | SafetyBlocked | treating Planner output as authority |
| `reliability` | assessment reports, calibration registry | AssessClaims, GetReliabilityReport | ReliabilityReady | arbitrary numeric LLM confidence |
| `visualization` | compiled scenes and approval state | CompileScene, ValidateScene, GetScene | SceneApproved | frontend React/Mol* internals |

### Allowed cross-module interfaces

- `agent_workflows` invokes `medicines`, `biomedical_knowledge`, `evidence`, `safety`, `reliability` and `visualization` **application ports**, not their `infrastructure` internals.
- `medicines` depends on a `MedicineCatalog` adapter port owned by its application layer; `connectors` implement it.
- `visualization` consumes an `ApprovedClaimReader` and `ApprovedAssetReader` application interface; it must not independently guess facts.
- `evidence` can request identity resolution through a `CanonicalEntityResolver` port.
- `safety` can evaluate request/result metadata through defined typed DTOs, but is not given blanket access to raw user uploads.
- `accounts` and `sessions` implement authorization checks, not medical decision logic.
- `agent_workflows` owns the **run lifecycle**, not the truth of an evidence claim. The evidence module owns truth/provenance statuses.

## 3. Application-level use case examples

### 3.1 Upload completion

`CompleteUpload(asset_id, owner_id, etag)`:

1. Enforce ownership and existing upload intent.
2. Check object exists, size/digest/MIME/magic bytes.
3. Sanitize/scan safely; remove metadata where allowed.
4. Transition asset `PENDING_UPLOAD → SCANNING → READY | REJECTED`.
5. Enqueue extraction only after `READY` and valid consent.
6. Return asset ID/status; never return raw permanent storage key.

Idempotence: multiple completion calls with same validated digest return same state; mismatched digest returns conflict.

### 3.2 Medicine confirmation

`ConfirmMedication(session_id, candidate_id, confirmed_entity_or_product_id, user_id, expected_session_version)`:

1. Check user ownership, candidate-session linkage and version.
2. Display normalized ingredient(s), strength/form/route when known.
3. Require explicit confirmation action; no OCR auto-confirm path.
4. Commit confirmed drug identity and evidence/source record for mapping.
5. Publish `MedicationConfirmed`, invalidate dependent runs/scenes if identity changed.

Do not store dosage adherence or prescribing information unless necessary and consented; the initial educational flow does not need personal regimen details.

### 3.3 Evidence claim approval

`AdjudicateClaim(claim_id, verifier_result, evidence_ids, evidence_policy_version)`:

1. Validate normalized predicate/domain/range and biological context.
2. Validate source snapshots/references and cited passage mapping.
3. Reject pure association→causation, context mismatch and missing source.
4. Save a new claim evaluation version; do not mutate previous source snapshots.
5. Commit and enqueue projection update through transactional outbox.

The verifier does not write raw SQL or create new sources without using controlled service ports.

### 3.4 Run creation and progress

`StartRun(session_id, message_id, assets, entity_ids, user_id)`:

1. Authorization and quota check.
2. Gate requested purpose/risk and input consent.
3. Persist `RECEIVED` and idempotency key in transaction.
4. Enqueue worker with run ID only; API returns `202`.
5. Worker transitions states through typed events; UI rehydrates from canonical state after disconnect.

An SSE connection should not be required for the run to finish.

### 3.5 Compile and release scene

`CompileScene(run_id, approved_claim_ids, scene_request)`:

1. Ensure verifier outputs and approval state are committed.
2. Resolve renderer capabilities and supported source-backed assets.
3. Generate declarative scene only; schema validation.
4. Re-run claim/scoping checks after compilation, including tooltips/narration.
5. Persist approved scene and surface fallback if necessary.

An LLM's proposed scene plan cannot bypass this use case.

## 4. Typed artifact envelopes between agents

Every agent must consume and produce envelope DTOs carrying execution metadata:

```json
{
  "artifact_id": "art_example",
  "artifact_type": "CLAIM_CANDIDATE_SET",
  "schema_version": "1.0",
  "created_by": {
    "agent_id": "molecular_specialist",
    "agent_version": "1.0",
    "model_alias": "provider-configured-model",
    "prompt_version": "molecular-v1"
  },
  "run_id": "run_example",
  "task_id": "task_example",
  "input_artifact_ids": ["art_parent"],
  "source_snapshot_ids": ["source_snapshot_1"],
  "payload": {"candidate_claim_ids": ["claim_candidate_1"]}
}
```

The `created_by` metadata proves execution provenance, **not scientific correctness**. Approval is separate. Schema incompatibility is a typed failure, not silently coerced JSON.

## 5. Agent instructions and budgets

### Planner

Inputs: user goal, selected objects, policy-enforced tool inventory, current workflow status and missing details.  
Outputs: `TaskPlan` with typed DAG and budgets.  
Allowed actions: select approved skills, request a narrow clarification, choose bounded replan.  
Forbidden: invent skill, invent citations, override clinical safety, promote candidate identity to confirmed.

### Specialists

Inputs: normalized task and accessible source tools.  
Outputs: typed observations/claim candidates with source refs.  
Forbidden: claim correctness verdict on own proposal; cross-user data access; treat provider text as instruction.

### Independent Scientific Verifier

Inputs: candidate claims, source refs and additional authorized source-checking tools.  
Outputs: per-claim verdict, contradictions, missing-context reason codes.  
Forbidden: convert low-source coverage into “likely true” solely based on model fluency.

### Reliability Agent

Inputs: verifier result, source grade/directness, task evidence coverage, identity status, scene schema result, calibration-model status.  
Outputs: reliability DTO.  
Forbidden: use uncalibrated invented numeric score, override safety gate, claim a diagnosis was established by an image.

### Visual Planner

Inputs: approved claim IDs, media/structure references, viewer registry, target detail level.  
Outputs: `ScenePlan` with ordered renderer kinds.  
Forbidden: HTML/JS/CSS generation, unsupported structure IDs, causal arrow from associations.

### Explainer

Inputs: approved claims, uncertainty records, scene labels, source references.  
Outputs: paragraphs, annotations, tooltips referenced to claim IDs.  
Forbidden: untracked factual sentences, inventing image-inferred patient molecular pathways.

**Budget policy:** per run max task nodes, max parallel specialists, timeouts, maximum controlled replans, user/plan-specific token ceilings. Configure in `skills/policies/limits.py` and verify in DAG executor; never let model choose unbounded limits.

## 6. Domain invariants and authorization constraints

- A claim ID points to one normalized proposition with versioned evaluations. Each proposition has explicit biological context.
- Scene release requires every non-decorative mechanistic edge to cite an approved claim; purely illustrative anatomical contours may have reviewed asset provenance instead.
- A product can have zero or multiple active ingredients. Brand identity is not sufficient to determine formulation without source and user confirmation.
- A confirmed medicine in session A does not imply the user actually takes it.
- A skin image is a user-provided observation, not disease ground truth.
- Evidence `SUPPORTED` in one organism/cell context is not automatically `SUPPORTED` in human tissue.
- A machine-generated reliability assessment with no calibration model must have `numeric_probability=null`.
- Hard-stop safety outcome prohibits releasing ordinary clinical-recommendation content even if Planner suggested it.
- `owner_id` authorization applies to all session, upload, message, run, event stream and scene access. Scientific public entities can be globally readable if licensing permits.
- Deleting a session starts deletion of input assets, messages and personally linked derivatives according to retention policy; shared public-source snapshots remain if no personal data is embedded.

## 7. Failure-mode table (mandatory engineering tests)

| Failure | Domain error/result | User-facing behavior |
|---|---|---|
| Upload valid name but corrupted bytes | `UPLOAD_REJECTED` | Clear request for a new file |
| OCR returns several similar drugs | `ENTITY_CONFIRMATION_REQUIRED` | Candidate picker, no mechanism yet |
| External drug lookup times out | `SOURCE_UNAVAILABLE` | Retry/known-source explanation, labeled vintage |
| Drug map missing active ingredient | `EVIDENCE_INSUFFICIENT` | Do not infer pharmacological target |
| Missing structure for protein | `STRUCTURE_UNAVAILABLE` | Evidence graph or source card fallback |
| Claim evidence contradicts graph edge | `CLAIM_REJECTED` | No scene edge; status described |
| Existing case contains unconfirmed diagnosis | `UNCONFIRMED_CONTEXT` | Conditional, educational wording |
| User uploads rash photo with alarming features | `SAFETY_ESCALATION` | Appropriate medical assessment guidance |
| LLM emits unknown skill | `INVALID_PLAN` | Bounded replan or limited output |
| Verifier and specialist disagree | `CONFLICTING_EVIDENCE` | Withhold assertion or show dispute |
| Scene renderer fails in browser | `RENDERER_UNAVAILABLE` | Evidence-only fallback |
| Missing citation/scope for visual arrow | `SCENE_VALIDATION_FAILED` | Block scene and record testable error |
| LLM claims numeric confidence | `UNSUPPORTED_CONFIDENCE` | Strip and replace with honest status |
| User requests data deletion | `DELETION_REQUESTED` | Confirm and launch cleanup task; audit |

## 8. Demo versus live integration

Define adapters with two implementations where appropriate:

```text
MedicineCatalog
  ├── RxNormCatalogAdapter            (LIVE, source-checked)
  └── DemoMedicineCatalogAdapter      (DEMO, clearly marked)

LLMGateway
  ├── ConfiguredProviderAdapter       (LIVE only with credentials)
  └── DeterministicFakeLLM             (TEST/DEMO)

StructureRepository
  ├── RcsbStructureAdapter            (LIVE, verified ID)
  └── TestStructureFixtureRepository  (TEST, fixture metadata)
```

Set env-based DI assembly once in `bootstrap/container.py`; do not pepper `if DEMO_MODE` throughout business logic. `DEMO_MODE` must be clearly reflected in API result provenance and a visible UI banner. Disable demo fallbacks in production configurations.

## 9. Suggested file-by-file implementation owners

| File | Responsibility | Important test |
|---|---|---|
| `bootstrap/container.py` | Construct injected adapters, policy and runner | no live provider invoked in test mode |
| `shared/application/unit_of_work.py` | Transactional boundary port | rolls back on exception |
| `modules/uploads/application/use_cases.py` | Upload intent, finalize, delete | idempotent finalize and ownership |
| `modules/medicines/application/use_cases.py` | Candidate confirmation | ambiguity cannot auto-confirm |
| `modules/evidence/domain/models.py` | Source, claim and evidence invariants | rejected unsupported relation type |
| `modules/evidence/application/use_cases.py` | Verify/approve claim with audit | source refs always present |
| `agents/contracts/plans.py` | Task DAG schemas | cycles and missing prerequisites rejected |
| `agents/workflow/runner.py` | Checkpoints, execution, cancellation | resume after task interruption |
| `skills/registry.py` | Enumerate allowed skills | unknown names rejected |
| `skills/executor.py` | Permission and budget enforcement | blocked excessive permissions |
| `agents/verifier/claim_checks.py` | Edge and source entailment checks | association not causation |
| `agents/reliability/calibration.py` | Calibrated estimator interface | no estimator returns null probability |
| `scenes/compiler.py` | Scene construction from claim artifacts | source-less edge rejected |
| `scenes/validators.py` | Schema, asset and claim validation | arbitrary URL rejected |
| `renderers/registry.ts` | Static scene-kind-to-viewer lookup | unknown viewer falls back |
| `renderers/molecule/adapter.ts` | SceneSpec→MolViewSpec mapping | unsupported structure blocked |
| `features/evidence/components/ClaimCard.tsx` | Citation and validity display | scope visible and accessible |
| `features/reliability/components/ReliabilityPanel.tsx` | No false numeric precision | numeric null shows status |
| `features/intake/components/MedicationListEditor.tsx` | List-based input and ambiguous item state | combination ingredients preserved |

## 10. API schema evolution rules

- Every public DTO includes a documented schema version where long-lived artifacts are persisted.
- Breaking changes require `/api/v2` or compatible additive migration paths; generated clients must be built and checked against the correct OpenAPI version.
- Scene schema major version upgrades require either a migrator or fallback renderer.
- Never delete source snapshot identifiers referenced by published scene history before retention policy and source governance checks.
- All end-user routes use standardized error envelopes and explicit permission checks.

## 11. Suggested ADR entries

1. `0001-modular-monolith.md` — why a modular monolith fits early needs.
2. `0002-postgresql-canonical-evidence.md` — avoid graph dual-source-of-truth.
3. `0003-agent-capability-allowlist.md` — minimize unchecked autonomy.
4. `0004-scene-schema-and-renderer-registry.md` — portable scene descriptions.
5. `0005-reliability-without-uncalibrated-score.md` — scientific uncertainty.
6. `0006-sensitive-image-handling.md` — privacy and non-diagnostic posture.
7. `0007-provider-agnostic-model-gateway.md` — portable evaluated models.

---

The master architecture defines the overall target. This document defines **ownership and interfaces** so Codex can create a durable codebase through real vertical slices rather than producing disconnected scaffolding.
