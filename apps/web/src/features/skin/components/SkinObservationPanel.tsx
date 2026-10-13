"use client";

import { FormEvent, useState } from "react";

import type { components } from "@/shared/api/generated/schema";
import { apiClient } from "@/shared/api/client";
import { apiErrorMessage } from "@/shared/api/errors";

type Asset = components["schemas"]["AssetResponse"];
type SkinObservation = components["schemas"]["SkinObservationResponse"];

type Props = {
  sessionId: string;
  asset: Asset | null;
};

export function SkinObservationPanel({ sessionId, asset }: Props) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<SkinObservation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!asset || !question.trim()) return;
    setBusy(true);
    setError(null);
    const { data, error: apiError } = await apiClient.POST(
      "/api/v1/sessions/{session_id}/skin-observations",
      {
        params: { path: { session_id: sessionId } },
        body: { asset_id: asset.id, question: question.trim() },
      },
    );
    setBusy(false);
    if (!data) {
      setError(apiErrorMessage(apiError, "The restricted skin observation could not be requested."));
      return;
    }
    setResult(data);
  }

  return (
    <section className="skin-panel" aria-label="Optional skin observation">
      <p className="eyebrow">Opt-in skin photo</p>
      <p>
        This feature is disabled unless the server owner explicitly enables it. It never diagnoses
        a photo or infers a personal molecular state.
      </p>
      <form onSubmit={submit}>
        <label htmlFor="skin-question">Question about the uploaded image</label>
        <textarea
          disabled={!asset}
          id="skin-question"
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask for educational limits, not a diagnosis"
          rows={3}
          value={question}
        />
        <button className="secondary-button" disabled={!asset || !question.trim() || busy} type="submit">
          {busy ? "Checking safety…" : "Request restricted observation"}
        </button>
      </form>
      {!asset ? <p className="panel-copy">Upload a consented image first.</p> : null}
      {error ? <p className="error-message" role="alert">{error}</p> : null}
      {result ? (
        <div className="skin-result">
          <strong>{result.status.replaceAll("_", " ")}</strong>
          <p>{result.guidance}</p>
          <ul>{result.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
      ) : null}
    </section>
  );
}
