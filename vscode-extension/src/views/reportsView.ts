import { ReportSummary, TreeRow } from "../types";

export function reportRows(reports?: ReportSummary[], reportRoot?: string): TreeRow[] {
  if (!reports) {
    return [
      {
        label: "Report summaries not loaded",
        description: "Refresh reports",
        tooltip: "Read aggregate memory-review report summaries from the configured Codex home.",
        command: { command: "govkb.refreshReports", title: "GovKB: Refresh Reports" }
      },
      {
        label: "Create a fresh report",
        description: "Run dry-run review",
        tooltip: "Run memory review in dry-run mode and refresh summaries after it finishes.",
        command: { command: "govkb.reviewMemoryDryRun", title: "GovKB: Review Memory Dry Run" }
      },
      {
        label: "Apply memory review",
        description: "Run actual review",
        tooltip: "Run memory review in apply mode and refresh summaries after it finishes.",
        command: { command: "govkb.reviewMemoryApply", title: "GovKB: Review Memory Apply" }
      }
    ];
  }
  if (reports.length === 0) {
    return [
      {
        label: "No report summaries found",
        description: "Run dry-run review",
        tooltip: reportRoot ? `Looked in ${reportRoot}` : "No project report folder has been resolved yet.",
        command: { command: "govkb.reviewMemoryDryRun", title: "GovKB: Review Memory Dry Run" }
      },
      {
        label: "Apply memory review",
        description: "Run actual review",
        tooltip: "Run memory review in apply mode and refresh summaries after it finishes.",
        command: { command: "govkb.reviewMemoryApply", title: "GovKB: Review Memory Apply" }
      }
    ];
  }
  return reports.map((report) => ({
    label: report.createdAt ?? report.path.split("/").pop() ?? report.path,
    description: [
      `failed ${report.sessions.failed}`,
      `deferred ${report.sessions.deferred}`,
      `learned ${report.sessions.learned}`,
      `candidates ${report.sessions.stagedCandidates}`
    ].join(", "),
    tooltip: [
      report.path,
      report.classifier.model ? `model: ${report.classifier.model}` : undefined,
      report.classifier.reasoning ? `reasoning: ${report.classifier.reasoning}` : undefined
    ]
      .filter(Boolean)
      .join("\n"),
    command: { command: "govkb.openReport", title: "GovKB: Open Report", arguments: [report.path] },
    contextValue: "govkb.report"
  }));
}
