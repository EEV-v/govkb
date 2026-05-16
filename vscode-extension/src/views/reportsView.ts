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
        command: { command: "govkb.reviewLearningDryRun", title: "GovKB: Review Learning Dry Run" }
      },
      {
        label: "Apply memory review",
        description: "Run actual review",
        tooltip: "Run memory review in apply mode and refresh summaries after it finishes.",
        command: { command: "govkb.reviewLearningApply", title: "GovKB: Review Learning Apply" }
      }
    ];
  }
  if (reports.length === 0) {
    return [
      {
        label: "No report summaries found",
        description: "Run dry-run review",
        tooltip: reportRoot ? `Looked in ${reportRoot}` : "No project report folder has been resolved yet.",
        command: { command: "govkb.reviewLearningDryRun", title: "GovKB: Review Learning Dry Run" }
      },
      {
        label: "Apply memory review",
        description: "Run actual review",
        tooltip: "Run memory review in apply mode and refresh summaries after it finishes.",
        command: { command: "govkb.reviewLearningApply", title: "GovKB: Review Learning Apply" }
      }
    ];
  }
  return reports.slice(0, 5).map((report) => ({
    label: report.createdAt ?? report.path.split("/").pop() ?? report.path,
    description: [
      `learned ${report.sessions.learned}`,
      `failed ${report.sessions.failed}`,
      `deferred ${report.sessions.deferred}`,
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
