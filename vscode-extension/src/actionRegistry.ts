export type GovkbMutationScope =
  | "none"
  | "project"
  | "codexHome"
  | "projectAndCodexHome"
  | "projectAndPromotionMetadata"
  | "promotionMetadata"
  | "promotionWorktree"
  | "promotionWorktreeAndMetadata";

export type GovkbActionId =
  | "setup"
  | "apply"
  | "discoverLearning"
  | "reviewLearningDryRun"
  | "reviewLearningApply"
  | "createReviewWorktree"
  | "openPromotion"
  | "acceptPromotion"
  | "rejectPromotion"
  | "finalizePromotion"
  | "reviewWorkspaceChanges"
  | "openCapability"
  | "convertSkill"
  | "renameSkill"
  | "mergeSkills"
  | "openCandidates"
  | "openLatestReport"
  | "refreshReports"
  | "openOutput"
  | "previewPromotionCleanup"
  | "cleanupPromotions";

export interface GovkbActionDefinition {
  id: GovkbActionId;
  command: string;
  label: string;
  description: string;
  icon: string;
  mutates: GovkbMutationScope;
  cliBacked: boolean;
}

export const actionDefinitions: Record<GovkbActionId, GovkbActionDefinition> = {
  setup: {
    id: "setup",
    command: "govkb.oneClickSetup",
    label: "Set up GovKB",
    description: "Initialize or select a governed project.",
    icon: "rocket",
    mutates: "projectAndCodexHome",
    cliBacked: true
  },
  apply: {
    id: "apply",
    command: "govkb.oneClickApply",
    label: "Apply governed skills",
    description: "Materialize governed skills into the configured Codex home.",
    icon: "cloud-upload",
    mutates: "codexHome",
    cliBacked: true
  },
  discoverLearning: {
    id: "discoverLearning",
    command: "govkb.discoverLearning",
    label: "Discover",
    description: "Refresh learning inventory.",
    icon: "search",
    mutates: "none",
    cliBacked: true
  },
  reviewLearningDryRun: {
    id: "reviewLearningDryRun",
    command: "govkb.reviewLearningDryRun",
    label: "Preview review",
    description: "Review a bounded batch without changing memory.",
    icon: "debug-alt",
    mutates: "codexHome",
    cliBacked: true
  },
  reviewLearningApply: {
    id: "reviewLearningApply",
    command: "govkb.reviewLearningApply",
    label: "Apply review",
    description: "Apply a bounded learning review through the CLI.",
    icon: "play",
    mutates: "codexHome",
    cliBacked: true
  },
  createReviewWorktree: {
    id: "createReviewWorktree",
    command: "govkb.promoteAuto",
    label: "Create learning review",
    description: "Create an isolated review worktree for learned updates.",
    icon: "git-pull-request-create",
    mutates: "promotionWorktree",
    cliBacked: true
  },
  openPromotion: {
    id: "openPromotion",
    command: "govkb.openPromotion",
    label: "Open digest",
    description: "Inspect reviewed governed changes.",
    icon: "eye",
    mutates: "none",
    cliBacked: false
  },
  acceptPromotion: {
    id: "acceptPromotion",
    command: "govkb.markPromotionAccepted",
    label: "Accept",
    description: "Mark this learning review accepted after inspecting the digest.",
    icon: "pass",
    mutates: "promotionMetadata",
    cliBacked: true
  },
  rejectPromotion: {
    id: "rejectPromotion",
    command: "govkb.markPromotionRejected",
    label: "Reject",
    description: "Reject this learning review with a reason.",
    icon: "error",
    mutates: "promotionMetadata",
    cliBacked: true
  },
  finalizePromotion: {
    id: "finalizePromotion",
    command: "govkb.finalizeAcceptedPromotion",
    label: "Finalize",
    description: "Apply accepted changes into the active project.",
    icon: "git-merge",
    mutates: "projectAndPromotionMetadata",
    cliBacked: true
  },
  reviewWorkspaceChanges: {
    id: "reviewWorkspaceChanges",
    command: "govkb.showStatus",
    label: "Review governed workspace changes",
    description: "Inspect current governed workspace changes.",
    icon: "diff",
    mutates: "none",
    cliBacked: true
  },
  openCapability: {
    id: "openCapability",
    command: "govkb.openCapability",
    label: "Open skill",
    description: "Choose and inspect a governed skill package.",
    icon: "go-to-file",
    mutates: "none",
    cliBacked: false
  },
  convertSkill: {
    id: "convertSkill",
    command: "govkb.convertSkillToGoverned",
    label: "Convert skill",
    description: "Convert one selected local Codex skill into governed source.",
    icon: "new-folder",
    mutates: "project",
    cliBacked: true
  },
  renameSkill: {
    id: "renameSkill",
    command: "govkb.renameGovernedSkill",
    label: "Rename",
    description: "Rename one governed skill package.",
    icon: "edit",
    mutates: "project",
    cliBacked: true
  },
  mergeSkills: {
    id: "mergeSkills",
    command: "govkb.mergeGovernedSkills",
    label: "Merge",
    description: "Merge one governed skill into another.",
    icon: "git-merge",
    mutates: "project",
    cliBacked: true
  },
  openCandidates: {
    id: "openCandidates",
    command: "govkb.listCandidates",
    label: "Open candidates",
    description: "Review staged candidate packages.",
    icon: "list-tree",
    mutates: "none",
    cliBacked: true
  },
  openLatestReport: {
    id: "openLatestReport",
    command: "govkb.openLatestReport",
    label: "Open latest",
    description: "Inspect the newest learning review report.",
    icon: "go-to-file",
    mutates: "none",
    cliBacked: false
  },
  refreshReports: {
    id: "refreshReports",
    command: "govkb.refreshReports",
    label: "Refresh",
    description: "Reload learning review reports.",
    icon: "refresh",
    mutates: "none",
    cliBacked: true
  },
  openOutput: {
    id: "openOutput",
    command: "govkb.openOutput",
    label: "Open output",
    description: "Show full GovKB command output.",
    icon: "output",
    mutates: "none",
    cliBacked: false
  },
  previewPromotionCleanup: {
    id: "previewPromotionCleanup",
    command: "govkb.previewPromotionCleanup",
    label: "Preview cleanup",
    description: "Find finished promotion worktrees that can be cleaned up.",
    icon: "search",
    mutates: "none",
    cliBacked: true
  },
  cleanupPromotions: {
    id: "cleanupPromotions",
    command: "govkb.cleanupPromotions",
    label: "Clean up worktrees",
    description: "Remove cleanup-eligible promotion worktrees while preserving lifecycle metadata.",
    icon: "trash",
    mutates: "promotionWorktreeAndMetadata",
    cliBacked: true
  }
};

export function actionDefinition(id: GovkbActionId): GovkbActionDefinition {
  return actionDefinitions[id];
}

export function allActionDefinitions(): GovkbActionDefinition[] {
  return Object.values(actionDefinitions);
}
