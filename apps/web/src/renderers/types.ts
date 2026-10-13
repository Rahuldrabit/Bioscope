import type { components } from "@/shared/api/generated/schema";

export type SceneSpec = components["schemas"]["SceneSpecResponse"];

export type RendererProps = {
  scene: SceneSpec;
  onOpenEvidence: (claimId: string) => void;
};
