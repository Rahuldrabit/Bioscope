import Link from "next/link";

const capabilities = [
  ["Evidence before visuals", "Future explanations will connect each scientific assertion to its source and scope."],
  ["Clear boundaries", "BioScope is educational software, not a diagnosis, treatment, or medication-dosing service."],
  ["Built for inspection", "Identity, evidence status, and known gaps will remain visible instead of being hidden behind a score."],
] as const;

export default function LandingPage() {
  return (
    <main id="main-content">
      <nav className="nav-shell" aria-label="Primary navigation">
        <Link className="wordmark" href="/">
          BioScope<span>AI</span>
        </Link>
        <Link className="text-link" href="/explore">
          Explore platform
        </Link>
      </nav>

      <section className="hero">
        <p className="eyebrow">Phase 0 · platform foundation</p>
        <h1>Explore biology with evidence in view.</h1>
        <p className="hero-copy">
          BioScope is being built as a source-grounded biomedical learning environment—from
          molecules to body systems—without pretending to diagnose or prescribe.
        </p>
        <div className="hero-actions">
          <Link className="primary-action" href="/explore">
            Open workspace preview
          </Link>
          <a className="secondary-action" href="#boundaries">
            Read the boundaries
          </a>
        </div>
        <div className="signal-grid" aria-label="Platform principles">
          <span>Source-linked</span>
          <span>Privacy-first</span>
          <span>Educational only</span>
        </div>
      </section>

      <section className="capability-section" aria-labelledby="principles-heading">
        <div>
          <p className="eyebrow">Design principles</p>
          <h2 id="principles-heading">A slower, more inspectable kind of AI.</h2>
        </div>
        <div className="capability-grid">
          {capabilities.map(([title, description], index) => (
            <article className="capability-card" key={title}>
              <span aria-hidden="true">0{index + 1}</span>
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="boundary-section" id="boundaries" aria-labelledby="boundaries-heading">
        <p className="eyebrow">Current scope</p>
        <h2 id="boundaries-heading">The platform is not making biomedical claims yet.</h2>
        <p>
          This initial build contains the web shell and API foundation only. Medicine recognition,
          uploads, source retrieval, scenes, and agent workflows are intentionally unavailable
          until their separately tested phases are implemented.
        </p>
      </section>
    </main>
  );
}
