"use client";

import { FormEvent, useState } from "react";

import { ClaimCard } from "@/features/evidence/components/ClaimCard";
import { ReliabilityPanel } from "@/features/reliability/components/ReliabilityPanel";
import { SkinObservationPanel } from "@/features/skin/components/SkinObservationPanel";
import { SceneHost } from "@/renderers/registry";
import type { components } from "@/shared/api/generated/schema";
import { apiClient, uploadAssetContent } from "@/shared/api/client";
import { apiErrorMessage } from "@/shared/api/errors";

type Session = components["schemas"]["SessionResponse"];
type Candidate = components["schemas"]["MedicineCandidateResponse"];
type ConfirmedMedication = components["schemas"]["ConfirmedMedicationResponse"];
type Run = components["schemas"]["RunResponse"];
type Claim = components["schemas"]["ClaimResponse"];
type Scene = components["schemas"]["SceneSpecResponse"];
type Asset = components["schemas"]["AssetResponse"];
type ReliabilityReport = components["schemas"]["ReliabilityReportResponse"];

export function ExplorationWorkspace() {
  const [session, setSession] = useState<Session | null>(null);
  const [medicineName, setMedicineName] = useState("");
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [confirmed, setConfirmed] = useState<ConfirmedMedication[]>([]);
  const [question, setQuestion] = useState("");
  const [run, setRun] = useState<Run | null>(null);
  const [scene, setScene] = useState<Scene | null>(null);
  const [claim, setClaim] = useState<Claim | null>(null);
  const [reliability, setReliability] = useState<ReliabilityReport | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [sensitiveConsent, setSensitiveConsent] = useState(false);
  const [uploadedAsset, setUploadedAsset] = useState<Asset | null>(null);
  const [notice, setNotice] = useState("Create a private demo session to begin.");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function createSession() {
    setBusy(true);
    setError(null);
    const { data, error: apiError } = await apiClient.POST("/api/v1/sessions", {
      body: { title: "Private learning session" },
    });
    setBusy(false);
    if (!data) {
      setError(apiErrorMessage(apiError, "The private session could not be created."));
      return;
    }
    setSession(data);
    setNotice("Private demo session created. Medicine identities remain unconfirmed until you choose one.");
  }

  async function refreshCandidates(sessionId: string) {
    const { data, error: apiError } = await apiClient.GET(
      "/api/v1/sessions/{session_id}/entity-candidates",
      { params: { path: { session_id: sessionId } } },
    );
    if (!data) {
      setError(apiErrorMessage(apiError, "Candidate records could not be loaded."));
      return;
    }
    setCandidates(data.candidates);
    setConfirmed(data.confirmed);
  }

  async function addMedicine(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !medicineName.trim()) return;
    setBusy(true);
    setError(null);
    const { data, error: apiError } = await apiClient.POST(
      "/api/v1/sessions/{session_id}/medicine-items",
      {
        params: { path: { session_id: session.id } },
        body: { label: medicineName.trim() },
      },
    );
    setBusy(false);
    if (!data) {
      setError(apiErrorMessage(apiError, "The medicine item could not be added."));
      return;
    }
    setMedicineName("");
    setNotice("Candidate added. Confirm it explicitly before any evidence workflow can begin.");
    await refreshCandidates(session.id);
  }

  async function confirmCandidate(candidate: Candidate) {
    if (!session) return;
    setBusy(true);
    setError(null);
    const { data, error: apiError } = await apiClient.POST(
      "/api/v1/sessions/{session_id}/confirm-entities",
      {
        params: { path: { session_id: session.id } },
        body: { candidate_id: candidate.id, expected_session_version: session.version },
      },
    );
    setBusy(false);
    if (!data) {
      setError(apiErrorMessage(apiError, "The candidate could not be confirmed. Refresh and try again."));
      return;
    }
    setSession({ ...session, version: session.version + 1 });
    setNotice("Identity confirmed by you. This does not mean the medicine is being taken or medically appropriate.");
    await refreshCandidates(session.id);
  }

  async function waitForRun(runId: string): Promise<Run | null> {
    for (let attempt = 0; attempt < 16; attempt += 1) {
      const { data } = await apiClient.GET("/api/v1/runs/{run_id}", {
        params: { path: { run_id: runId } },
      });
      if (data && !["RECEIVED", "RUNNING", "VERIFYING", "COMPILING"].includes(data.status)) {
        return data;
      }
      await new Promise((resolve) => window.setTimeout(resolve, 250));
    }
    return null;
  }

  async function openClaim(claimId: string) {
    const { data, error: apiError } = await apiClient.GET("/api/v1/claims/{claim_id}", {
      params: { path: { claim_id: claimId } },
    });
    if (!data) {
      setError(apiErrorMessage(apiError, "Claim provenance could not be loaded."));
      return;
    }
    setClaim(data);
  }

  async function uploadImage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !uploadFile || !sensitiveConsent) return;
    setBusy(true);
    setError(null);
    const { data: intent, error: apiError } = await apiClient.POST("/api/v1/assets/upload-intents", {
      body: {
        session_id: session.id,
        filename: uploadFile.name,
        content_type: uploadFile.type,
        consent_sensitive_processing: true,
      },
    });
    if (!intent) {
      setBusy(false);
      setError(apiErrorMessage(apiError, "The private upload intent could not be created."));
      return;
    }
    const uploaded = await uploadAssetContent(intent.content_endpoint, intent.upload_token, uploadFile);
    setBusy(false);
    if (!uploaded.data) {
      setError(apiErrorMessage(uploaded.error, "The selected image could not be securely uploaded."));
      return;
    }
    setUploadedAsset(uploaded.data);
    setNotice("Private image uploaded with consent. It remains an input, not a diagnosis or confirmation.");
  }

  async function startExploration(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !question.trim()) return;
    setBusy(true);
    setError(null);
    setScene(null);
    setClaim(null);
    setReliability(null);
    const { data, error: apiError } = await apiClient.POST("/api/v1/runs", {
      body: { session_id: session.id, question: question.trim() },
    });
    if (!data) {
      setBusy(false);
      setError(apiErrorMessage(apiError, "The exploration run could not be started."));
      return;
    }
    setRun(data);
    setNotice("The workflow is checking identity, safety policy, provenance, and scene validity.");
    const finished = await waitForRun(data.id);
    setBusy(false);
    if (!finished) {
      setNotice("The run is still processing. Reopen the session to inspect its final state.");
      return;
    }
    setRun(finished);
    if (finished.status === "WAITING_FOR_CONFIRMATION") {
      setNotice("Confirm a medicine identity first. The system will not infer a mechanism from an unconfirmed name.");
      return;
    }
    if (finished.status === "SAFETY_ESCALATION") {
      setNotice("This request needs timely in-person medical assessment. The educational workflow was stopped.");
      return;
    }
    const { data: sceneList } = await apiClient.GET("/api/v1/runs/{run_id}/scenes", {
      params: { path: { run_id: finished.id } },
    });
    const selectedScene = sceneList?.items[0];
    if (selectedScene) {
      const { data: sceneData } = await apiClient.GET("/api/v1/scenes/{scene_id}", {
        params: { path: { scene_id: selectedScene.id } },
      });
      if (sceneData) {
        setScene(sceneData);
        await openClaim(sceneData.claim_ids[0]);
      }
    }
    const { data: report } = await apiClient.GET("/api/v1/runs/{run_id}/reliability", {
      params: { path: { run_id: finished.id } },
    });
    if (report) setReliability(report);
    setNotice("The available result is a clearly labelled synthetic fixture, not a scientific or clinical conclusion.");
  }

  return (
    <section className="workspace-grid" aria-labelledby="workspace-heading">
      <aside className="workspace-panel intake-panel">
        <p className="eyebrow">Private intake</p>
        <h1 id="workspace-heading">Build an evidence request</h1>
        <p className="panel-copy">
          This local demo uses an isolated development identity. It never treats a typed or OCR-derived
          medicine as confirmed until you explicitly select it.
        </p>
        {!session ? (
          <button className="primary-button" disabled={busy} onClick={createSession} type="button">
            {busy ? "Creating private session…" : "Create private demo session"}
          </button>
        ) : (
          <>
            <p className="status-line"><strong>Session:</strong> private and owner-scoped</p>
            <form onSubmit={addMedicine}>
              <label htmlFor="medicine">Medicine name or combination</label>
              <input
                id="medicine"
                onChange={(event) => setMedicineName(event.target.value)}
                placeholder="e.g. acetaminophen + caffeine"
                value={medicineName}
              />
              <button className="primary-button" disabled={busy || !medicineName.trim()} type="submit">
                Add as an unconfirmed candidate
              </button>
            </form>
            <form onSubmit={uploadImage}>
              <label htmlFor="private-image">Optional private image</label>
              <input
                accept="image/jpeg,image/png,image/webp"
                id="private-image"
                onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)}
                type="file"
              />
              <label className="consent-row" htmlFor="sensitive-consent">
                <input
                  checked={sensitiveConsent}
                  id="sensitive-consent"
                  onChange={(event) => setSensitiveConsent(event.target.checked)}
                  type="checkbox"
                />
                I consent to private sensitive-image processing for this session.
              </label>
              <button
                className="secondary-button"
                disabled={busy || !uploadFile || !sensitiveConsent}
                type="submit"
              >
                Upload private image
              </button>
              {uploadedAsset ? <p className="status-line">Image ready: {uploadedAsset.original_filename}</p> : null}
            </form>
            <form onSubmit={startExploration}>
              <label htmlFor="question">Educational question</label>
              <textarea
                id="question"
                name="question"
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="What established science can be explored?"
                rows={4}
                value={question}
              />
              <button className="secondary-button" disabled={!question.trim() || busy} type="submit">
                {busy ? "Checking the workflow…" : "Start educational exploration"}
              </button>
            </form>
          </>
        )}
        {run ? <p className="status-line">Workflow status: <strong>{run.status.replaceAll("_", " ")}</strong></p> : null}
        {error ? <p className="error-message" role="alert">{error}</p> : null}
      </aside>

      <section className="workspace-panel viewer-panel" aria-labelledby="viewer-heading">
        <p className="eyebrow">Scientific viewer</p>
        {scene ? <SceneHost onOpenEvidence={(claimId) => void openClaim(claimId)} scene={scene} /> : <div className="viewer-orb" aria-hidden="true" />}
        <h2 id="viewer-heading">Evidence appears only after verification</h2>
        <p>{notice}</p>
        <div className="safety-notice">
          <strong>Educational boundary</strong>
          <span>No diagnosis, dose, medication change, or patient-specific molecular conclusion is available.</span>
        </div>
      </section>

      <aside className="workspace-panel evidence-panel" aria-labelledby="evidence-heading">
        <p className="eyebrow">Identity and evidence</p>
        <h2 id="evidence-heading">Confirm before exploring</h2>
        {candidates.length === 0 ? (
          <p className="panel-copy">No candidates yet. Add a medicine name to keep its status visible.</p>
        ) : (
          <ul className="candidate-list">
            {candidates.map((candidate) => (
              <li key={candidate.id}>
                <strong>{candidate.label}</strong>
                <span>{candidate.ingredients.join(" + ")}</span>
                <small>{candidate.provenance.replaceAll("_", " ")}</small>
                {candidate.status === "CANDIDATE" ? (
                  <button
                    className="text-button"
                    disabled={busy || !session}
                    onClick={() => void confirmCandidate(candidate)}
                    type="button"
                  >
                    Confirm this identity
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        )}
        {confirmed.length ? (
          <div className="confirmed-list">
            <p className="eyebrow">User confirmed</p>
            {confirmed.map((item) => <p key={item.id}>{item.label}</p>)}
          </div>
        ) : null}
        {claim ? <ClaimCard claim={claim} /> : null}
        {reliability ? <ReliabilityPanel report={reliability} /> : null}
        {session ? <SkinObservationPanel asset={uploadedAsset} sessionId={session.id} /> : null}
      </aside>
    </section>
  );
}
