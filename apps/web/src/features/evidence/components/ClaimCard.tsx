import type { components } from "@/shared/api/generated/schema";

type Claim = components["schemas"]["ClaimResponse"];

export function ClaimCard({ claim }: { claim: Claim }) {
  return (
    <article className="claim-card">
      <p className="eyebrow">{claim.provenance} · {claim.status}</p>
      <h3>{claim.subject_label} {claim.predicate.replaceAll("_", " ")}</h3>
      <p>Scope: {String(claim.context.scope ?? "not specified")}</p>
      <p className="claim-warning">
        {claim.provenance === "DEMO"
          ? "Synthetic testing fixture — not a biomedical conclusion."
          : "Evidence status shown with source provenance."}
      </p>
      <a href={claim.source.stable_url} rel="noreferrer" target="_blank">{claim.source.citation}</a>
      <small>Snapshot {claim.source.release_version} · source {claim.source.status}</small>
    </article>
  );
}
