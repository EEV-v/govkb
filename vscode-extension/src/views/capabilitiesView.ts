import { CapabilitySummary, TreeRow } from "../types";

function capabilityPath(capability: CapabilitySummary, governedRoot?: string): string | undefined {
  return capability.path ?? (governedRoot ? `${governedRoot}/capabilities/${capability.id}` : undefined);
}

export function capabilityRows(capabilities?: CapabilitySummary[], governedRoot?: string): TreeRow[] {
  if (!capabilities) {
    return [
      {
        label: "Governed skills not loaded",
        description: "Run Show Status",
        tooltip: "Governed skills are loaded from govkb status --json.",
        command: { command: "govkb.showStatus", title: "GovKB: Show Status" }
      },
      {
        label: "Convert one skill",
        description: "Choose source skill",
        tooltip: "Convert one chosen local Codex skill name, folder, or SKILL.md file into a governed capability package.",
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
        command: { command: "govkb.oneClickSetup", title: "GovKB: One-Click Setup Current Project" }
      },
      {
        label: "Convert one skill",
        description: "Choose source skill",
        tooltip: "Convert one chosen local Codex skill name, folder, or SKILL.md file into a governed capability package.",
        command: { command: "govkb.convertSkillToGoverned", title: "GovKB: Convert One Existing Skill To Governed" }
      }
    ];
  }
  return [
    {
      label: "Governed skills",
      description: `${capabilities.length} available`,
      tooltip: "Open, rename, merge, or convert governed skills from this view.",
      command: { command: "govkb.refreshCapabilities", title: "GovKB: Refresh Governed Skills" }
    },
    {
      label: "Convert one skill",
      description: "Choose source skill",
      tooltip: "Convert one chosen local Codex skill name, folder, or SKILL.md file into a governed capability package.",
      command: { command: "govkb.convertSkillToGoverned", title: "GovKB: Convert One Existing Skill To Governed" }
    },
    ...capabilities.map((capability) => {
      const sourcePath = capabilityPath(capability, governedRoot);
      return {
        label: capability.id,
        description: [
          capability.memoryEnabled ? "memory" : "no memory",
          capability.lifecycleState ?? undefined,
          capability.migrationStatus ? `migration ${capability.migrationStatus}` : undefined
        ]
          .filter(Boolean)
          .join(", "),
        tooltip: [
          capability.name,
          capability.description,
          capability.aliases && capability.aliases.length > 0 ? `Aliases: ${capability.aliases.join(", ")}` : undefined,
          sourcePath
        ]
          .filter(Boolean)
          .join("\n"),
        command: { command: "govkb.openCapability", title: "GovKB: Open Governed Skill", arguments: [capability] },
        contextValue: "govkb.capability"
      };
    })
  ];
}
