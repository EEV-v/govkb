import { SkillUpdateState, StatusPayload, TreeRow } from "../types";

const skillUpdateLabels: Record<SkillUpdateState, string> = {
  current: "current",
  "not-applied": "not applied",
  "apply-available": "apply available",
  "workspace-changes": "workspace changes",
  "learned-updates": "learned updates",
  unknown: "unknown"
};

function skillUpdateDescription(status: StatusPayload): string {
  return skillUpdateLabels[status.skillUpdates.state] ?? "unknown";
}

function skillUpdateTooltip(status: StatusPayload): string {
  const codex = status.installState.codex;
  const updates = status.skillUpdates;
  const memory = updates.pendingLocalMemory;
  const memoryItems = memory.items.map((item) => {
    return `${item.capabilityId}: ${item.reason}, ${item.additions} addition(s)`;
  });
  return [
    `Codex install state: ${codex.status}`,
    `Skill update state: ${updates.state}`,
    updates.repoRevision ? `Repo revision: ${updates.repoRevision}` : undefined,
    updates.appliedRevision ? `Applied revision: ${updates.appliedRevision}` : undefined,
    updates.governedDirty ? "Governed package has local changes." : undefined,
    memory.available
      ? `Local memory pending: ${memory.pendingCount} item(s), ${memory.safePromotionCount} safe, ${memory.rejectedCount} rejected`
      : undefined,
    ...(status.project.governedStatus ?? []),
    ...memoryItems
  ]
    .filter(Boolean)
    .join("\n");
}

function skillUpdateCommand(status: StatusPayload): TreeRow["command"] {
  switch (status.skillUpdates.state) {
    case "current":
      return undefined;
    case "not-applied":
    case "apply-available":
      return { command: "govkb.oneClickApply", title: "GovKB: One-Click Apply Current Project" };
    case "learned-updates":
      return { command: "govkb.promoteAuto", title: "GovKB: Auto Promote Learned Updates" };
    case "workspace-changes":
    case "unknown":
      return { command: "govkb.showStatus", title: "GovKB: Show Status" };
  }
}

export function statusRows(status?: StatusPayload): TreeRow[] {
  if (!status) {
    return [
      {
        label: "Project status not loaded",
        description: "Run Show Status",
        tooltip: "Read the selected workspace through govkb status --json.",
        command: { command: "govkb.showStatus", title: "GovKB: Show Status" }
      },
      {
        label: "New project setup",
        description: "Run One-Click Setup",
        tooltip: "Initialize the selected workspace through the GovKB CLI.",
        command: { command: "govkb.oneClickSetup", title: "GovKB: One-Click Setup Current Project" }
      },
      {
        label: "Troubleshooting",
        description: "Open output",
        tooltip: "Show the GovKB output channel.",
        command: { command: "govkb.openOutput", title: "GovKB: Open Output" }
      }
    ];
  }
  const validationErrors = status.validation.errors.length;
  const validationDescription = validationErrors > 0 ? `${validationErrors} error(s)` : status.validation.status;
  const kbWarnings = status.kbHealth.warnings.length;
  const skillUpdates = skillUpdateDescription(status);
  const rows: TreeRow[] = [
    { label: "Project", description: status.project.id ?? "<unknown>", tooltip: status.projectRoot },
    { label: "Validation", description: validationDescription },
    { label: "Capabilities", description: String(status.capabilities.length) },
    { label: "Adapters", description: status.adapters.join(", ") || "none" },
    { label: "KB health warnings", description: String(kbWarnings) },
    { label: "Codex install state", description: status.installState.codex.status },
    {
      label: "Skill updates",
      description: skillUpdates,
      tooltip: skillUpdateTooltip(status),
      command: skillUpdateCommand(status)
    }
  ];
  if (validationErrors > 0) {
    rows.push({
      label: "Validation details",
      description: "Open output",
      tooltip: status.validation.errors.map((message) => `${message.location}: ${message.message}`).join("\n"),
      command: { command: "govkb.openOutput", title: "GovKB: Open Output" }
    });
  }
  if (status.kbHealth.suggestedRemediation) {
    rows.push({
      label: "Suggested remediation",
      description: status.kbHealth.suggestedRemediation,
      tooltip: "Run setup to refresh governed project scaffolding and starter knowledge.",
      command: { command: "govkb.oneClickSetup", title: "GovKB: One-Click Setup Current Project" }
    });
  }
  if (status.installState.codex.status === "missing") {
    rows.push({
      label: "Codex materialization",
      description: "Run One-Click Apply",
      tooltip: status.installState.codex.statePath ?? "Apply the governed package to the configured Codex home.",
      command: { command: "govkb.oneClickApply", title: "GovKB: One-Click Apply Current Project" }
    });
  }
  return [
    ...rows
  ];
}
