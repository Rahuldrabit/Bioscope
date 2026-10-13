import type { RendererProps } from "@/renderers/types";

export function GraphViewer({ scene, onOpenEvidence }: RendererProps) {
  const nodes = scene.elements.slice(0, 6);
  return (
    <section aria-label="Evidence relationship graph" className="graph-viewer">
      <svg aria-hidden="true" viewBox="0 0 480 210">
        {scene.relations.map((relation, index) => (
          <line
            className="graph-edge"
            key={relation.id}
            x1={90 + (index % 2) * 40}
            x2={390 - (index % 2) * 40}
            y1={105}
            y2={105}
          />
        ))}
        {nodes.map((node, index) => (
          <g key={node.id} transform={`translate(${index % 2 === 0 ? 100 : 380}, ${70 + (index % 3) * 35})`}>
            <circle className="graph-node" r="24" />
            <text className="graph-node-label" textAnchor="middle" y="4">
              {node.kind.slice(0, 8)}
            </text>
          </g>
        ))}
      </svg>
      <ul className="graph-relation-list">
        {scene.relations.map((relation) => (
          <li key={relation.id}>
            <span>{relation.predicate.replaceAll("_", " ")}</span>
            <button onClick={() => onOpenEvidence(relation.claim_id)} type="button">
              Inspect claim
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
