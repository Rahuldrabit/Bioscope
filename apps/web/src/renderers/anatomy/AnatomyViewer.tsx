import type { RendererProps } from "@/renderers/types";

export function AnatomyViewer({ scene, onOpenEvidence }: RendererProps) {
  return (
    <section aria-label="Educational anatomy schematic" className="anatomy-viewer">
      <svg role="img" aria-label="General skin-layer educational schematic" viewBox="0 0 420 180">
        <rect fill="#f6d6c4" height="48" rx="8" width="380" x="20" y="15" />
        <rect fill="#efbfa4" height="50" rx="8" width="380" x="20" y="65" />
        <rect fill="#e6a47f" height="48" rx="8" width="380" x="20" y="117" />
        <text x="38" y="45">Epidermis · general anatomy</text>
        <text x="38" y="96">Dermis · general anatomy</text>
        <text x="38" y="148">Subcutaneous layer · general anatomy</text>
      </svg>
      <p>Illustrative educational schematic, not a patient image or diagnosis.</p>
      {scene.claim_ids[0] ? (
        <button onClick={() => onOpenEvidence(scene.claim_ids[0])} type="button">
          Inspect linked evidence
        </button>
      ) : null}
    </section>
  );
}
