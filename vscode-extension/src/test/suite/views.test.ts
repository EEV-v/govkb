import test from "node:test";
import assert from "node:assert/strict";
import { candidateRows } from "../../views/candidatesView";
import { capabilityRows } from "../../views/capabilitiesView";
import { promotionRows } from "../../views/promotionsView";
import { reportRows } from "../../views/reportsView";
import { statusRows } from "../../views/statusView";
import { StatusPayload } from "../../types";

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

test("statusRows summarize project health", () => {
  const rows = statusRows(status);
  assert.equal(rows[0].description, "demo-project");
  assert.equal(rows[1].description, "ok");
  assert.equal(rows[6].description, "current");
});

test("statusRows provide first-open actions", () => {
  const rows = statusRows();
  assert.equal(rows[0].label, "Project status not loaded");
  assert.equal(rows[0].command?.command, "govkb.showStatus");
  assert.equal(rows[1].command?.command, "govkb.oneClickSetup");
});

test("statusRows show apply action when materialized skills are stale", () => {
  const rows = statusRows({
    ...status,
    project: { ...status.project, gitRevision: "def" },
    skillUpdates: { ...status.skillUpdates, state: "apply-available", repoRevision: "def" }
  });
  assert.equal(rows[6].description, "apply available");
  assert.equal(rows[6].command?.command, "govkb.oneClickApply");
});

test("statusRows show workspace changes when governed package is dirty", () => {
  const rows = statusRows({
    ...status,
    project: { ...status.project, governedDirty: true, governedStatus: [" M .governed/project.toml"] },
    skillUpdates: { ...status.skillUpdates, state: "workspace-changes", governedDirty: true }
  });
  assert.equal(rows[6].description, "workspace changes");
  assert.equal(rows[6].command?.command, "govkb.showStatus");
});

test("statusRows show promotion action when learned memory is pending", () => {
  const rows = statusRows({
    ...status,
    skillUpdates: {
      ...status.skillUpdates,
      state: "learned-updates",
      pendingLocalMemory: {
        available: true,
        safePromotionCount: 1,
        rejectedCount: 0,
        pendingCount: 1,
        items: [
          {
            capabilityId: "project-knowledge-steward",
            reason: "staged: auto promotion skipped active worktree mutation",
            additions: 1,
            repoPath: "/repo/.governed/capabilities/project-knowledge-steward/references/long-term-memory.md",
            localPath: "/tmp/codex-home/skills/govkb-demo-project-project-knowledge-steward/references/long-term-memory.md"
          }
        ]
      }
    }
  });
  assert.equal(rows[6].description, "learned updates");
  assert.equal(rows[6].command?.command, "govkb.promoteAuto");
});

test("capabilityRows summarize capabilities", () => {
  const rows = capabilityRows(status.capabilities);
  assert.equal(rows[0].label, "project-knowledge-steward");
});

test("capabilityRows provide refresh actions before status loads", () => {
  const rows = capabilityRows();
  assert.equal(rows[0].command?.command, "govkb.showStatus");
});

test("candidateRows summarize candidates", () => {
  const rows = candidateRows([
    {
      id: "backend-workflow",
      status: "ready-for-review",
      occurrences: 2,
      suggestedCapabilityId: "backend-local-stack-workflow",
      activationState: "not-activated",
      path: "/repo/.governed/candidates/backend-workflow"
    }
  ]);
  assert.equal(rows[0].description, "ready-for-review, 2 occurrence(s), not-activated");
});

test("candidateRows provide discovery action when empty", () => {
  const rows = candidateRows([]);
  assert.equal(rows[0].command?.command, "govkb.reviewMemoryDryRun");
});

test("reportRows summarize report counts", () => {
  const rows = reportRows([
    {
      path: "/tmp/report.md",
      classifier: { model: "gpt-5.4-mini", reasoning: "low" },
      sessions: { failed: 1, deferred: 0, learned: 0, stagedCandidates: 0 },
      containsRawTranscript: false
    }
  ]);
  assert.equal(rows[0].description, "failed 1, deferred 0, learned 0, candidates 0");
  assert.equal(rows[0].command?.command, "govkb.openReport");
  assert.equal(rows[0].contextValue, "govkb.report");
});

test("reportRows provide refresh actions before reports load", () => {
  const rows = reportRows();
  assert.equal(rows[0].command?.command, "govkb.refreshReports");
});

test("promotionRows summarize promotion lifecycle state", () => {
  const rows = promotionRows([
    {
      runId: "run-1",
      branch: "codex/govkb-auto-promote/demo-project/run-1",
      head: "abc123",
      worktreeRoot: "/tmp/worktree",
      digestPath: "/tmp/worktree/.governed/reports/promotions/latest-promotion-digest.md",
      reportPaths: [],
      status: [" M .governed/capabilities/workflow-review/references/long-term-memory.md"],
      state: "ready-for-review",
      metadataPath: "/tmp/promotions/run-1.json",
      review: null,
      archive: null
    }
  ]);
  assert.equal(rows[0].description, "ready-for-review, 1 change");
  assert.equal(rows[0].command?.command, "govkb.openPromotion");
  assert.equal(rows[0].contextValue, "govkb.promotion");
});

test("promotionRows provide refresh and auto-promote actions before load", () => {
  const rows = promotionRows();
  assert.equal(rows[0].command?.command, "govkb.refreshPromotions");
  assert.equal(rows[1].command?.command, "govkb.promoteAuto");
});
