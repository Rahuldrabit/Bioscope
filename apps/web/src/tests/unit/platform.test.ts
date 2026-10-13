import { describe, expect, it } from "vitest";

import { platformState } from "@/shared/lib/platform";

describe("platform state", () => {
  it("keeps biomedical inference unavailable during controlled educational expansion", () => {
    expect(platformState).toMatchObject({
      phase: 6,
      biomedicalInferenceAvailable: false,
      demoMode: true,
    });
  });
});
