import { PromotionSummary, TreeRow } from "../types";

function changeDescription(promotion: PromotionSummary): string {
  const changed = promotion.status.length;
  const suffix = changed === 1 ? "change" : "changes";
  return `${promotion.state}, ${changed} ${suffix}`;
}

function promotionTooltip(promotion: PromotionSummary): string {
  return [
    `run: ${promotion.runId}`,
    promotion.branch ? `branch: ${promotion.branch}` : undefined,
    promotion.head ? `head: ${promotion.head}` : undefined,
    `worktree: ${promotion.worktreeRoot}`,
    promotion.digestPath ? `digest: ${promotion.digestPath}` : undefined,
    promotion.review?.reason ? `review: ${promotion.review.decision ?? promotion.state} - ${promotion.review.reason}` : undefined,
    promotion.archive?.reason ? `archive: ${promotion.archive.reason}` : undefined
  ]
    .filter(Boolean)
    .join("\n");
}

export function promotionRows(promotions?: PromotionSummary[]): TreeRow[] {
  if (!promotions) {
    return [
      {
        label: "Promotions not loaded",
        description: "Refresh promotions",
        tooltip: "Read isolated promotion review worktrees through govkb promotions list --json.",
        command: { command: "govkb.refreshPromotions", title: "GovKB: Refresh Promotions" }
      },
      {
        label: "Check learned updates",
        description: "Run auto promote",
        tooltip: "Create an isolated promotion worktree for safe local memory updates.",
        command: { command: "govkb.promoteAuto", title: "GovKB: Auto Promote Learned Updates" }
      }
    ];
  }
  if (promotions.length === 0) {
    return [
      {
        label: "No isolated promotions found",
        description: "Run auto promote",
        tooltip: "No isolated promotion review worktrees were found for this project.",
        command: { command: "govkb.promoteAuto", title: "GovKB: Auto Promote Learned Updates" }
      }
    ];
  }
  return promotions.map((promotion) => ({
    label: promotion.runId,
    description: changeDescription(promotion),
    tooltip: promotionTooltip(promotion),
    command: { command: "govkb.openPromotion", title: "GovKB: Open Promotion Digest", arguments: [promotion] },
    contextValue: "govkb.promotion"
  }));
}
