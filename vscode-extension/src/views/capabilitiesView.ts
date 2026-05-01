import { CapabilitySummary, TreeRow } from "../types";

export function capabilityRows(capabilities?: CapabilitySummary[]): TreeRow[] {
  if (!capabilities) {
    return [
      {
        label: "Capabilities not loaded",
        description: "Run Show Status",
        tooltip: "Capabilities are loaded from govkb status --json.",
        command: { command: "govkb.showStatus", title: "GovKB: Show Status" }
      },
      {
        label: "Apply governed package",
        description: "Run One-Click Apply",
        tooltip: "Materialize current governed capabilities to Codex through the GovKB CLI.",
        command: { command: "govkb.oneClickApply", title: "GovKB: One-Click Apply Current Project" }
      }
    ];
  }
  if (capabilities.length === 0) {
    return [
      {
        label: "No capabilities in status",
        description: "Run setup",
        tooltip: "Initialize or repair the governed package through the GovKB CLI.",
        command: { command: "govkb.oneClickSetup", title: "GovKB: One-Click Setup Current Project" }
      }
    ];
  }
  return capabilities.map((capability) => ({
    label: capability.id,
    description: [capability.governed ? "governed" : "local", capability.memoryEnabled ? "memory" : undefined]
      .filter(Boolean)
      .join(", "),
    tooltip: capability.description || capability.name
  }));
}
