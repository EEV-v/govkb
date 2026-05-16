import {
  CandidateSummary,
  LearningInventoryPayload,
  LearningRunState,
  PromotionSummary,
  ReportSummary,
  StatusPayload,
  TreeRow
} from "../types";
import { changedSkillCount, isPromotionPendingCommit, promotionGroups } from "./promotionsView";

export interface LearningRowsInput {
  status?: StatusPayload;
  inventory?: LearningInventoryPayload;
  run?: LearningRunState;
  reports?: ReportSummary[];
  candidates?: CandidateSummary[];
  promotions?: PromotionSummary[];
}

function latestReportCommand(reports?: ReportSummary[]): TreeRow["command"] {
  const report = reports?.[0];
  return report
    ? { command: "govkb.openReport", title: "GovKB: Open Report", arguments: [report.path] }
    : { command: "govkb.openLatestReport", title: "GovKB: Open Latest Report" };
}

function learningNextStepRow(
  promotion: PromotionSummary | undefined,
  status: StatusPayload | undefined,
  pending: StatusPayload["skillUpdates"]["pendingLocalMemory"] | undefined,
  inventory: LearningInventoryPayload | undefined
): TreeRow {
  if (promotion?.state === "ready-for-review") {
    const changed = changedSkillCount(promotion);
    return {
      label: "Next: review learning update digest",
      description: `${changed} skill file${changed === 1 ? "" : "s"} ready`,
      tooltip: [
        "Click to open the digest.",
        "After reading it, accept or reject the review in Promotions.",
        "Accepted reviews can then be finalized in the active project without committing."
      ].join("\n"),
      command: { command: "govkb.openPromotion", title: "GovKB: Open Promotion Digest", arguments: [promotion] },
      icon: "eye"
    };
  }
  if (promotion?.state === "accepted") {
    const changed = changedSkillCount(promotion);
    return {
      label: "Next: finalize accepted learning updates",
      description: `${changed} skill file${changed === 1 ? "" : "s"}, no commit`,
      tooltip:
        "Finalize copies reviewed .governed updates into the active project and marks the promotion applied. Commit later through the normal project flow.",
      command: {
        command: "govkb.finalizeAcceptedPromotion",
        title: "GovKB: Finalize Accepted Learning Updates",
        arguments: [promotion]
      },
      icon: "git-merge"
    };
  }
  if (promotion?.state === "applied" && isPromotionPendingCommit(promotion, status)) {
    return {
      label: "Next: commit governed updates",
      description: "review git diff",
      tooltip: "The promotion was applied to the active project. Review and commit .governed changes through normal git flow.",
      icon: "repo-commit",
      command: { command: "govkb.showStatus", title: "GovKB: Show Status" }
    };
  }
  if (pending?.available) {
    return {
      label: "Next: create a review worktree",
      description: `${pending.pendingCount} learned update${pending.pendingCount === 1 ? "" : "s"}`,
      tooltip: "Create an isolated review for learned local memory updates before applying them to the governed package.",
      icon: "git-pull-request-create",
      command: { command: "govkb.promoteAuto", title: "GovKB: Auto Promote Learned Updates" }
    };
  }
  return {
    label: "Next: review another session batch",
    description: inventory ? `${inventory.sessions.selectedBeforeLimit} available` : "discover sessions first",
    tooltip: "Run a bounded dry run or apply run to classify more sessions.",
    icon: inventory ? "debug-alt" : "search",
    command: inventory
      ? { command: "govkb.reviewLearningDryRun", title: "GovKB: Review Learning Dry Run" }
      : { command: "govkb.discoverLearning", title: "GovKB: Discover Learning Opportunities" }
  };
}

export function learningRows(input: LearningRowsInput = {}): TreeRow[] {
  const { status, inventory, run, reports, candidates, promotions } = input;
  const rows: TreeRow[] = [];
  const latestPromotionGroup = promotions && promotions.length > 0 ? promotionGroups(promotions)[0] : undefined;
  const latestPromotion = latestPromotionGroup?.promotion;
  const hiddenPromotionDuplicates = latestPromotionGroup?.hidden ?? 0;
  const pending = status?.skillUpdates.pendingLocalMemory;
  const latestReport = reports?.[0];
  rows.push({
    label: "Learning",
    description: status ? `${status.capabilities.length} target(s)` : "status not loaded",
    tooltip: status?.projectRoot ?? "Run status or discover learning for the selected project.",
    icon: "lightbulb",
    command: { command: "govkb.discoverLearning", title: "GovKB: Discover Learning Opportunities" }
  });
  rows.push(learningNextStepRow(latestPromotion, status, pending, inventory));

  if (!inventory) {
    rows.push({
      label: "Session inventory not loaded",
      description: "Discover learning",
      tooltip: "Run read-only inventory before AI classification.",
      icon: "search",
      command: { command: "govkb.discoverLearning", title: "GovKB: Discover Learning Opportunities" }
    });
  } else {
    rows.push({
      label: "Sessions",
      description: `${inventory.sessions.selectedForReview} selected, ${inventory.sessions.selectedBeforeLimit} available`,
      icon: "list-tree",
      tooltip: [
        `Total discovered: ${inventory.sessions.totalDiscovered}`,
        `Lookback days: ${inventory.lookbackDays ?? "default"}`,
        `Max sessions: ${inventory.maxSessions ?? "default"}`,
        `Already processed: ${inventory.sessions.alreadyProcessed}`,
        `Missing indexed files: ${inventory.sessions.indexedMissingFiles}`,
        inventory.recommendedBatch.reason
      ].join("\n")
    });
  }

  if (run?.active) {
    const current = run.sessions[run.sessions.length - 1];
    rows.push({
      label: "Active review",
      description: current ? `${current.sessionId}: ${current.status}` : "starting",
      tooltip: current?.reason ?? current?.threadName ?? "Review is running.",
      icon: "sync"
    });
  } else if (run?.summary) {
    rows.push({
      label: "Last review",
      description: `${run.summary.reviewed} reviewed, ${run.summary.existingSkillUpdates} learned, ${run.summary.failed} failed`,
      tooltip: `deferred ${run.summary.deferred}, staged ${run.summary.staged}, candidates ${run.summary.stagedCandidates}`,
      icon: run.summary.failed > 0 ? "warning" : "checklist"
    });
  }

  if (latestPromotion?.state === "accepted") {
    rows.push({
      label: "Learning review",
      description:
        hiddenPromotionDuplicates > 0
          ? `accepted, ${hiddenPromotionDuplicates} duplicate worktree(s) hidden`
          : "accepted",
      tooltip: [
        `Run: ${latestPromotion.runId}`,
        "The accepted promotion is ready to finalize from the Next row. Finalizing copies reviewed .governed changes into the active project without committing.",
        latestPromotion.review?.reason
      ]
        .filter(Boolean)
        .join("\n"),
      command: {
        command: "govkb.openPromotion",
        title: "GovKB: Open Promotion Digest",
        arguments: [latestPromotion]
      },
      icon: "git-merge"
    });
  } else if (latestPromotion) {
    const finalizedDescription =
      latestPromotion.state === "applied" && !isPromotionPendingCommit(latestPromotion, status)
        ? "finalized"
        : latestPromotion.state;
    rows.push({
      label: "Learning review",
      description:
        hiddenPromotionDuplicates > 0
          ? `${finalizedDescription}, ${hiddenPromotionDuplicates} duplicate worktree(s) hidden`
          : finalizedDescription,
      tooltip: `Open ${latestPromotion.runId}, then accept or reject the reviewed governed changes in Promotions.`,
      icon: latestPromotion.state === "applied" && !isPromotionPendingCommit(latestPromotion, status) ? "pass" : "eye",
      command: { command: "govkb.openPromotion", title: "GovKB: Open Promotion Digest", arguments: [latestPromotion] }
    });
  } else if (pending?.available) {
    rows.push({
      label: "Promote learned updates",
      description: `${pending.pendingCount} pending`,
      tooltip: pending.items.map((item) => `${item.capabilityId}: ${item.additions} addition(s)`).join("\n"),
      icon: "git-pull-request-create",
      command: { command: "govkb.promoteAuto", title: "GovKB: Auto Promote Learned Updates" }
    });
  } else {
    rows.push({
      label: "Learned updates",
      description: "none pending",
      tooltip: "No local memory updates are waiting for governed promotion.",
      icon: "pass"
    });
  }

  rows.push({
    label: candidates && candidates.length > 0 ? "New skill candidates need triage" : "New skill candidates",
    description: candidates && candidates.length > 0 ? `${candidates.length} staged` : "none",
    icon: candidates && candidates.length > 0 ? "warning" : "pass",
    tooltip:
      candidates && candidates.length === 0
        ? "No new governed skill candidates. This run learned into existing capabilities."
        : "Candidates are staged governed capability proposals.",
    command: candidates && candidates.length > 0 ? { command: "govkb.listCandidates", title: "GovKB: List Candidates" } : undefined
  });

  rows.push({
    label: "Latest report",
    description: latestReport
      ? `${latestReport.sessions.learned} learned, ${latestReport.sessions.failed} failed`
      : reports
        ? "none"
        : "not loaded",
    tooltip: latestReport?.path ?? "Refresh reports after a dry-run or apply run.",
    icon: latestReport ? "file-text" : "refresh",
    command: latestReportCommand(reports)
  });

  if (!pending?.available) {
    rows.push({
      label: "Review next batch",
      description: inventory ? `${inventory.recommendedBatch.maxSessions} session(s)` : "use settings",
      tooltip: "Dry-run writes report and patch previews without applying memory.",
      icon: "debug-alt",
      command: { command: "govkb.reviewLearningDryRun", title: "GovKB: Review Learning Dry Run" }
    });
    rows.push({
      label: "Apply learning",
      description: "updates local memory",
      tooltip: "Apply mode can update local memory and stage governed candidates through the CLI.",
      icon: "play",
      command: { command: "govkb.reviewLearningApply", title: "GovKB: Review Learning Apply" }
    });
  }
  return rows;
}
