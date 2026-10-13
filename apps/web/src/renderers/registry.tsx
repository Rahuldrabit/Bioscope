"use client";

import type { ReactNode } from "react";

import { AnatomyViewer } from "@/renderers/anatomy/AnatomyViewer";
import { EvidenceOnlyScene } from "@/renderers/fallback/EvidenceOnlyScene";
import { GraphViewer } from "@/renderers/graph/GraphViewer";
import { MolecularViewer } from "@/renderers/molecule/MolecularViewer";
import type { RendererProps, SceneSpec } from "@/renderers/types";

const renderers: Record<SceneSpec["kind"], (props: RendererProps) => ReactNode> = {
  interaction_network: GraphViewer,
  evidence_table: EvidenceOnlyScene,
  molecular_structure: MolecularViewer,
  skin_layer: AnatomyViewer,
};

export function SceneHost(props: RendererProps) {
  const Renderer = renderers[props.scene.kind] ?? EvidenceOnlyScene;
  return <Renderer {...props} />;
}
