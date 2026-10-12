import { describe, expect, it } from "vitest";

import { platformState } from "@/shared/lib/platform";

describe("platform state", () => {
  it("does not claim biomedical inference during Phase 0", () => {
    expect(platformState).toMatchObject({
      phase: 0,
      biomedicalInferenceAvailable: false,
      demoMode: true,
    });
  });
});
