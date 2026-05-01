import { StatusPayload, TreeRow } from "../types";

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
  const rows: TreeRow[] = [
    { label: "Project", description: status.project.id ?? "<unknown>", tooltip: status.projectRoot },
    { label: "Validation", description: validationDescription },
    { label: "Capabilities", description: String(status.capabilities.length) },
    { label: "Adapters", description: status.adapters.join(", ") || "none" },
    { label: "KB health warnings", description: String(kbWarnings) },
    { label: "Codex install state", description: status.installState.codex.status }
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
