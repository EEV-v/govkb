import { CapabilitySummary, TreeRow } from "../types";

function capabilityPath(capability: CapabilitySummary, governedRoot?: string): string | undefined {
  return capability.path ?? (governedRoot ? `${governedRoot}/capabilities/${capability.id}` : undefined);
}

function capabilityDisplayName(capability: CapabilitySummary): string {
  return capability.name?.trim() || capability.id;
}

function capabilityDescription(capability: CapabilitySummary): string {
  const parts = [
    capabilityDisplayName(capability) !== capability.id ? capability.id : undefined,
    capability.lifecycleState ?? undefined,
    capability.memoryEnabled ? "memory" : "no memory",
    capability.requiresExplicitAcceptance ? "explicit acceptance" : undefined,
    capability.migrationStatus ? capability.migrationStatus : undefined
  ].filter(Boolean);
  return parts.join(", ");
}

function capabilityTooltip(capability: CapabilitySummary, sourcePath?: string): string {
  const memoryTargets = (capability.memoryTargets ?? [])
    .map((target) => `${target.name}: ${target.path}${target.sections.length > 0 ? ` (${target.sections.length} section(s))` : ""}`)
    .join("\n");
  return [
    capabilityDisplayName(capability),
    capability.description,
    `ID: ${capability.id}`,
    capability.lifecycleState ? `State: ${capability.lifecycleState}` : undefined,
    capability.migrationStatus ? `Migration: ${capability.migrationStatus}` : undefined,
    capability.aliases && capability.aliases.length > 0 ? `Aliases: ${capability.aliases.join(", ")}` : undefined,
    memoryTargets ? `Memory targets:\n${memoryTargets}` : undefined,
    sourcePath ? `Path: ${sourcePath}` : undefined
  ]
    .filter(Boolean)
    .join("\n");
}

export function capabilityRows(capabilities?: CapabilitySummary[], governedRoot?: string): TreeRow[] {
  if (!capabilities) {
    return [
      {
        label: "Governed skills not loaded",
        description: "Run Show Status",
        tooltip: "Governed skills are loaded from govkb status --json.",
        icon: "book",
        command: { command: "govkb.showStatus", title: "GovKB: Show Status" }
      },
      {
        label: "Convert one skill",
        description: "Choose source skill",
        tooltip: "Convert one chosen local Codex skill name, folder, or SKILL.md file into a governed capability package.",
        icon: "new-folder",
        command: { command: "govkb.convertSkillToGoverned", title: "GovKB: Convert One Existing Skill To Governed" }
      }
    ];
  }
  if (capabilities.length === 0) {
    return [
      {
        label: "No governed skills",
        description: "Run setup",
        tooltip: "Initialize or repair the governed package through the GovKB CLI.",
        icon: "warning",
        command: { command: "govkb.oneClickSetup", title: "GovKB: One-Click Setup Current Project" }
      },
      {
        label: "Convert one skill",
        description: "Choose source skill",
        tooltip: "Convert one chosen local Codex skill name, folder, or SKILL.md file into a governed capability package.",
        icon: "new-folder",
        command: { command: "govkb.convertSkillToGoverned", title: "GovKB: Convert One Existing Skill To Governed" }
      }
    ];
  }
  return [
    {
      label: "Governed skills",
      description: `${capabilities.length} available`,
      tooltip: "Open, rename, merge, or convert governed skills from this view.",
      icon: "book",
      command: { command: "govkb.refreshCapabilities", title: "GovKB: Refresh Governed Skills" }
    },
    {
      label: "Convert one skill",
      description: "Choose source skill",
      tooltip: "Convert one chosen local Codex skill name, folder, or SKILL.md file into a governed capability package.",
      icon: "new-folder",
      command: { command: "govkb.convertSkillToGoverned", title: "GovKB: Convert One Existing Skill To Governed" }
    },
    ...capabilities.map((capability) => {
      const sourcePath = capabilityPath(capability, governedRoot);
      return {
        label: capabilityDisplayName(capability),
        description: capabilityDescription(capability),
        tooltip: capabilityTooltip(capability, sourcePath),
        command: { command: "govkb.openCapability", title: "GovKB: Open Governed Skill", arguments: [capability] },
        icon: capability.memoryEnabled ? "symbol-method" : "file",
        contextValue: "govkb.capability"
      };
    })
  ];
}
