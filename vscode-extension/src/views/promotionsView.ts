import { PromotionSummary, StatusPayload, TreeRow } from "../types";

export interface PromotionGroup {
  promotion: PromotionSummary;
  hidden: number;
}

export function changedSkillCount(promotion: PromotionSummary): number {
  return promotion.status.filter((line) => line.includes(".governed/capabilities/")).length || promotion.status.length;
}

function statusPath(line: string): string {
  return line
    .trim()
    .replace(/^[!? MADRCU]{1,2}\s+/, "")
    .replace(/^\.\/+/, "");
}

function pathsOverlap(left: string, right: string): boolean {
  const a = left.replace(/\/+$/, "");
  const b = right.replace(/\/+$/, "");
  return a === b || a.startsWith(`${b}/`) || b.startsWith(`${a}/`);
}

function activeGovernedPaths(status?: StatusPayload): string[] {
  return (status?.project.governedStatus ?? []).map(statusPath).filter(Boolean);
}

function promotionPaths(promotion: PromotionSummary): string[] {
  const applied = promotion.apply?.files ?? [];
  if (applied.length > 0) {
    return applied.map((item) => item.replace(/^\.\/+/, ""));
  }
  return promotion.status.map(statusPath).filter(Boolean);
}

export function isPromotionPendingCommit(promotion: PromotionSummary, status?: StatusPayload): boolean {
  if (promotion.state !== "applied") {
    return false;
  }
  if (!status) {
    return true;
  }
  const active = activeGovernedPaths(status);
  if (active.length === 0) {
    return false;
  }
  const promoted = promotionPaths(promotion);
  return active.some((activePath) => promoted.some((promotedPath) => pathsOverlap(activePath, promotedPath)));
}

function changeDescription(promotion: PromotionSummary, hidden = 0, status?: StatusPayload): string {
  const changed = changedSkillCount(promotion);
  const duplicateSuffix = hidden > 0 ? `, ${hidden} duplicate${hidden === 1 ? "" : "s"} hidden` : "";
  const suffix = changed === 1 ? "skill file" : "skill files";
  if (promotion.state === "accepted") {
    return `${changed} ${suffix}, applies without commit${duplicateSuffix}`;
  }
  if (promotion.state === "applied") {
    return isPromotionPendingCommit(promotion, status)
      ? `${changed} ${suffix}, pending commit${duplicateSuffix}`
      : `${changed} ${suffix}, finalized${duplicateSuffix}`;
  }
  if (promotion.state === "ready-for-review") {
    return `${changed} ${suffix} ready${duplicateSuffix}`;
  }
  return `${changed} ${suffix}, ${promotion.state}${duplicateSuffix}`;
}

function promotionTooltip(promotion: PromotionSummary): string {
  return [
    `run: ${promotion.runId}`,
    promotion.branch ? `branch: ${promotion.branch}` : undefined,
    promotion.head ? `head: ${promotion.head}` : undefined,
    `worktree: ${promotion.worktreeRoot}`,
    promotion.digestPath ? `digest: ${promotion.digestPath}` : undefined,
    promotion.review?.reason ? `review: ${promotion.review.decision ?? promotion.state} - ${promotion.review.reason}` : undefined,
    promotion.apply?.appliedAt ? `applied: ${promotion.apply.appliedAt}` : undefined,
    promotion.archive?.reason ? `archive: ${promotion.archive.reason}` : undefined
  ]
    .filter(Boolean)
    .join("\n");
}

function promotionContextValue(promotion: PromotionSummary): string {
  if (promotion.state === "ready-for-review") {
    return "govkb.promotion.ready";
  }
  if (promotion.state === "accepted") {
    return "govkb.promotion.accepted";
  }
  if (promotion.state === "applied") {
    return "govkb.promotion.applied";
  }
  return "govkb.promotion";
}

function promotionIcon(promotion: PromotionSummary, status?: StatusPayload): string {
  if (promotion.state === "ready-for-review") {
    return "eye";
  }
  if (promotion.state === "accepted") {
    return "git-merge";
  }
  if (promotion.state === "applied") {
    return isPromotionPendingCommit(promotion, status) ? "repo-commit" : "pass";
  }
  return "git-pull-request";
}

function promotionLabel(promotion: PromotionSummary, status?: StatusPayload): string {
  if (promotion.state === "accepted") {
    return "Next: finalize accepted learning updates";
  }
  if (promotion.state === "applied") {
    return isPromotionPendingCommit(promotion, status) ? "Next: commit governed changes" : "Learning updates finalized";
  }
  if (promotion.state === "ready-for-review") {
    return "1. Open learning review";
  }
  return promotion.runId;
}

function promotionPriority(promotion: PromotionSummary): number {
  if (promotion.state === "applied") {
    return 3;
  }
  if (promotion.state === "accepted") {
    return 2;
  }
  if (promotion.state === "ready-for-review") {
    return 1;
  }
  return 0;
}

function promotionFingerprint(promotion: PromotionSummary): string {
  if (!["ready-for-review", "accepted", "applied"].includes(promotion.state)) {
    return promotion.runId;
  }
  const changed = promotion.status
    .filter((line) => !line.includes(".governed/reports/promotions/"))
    .map((line) => line.trim())
    .sort();
  return [promotion.head ?? "", ...changed].join("\n") || promotion.runId;
}

export function promotionGroups(promotions: PromotionSummary[]): PromotionGroup[] {
  const byFingerprint = new Map<string, { promotion: PromotionSummary; index: number; hidden: number }>();
  promotions.forEach((promotion, index) => {
    const key = promotionFingerprint(promotion);
    const existing = byFingerprint.get(key);
    if (!existing) {
      byFingerprint.set(key, { promotion, index, hidden: 0 });
      return;
    }
    existing.hidden += 1;
    if (promotionPriority(promotion) > promotionPriority(existing.promotion)) {
      existing.promotion = promotion;
    }
  });
  const compacted = [...byFingerprint.values()].sort((a, b) => a.index - b.index);
  return compacted.map((item) => ({ promotion: item.promotion, hidden: item.hidden }));
}

function primaryCommand(promotion: PromotionSummary): TreeRow["command"] {
  if (promotion.state === "accepted") {
    return {
      command: "govkb.finalizeAcceptedPromotion",
      title: "GovKB: Finalize Accepted Learning Updates",
      arguments: [promotion]
    };
  }
  return { command: "govkb.openPromotion", title: "GovKB: Open Promotion Digest", arguments: [promotion] };
}

function reviewDecisionRows(promotion: PromotionSummary): TreeRow[] {
  if (promotion.state !== "ready-for-review") {
    return [];
  }
  return [
    {
      label: "2. Accept reviewed updates",
      description: "then finalize",
      tooltip:
        "Use this after reading the digest. Accepting records your review decision and makes finalization available.",
      icon: "pass",
      command: {
        command: "govkb.markPromotionAccepted",
        title: "GovKB: Mark Promotion Accepted",
        arguments: [promotion]
      },
      contextValue: "govkb.promotion.ready.accept"
    },
    {
      label: "Reject this review",
      description: "keep project unchanged",
      tooltip: "Reject this promotion if the digest is wrong, noisy, or should not become governed knowledge.",
      icon: "error",
      command: {
        command: "govkb.markPromotionRejected",
        title: "GovKB: Mark Promotion Rejected",
        arguments: [promotion]
      },
      contextValue: "govkb.promotion.ready.reject"
    }
  ];
}

export function promotionRows(promotions?: PromotionSummary[], status?: StatusPayload): TreeRow[] {
  if (!promotions) {
    return [
      {
        label: "Promotions not loaded",
        description: "Refresh promotions",
        tooltip: "Read isolated promotion review worktrees through govkb promotions list --json.",
        icon: "refresh",
        command: { command: "govkb.refreshPromotions", title: "GovKB: Refresh Promotions" }
      },
      {
        label: "Check learned updates",
        description: "Run auto promote",
        tooltip: "Create an isolated promotion worktree for safe local memory updates.",
        icon: "git-pull-request-create",
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
        icon: "git-pull-request-create",
        command: { command: "govkb.promoteAuto", title: "GovKB: Auto Promote Learned Updates" }
      }
    ];
  }
  const groups = promotionGroups(promotions);
  const hiddenTotal = groups.reduce((total, group) => total + group.hidden, 0);
  const rows: TreeRow[] = groups.flatMap(({ promotion, hidden }) => [
    {
      label: promotionLabel(promotion, status),
      description: changeDescription(promotion, hidden, status),
      tooltip: promotionTooltip(promotion),
      command: primaryCommand(promotion),
      icon: promotionIcon(promotion, status),
      contextValue: promotionContextValue(promotion)
    },
    ...reviewDecisionRows(promotion)
  ]);
  if (hiddenTotal > 0) {
    rows.push({
      label: "Duplicate review worktrees",
      description: `${hiddenTotal} hidden`,
      tooltip: "Repeated learning apply runs created equivalent isolated review worktrees for the same governed changes. They are hidden here because one lifecycle decision covers the equivalent change set.",
      icon: "layers"
    });
  }
  return rows;
}
