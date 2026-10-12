import type { Metadata } from "next";
import type { ReactNode } from "react";

import "@/shared/styles/globals.css";

export const metadata: Metadata = {
  title: "BioScope AI | Evidence-grounded biomedical learning",
  description: "An educational biomedical explorer. Phase 0 platform preview.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main-content">
          Skip to main content
        </a>
        {children}
      </body>
    </html>
  );
}
