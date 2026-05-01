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
        command: { command: "govkb.reviewMemoryDryRun", title: "GovKB: Review Memory Dry Run" }
      },
      {
        label: "Apply memory review",
        description: "Run actual review",
        tooltip: "Run memory review in apply mode, updating eligible memory and staging candidates.",
        command: { command: "govkb.reviewMemoryApply", title: "GovKB: Review Memory Apply" }
      }
    ];
  }
  if (candidates.length === 0) {
    return [
      {
        label: "No candidates found",
        description: "Run dry-run review",
        tooltip: "No staged candidates were returned by the GovKB CLI.",
        command: { command: "govkb.reviewMemoryDryRun", title: "GovKB: Review Memory Dry Run" }
      },
      {
        label: "Apply memory review",
        description: "Run actual review",
        tooltip: "Run memory review in apply mode to update eligible memory and stage candidates.",
        command: { command: "govkb.reviewMemoryApply", title: "GovKB: Review Memory Apply" }
      }
    ];
  }
  return candidates.map((candidate) => ({
    label: candidate.id,
    description: `${candidate.status}, ${candidate.occurrences} occurrence(s), ${candidate.activationState}`,
    tooltip: candidate.suggestedCapabilityId ? `Suggested: ${candidate.suggestedCapabilityId}` : candidate.path
  }));
}
