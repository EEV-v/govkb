import { DoctorPayload, SkillUpdateState, StatusPayload, TreeRow } from "../types";

const skillUpdateLabels: Record<SkillUpdateState, string> = {
  current: "current",
  "not-applied": "not applied",
  "apply-available": "apply available",
  "workspace-changes": "workspace changes",
  "learned-updates": "learned updates",
  unknown: "unknown"
};

function skillUpdateDescription(status: StatusPayload): string {
  const pending = status.skillUpdates.pendingLocalMemory;
  if (status.skillUpdates.state === "learned-updates" && pending.available) {
    return `${pending.pendingCount} learned update(s)`;
  }
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

function doctorRows(doctor?: DoctorPayload): TreeRow[] {
  if (!doctor) {
    return [];
  }
  const proposals = doctor.proposalQueue.summary;
  const rows: TreeRow[] = [
    {
      label: "Doctor",
      description: doctor.state,
      tooltip: [
        `Cron: ${doctor.cron.status}`,
        `Memory review state: ${doctor.memoryReview.state.status}`,
        `Latest memory report: ${doctor.memoryReview.latestRun.status}`,
        `Processed sessions: ${doctor.memoryReview.state.processedSessionCount}`,
        doctor.memoryReview.latestRun.path ? `Latest report: ${doctor.memoryReview.latestRun.path}` : undefined
      ]
        .filter(Boolean)
        .join("\n"),
      icon: doctor.state === "ok" ? "pass" : doctor.state === "error" ? "error" : "warning",
      command: { command: "govkb.refreshHealth", title: "GovKB: Refresh Health" }
    },
    {
      label: "Proposal queue",
      description: `${proposals.proposalCount} proposal(s), ${proposals.warningCount} warning(s)`,
      tooltip: Object.entries(proposals.actionCounts)
        .map(([action, count]) => `${action}: ${count}`)
        .join("\n"),
      icon: proposals.proposalCount > 0 ? "list-tree" : "pass",
      command: { command: "govkb.reviewProposals", title: "GovKB: Review Proposals" }
    },
    {
      label: "Memory review cron",
      description: doctor.cron.status,
      tooltip: [
        doctor.cron.scriptPath,
        doctor.cron.logPath,
        doctor.cron.error,
        ...doctor.cron.matchingLines
      ]
        .filter(Boolean)
        .join("\n"),
      icon: doctor.cron.status === "installed" ? "watch" : "warning",
      command: { command: "govkb.refreshHealth", title: "GovKB: Refresh Health" }
    }
  ];
  if (doctor.recommendations.length > 0) {
    rows.push({
      label: "Doctor recommendations",
      description: `${doctor.recommendations.length}`,
      tooltip: doctor.recommendations
        .map((item) => [item.message, item.command].filter(Boolean).join("\n"))
        .join("\n\n"),
      icon: "lightbulb",
      command: { command: "govkb.refreshHealth", title: "GovKB: Refresh Health" }
    });
  }
  return rows;
}

export function statusRows(status?: StatusPayload, doctor?: DoctorPayload): TreeRow[] {
  if (!status) {
    return [
      {
        label: "Project status not loaded",
        description: "Run Show Status",
        tooltip: "Read the selected workspace through govkb status --json.",
        icon: "pulse",
        command: { command: "govkb.showStatus", title: "GovKB: Show Status" }
      },
      {
        label: "New project setup",
        description: "Run One-Click Setup",
        tooltip: "Initialize the selected workspace through the GovKB CLI.",
        icon: "rocket",
        command: { command: "govkb.oneClickSetup", title: "GovKB: One-Click Setup Current Project" }
      },
      {
        label: "Troubleshooting",
        description: "Open output",
        tooltip: "Show the GovKB output channel.",
        icon: "output",
        command: { command: "govkb.openOutput", title: "GovKB: Open Output" }
      }
    ];
  }
  const validationErrors = status.validation.errors.length;
  const validationDescription = validationErrors > 0 ? `${validationErrors} error(s)` : status.validation.status;
  const kbWarnings = status.kbHealth.warnings.length;
  const skillUpdates = skillUpdateDescription(status);
  const validationSummary = validationErrors > 0 ? "validation errors" : status.validation.status;
  const capabilitySummary = `${status.capabilities.length} governed skill(s)`;
  const rows: TreeRow[] = [
    {
      label: status.project.id ?? "Project",
      description: `${validationSummary}, ${capabilitySummary}`,
      icon: validationErrors > 0 ? "error" : "project",
      tooltip: [
        status.projectRoot,
        `Current release: ${status.project.currentRelease}`,
        status.project.gitRevision ? `Git revision: ${status.project.gitRevision}` : undefined
      ]
        .filter(Boolean)
        .join("\n")
    },
    {
      label: "Codex skills",
      description: status.installState.codex.status === "present" ? skillUpdates : status.installState.codex.status,
      tooltip: skillUpdateTooltip(status),
      icon: status.installState.codex.status === "present" ? "cloud" : "cloud-upload",
      command: skillUpdateCommand(status)
    },
    {
      label: "Learned updates",
      description: skillUpdates,
      tooltip: skillUpdateTooltip(status),
      icon: status.skillUpdates.pendingLocalMemory.available ? "lightbulb" : "pass",
      command: skillUpdateCommand(status)
    }
  ];
  if (kbWarnings > 0) {
    rows.push({
      label: "KB health warnings",
      description: String(kbWarnings),
      tooltip: status.kbHealth.warnings.map((message) => `${message.location}: ${message.message}`).join("\n"),
      icon: "warning"
    });
  }
  if (validationErrors > 0) {
    rows.push({
      label: "Validation details",
      description: "Open output",
      tooltip: status.validation.errors.map((message) => `${message.location}: ${message.message}`).join("\n"),
      icon: "error",
      command: { command: "govkb.openOutput", title: "GovKB: Open Output" }
    });
  }
  if (status.kbHealth.suggestedRemediation) {
    rows.push({
      label: "Suggested remediation",
      description: status.kbHealth.suggestedRemediation,
      tooltip: "Run setup to refresh governed project scaffolding and starter knowledge.",
      icon: "tools",
      command: { command: "govkb.oneClickSetup", title: "GovKB: One-Click Setup Current Project" }
    });
  }
  if (status.installState.codex.status === "missing") {
    rows.push({
      label: "Codex materialization",
      description: "Run One-Click Apply",
      tooltip: status.installState.codex.statePath ?? "Apply the governed package to the configured Codex home.",
      icon: "cloud-upload",
      command: { command: "govkb.oneClickApply", title: "GovKB: One-Click Apply Current Project" }
    });
  }
  return [
    ...rows,
    ...doctorRows(doctor)
  ];
}
