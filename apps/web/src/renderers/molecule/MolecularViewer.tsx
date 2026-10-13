import type { RendererProps } from "@/renderers/types";

export function MolecularViewer({ scene, onOpenEvidence }: RendererProps) {
  const structure = scene.structure;
  if (!structure) {
    return (
      <section className="molecule-fallback">
        <p>No verified structure record is available for this evidence. A molecular model is not fabricated.</p>
        <button onClick={() => onOpenEvidence(scene.claim_ids[0])} type="button">
          Open evidence instead
        </button>
      </section>
    );
  }
  return (
    <section className="molecule-fallback">
      <p>Verified structure identifier: <strong>{structure.pdb_id}</strong></p>
      <p>A verified structure viewer is not bundled until its dependency policy is approved.</p>
      <a href={structure.source_url} rel="noreferrer" target="_blank">Open the verified RCSB structure record</a>
      <button onClick={() => onOpenEvidence(scene.claim_ids[0])} type="button">
        Inspect linked evidence
      </button>
    </section>
  );
}
