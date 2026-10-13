import type { RendererProps } from "@/renderers/types";

export function EvidenceOnlyScene({ scene, onOpenEvidence }: RendererProps) {
  return (
    <section aria-label="Evidence-only scene" className="evidence-only-scene">
      <p>This view does not infer a visual mechanism. Inspect the claim provenance directly.</p>
      <ul>
        {scene.claim_ids.map((claimId) => (
          <li key={claimId}>
            <button onClick={() => onOpenEvidence(claimId)} type="button">
              Open evidence record
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
