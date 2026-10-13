import Link from "next/link";

import { ExplorationWorkspace } from "@/features/intake/components/ExplorationWorkspace";

export default function ExplorePage() {
  return (
    <main className="workspace" id="main-content">
      <header className="workspace-header">
        <Link className="wordmark" href="/">
          BioScope<span>AI</span>
        </Link>
        <span className="demo-badge">DEMO PLATFORM</span>
      </header>
      <ExplorationWorkspace />
    </main>
  );
}
