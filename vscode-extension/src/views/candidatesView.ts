import { CandidateSummary, TreeRow } from "../types";

export function candidateRows(candidates?: CandidateSummary[]): TreeRow[] {
  if (!candidates) {
    return [
      {
        label: "Candidates not loaded",
        description: "Run List Candidates",
        tooltip: "Read staged candidate summaries through govkb candidates list --json.",
        command: { command: "govkb.listCandidates", title: "GovKB: List Candidates" }
      },
      {
        label: "Discover candidates",
        description: "Run dry-run review",
        tooltip: "Dry-run review can stage candidate proposals without memory mutation.",
        command: { command: "govkb.reviewLearningDryRun", title: "GovKB: Review Learning Dry Run" }
      },
      {
        label: "Apply memory review",
        description: "Run actual review",
        tooltip: "Run memory review in apply mode, updating eligible memory and staging candidates.",
        command: { command: "govkb.reviewLearningApply", title: "GovKB: Review Learning Apply" }
      }
    ];
  }
  if (candidates.length === 0) {
    return [
      {
        label: "No new skill candidates",
        description: "existing skills learned instead",
        tooltip: "No staged governed-skill candidates were returned by the GovKB CLI."
      }
    ];
  }
  return [
    {
      label: "Candidates need triage",
      description: `${candidates.length} staged`,
      tooltip: "Open each candidate draft and decide whether it is useful enough to keep, edit, or remove before promotion."
    },
    ...candidates.map((candidate) => ({
      label: `Review candidate: ${candidate.suggestedCapabilityId ?? candidate.id}`,
      description: `${candidate.status}, ${candidate.occurrences} occurrence${candidate.occurrences === 1 ? "" : "s"}`,
      tooltip: [
        `Candidate id: ${candidate.id}`,
        candidate.suggestedCapabilityId ? `Suggested skill: ${candidate.suggestedCapabilityId}` : undefined,
        `Activation: ${candidate.activationState}`,
        candidate.path
      ]
        .filter(Boolean)
        .join("\n"),
      command: { command: "govkb.openCandidate", title: "GovKB: Open Candidate Draft", arguments: [candidate] },
      contextValue: "govkb.candidate"
    }))
  ];
}
