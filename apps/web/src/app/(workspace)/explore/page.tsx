import Link from "next/link";

export default function ExplorePage() {
  return (
    <main className="workspace" id="main-content">
      <header className="workspace-header">
        <Link className="wordmark" href="/">
          BioScope<span>AI</span>
        </Link>
        <span className="demo-badge">DEMO PLATFORM</span>
      </header>
      <section className="workspace-grid" aria-labelledby="workspace-heading">
        <aside className="workspace-panel intake-panel">
          <p className="eyebrow">Input</p>
          <h1 id="workspace-heading">Start an exploration</h1>
          <p>
            Secure sessions, uploads, and scientific retrieval begin in later, separately tested
            phases.
          </p>
          <label htmlFor="question">Question</label>
          <textarea
            disabled
            id="question"
            name="question"
            placeholder="Question input is not available in Phase 0"
            rows={5}
          />
          <button disabled type="button">
            Begin when available
          </button>
        </aside>
        <section className="workspace-panel viewer-panel" aria-labelledby="viewer-heading">
          <div className="viewer-orb" aria-hidden="true" />
          <p className="eyebrow">Scientific viewer</p>
          <h2 id="viewer-heading">Waiting for verified evidence</h2>
          <p>
            No biomedical scene is shown until a future workflow has verified the required claims
            and provenance.
          </p>
        </section>
        <aside className="workspace-panel evidence-panel" aria-labelledby="evidence-heading">
          <p className="eyebrow">Evidence status</p>
          <h2 id="evidence-heading">No claims released</h2>
          <ul>
            <li>Identity status: not started</li>
            <li>Source retrieval: not started</li>
            <li>Clinical relevance: not assessed</li>
          </ul>
        </aside>
      </section>
    </main>
  );
}
