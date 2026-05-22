import test from "node:test";
import assert from "node:assert/strict";
import { buildHomeModel } from "../../homeState";
import { allHomeActions, renderHomeHtml } from "../../homeWebview";
import { LearningInventoryPayload, PromotionSummary, StatusPayload } from "../../types";

const status: StatusPayload = {
  schemaVersion: 1,
  projectRoot: "/repo",
  governedRoot: "/repo/.governed",
  project: { id: "demo-project", currentRelease: "unreleased", gitRevision: "abc", governedDirty: false, governedStatus: [] },
  validation: { status: "ok", warnings: [], errors: [] },
  kbHealth: { warnings: [], suggestedRemediation: null },
  capabilities: [{ id: "project-knowledge-steward", name: "Project Knowledge Steward", governed: true }],
  adapters: ["codex"],
  releases: [],
  installState: {
    codex: {
      status: "present",
      statePath: "/tmp/state.json",
      appliedRevision: "abc",
      appliedRelease: "unreleased",
      appliedAt: null,
      materializedCapabilities: []
    }
  },
  skillUpdates: {
    state: "current",
    repoRevision: "abc",
    appliedRevision: "abc",
    governedDirty: false,
    pendingLocalMemory: {
      available: false,
      safePromotionCount: 0,
      rejectedCount: 0,
      pendingCount: 0,
      items: []
    }
  }
};

const inventory: LearningInventoryPayload = {
  schemaVersion: 1,
  projectRoot: "/repo",
  codexHome: "/tmp/codex-home",
  lookbackDays: 90,
  maxSessions: 5,
  sessions: {
    totalDiscovered: 12,
    selectedForReview: 5,
    selectedBeforeLimit: 8,
    selectedIndexed: 4,
    selectedFileOnly: 1,
    alreadyProcessed: 3,
    indexedRows: 10,
    indexedMissingFiles: 1,
    fileOnlyRecentUnprocessed: 2
  },
  selectedSessions: [],
  memoryTargets: [],
  recommendedBatch: { lookbackDays: 90, maxSessions: 5, dryRun: true, reason: "Review a bounded batch." }
};

function promotion(state: string): PromotionSummary {
  return {
    runId: `run-${state}`,
    branch: "codex/govkb-auto-promote/demo/run",
    head: "abc",
    worktreeRoot: "/tmp/worktree",
    digestPath: "/tmp/worktree/.governed/reports/promotions/latest-promotion-digest.md",
    reportPaths: [],
    status: [" M .governed/capabilities/project-knowledge-steward/references/long-term-memory.md"],
    state,
    metadataPath: "/tmp/meta.json",
    review: null,
    archive: null,
    apply: null
  };
}

test("renderHomeHtml exposes primary and section actions", () => {
  const model = buildHomeModel();
  const html = renderHomeHtml(model);
  assert.match(html, /GovKB Home/);
  assert.match(html, /Set up GovKB/);
  assert.match(html, /Why/);
  assert.match(html, /Clicking it will/);
  assert.match(html, /data-action-index="0"/);
  assert.match(html, /data-command="govkb.oneClickSetup"/);
  assert.match(html, /<svg viewBox="0 0 24 24"/);
  assert.ok(html.indexOf("primary-action") < html.indexOf("badge-grid"));
});

test("renderHomeHtml explains why stale governed skills need apply", () => {
  const model = buildHomeModel({
    status: {
      ...status,
      skillUpdates: { ...status.skillUpdates, state: "apply-available", repoRevision: "def" }
    }
  });
  const html = renderHomeHtml(model);
  assert.match(html, /Repo governed skills changed since the last Codex install/);
  assert.match(html, /The repository revision and the materialized Codex skill revision differ/);
  assert.match(html, /Updates local Codex skills from `.governed`/);
});

test("allHomeActions includes guided promotion and skill management actions", () => {
  const model = buildHomeModel({ status, inventory, promotions: [promotion("ready-for-review")] });
  const commands = allHomeActions(model).map((action) => action.command);
  assert.equal(commands.includes("govkb.openPromotion"), true);
  assert.equal(commands.includes("govkb.markPromotionAccepted"), true);
  assert.equal(commands.includes("govkb.markPromotionRejected"), true);
  assert.equal(commands.includes("govkb.reviewLearningApply"), true);
  assert.equal(commands.includes("govkb.openCapability"), true);
  assert.equal(commands.includes("govkb.convertSkillToGoverned"), true);
  assert.equal(commands.includes("govkb.renameGovernedSkill"), true);
  assert.equal(commands.includes("govkb.mergeGovernedSkills"), true);
  assert.equal(commands.includes("govkb.openLatestReport"), true);
});
