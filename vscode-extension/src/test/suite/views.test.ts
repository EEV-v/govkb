import test from "node:test";
import assert from "node:assert/strict";
import { candidateRows } from "../../views/candidatesView";
import { capabilityRows } from "../../views/capabilitiesView";
import { reportRows } from "../../views/reportsView";
import { statusRows } from "../../views/statusView";
import { StatusPayload } from "../../types";

const status: StatusPayload = {
  schemaVersion: 1,
  projectRoot: "/repo",
  governedRoot: "/repo/.governed",
  project: { id: "demo-project", currentRelease: "unreleased" },
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
  }
};

test("statusRows summarize project health", () => {
  const rows = statusRows(status);
  assert.equal(rows[0].description, "demo-project");
  assert.equal(rows[1].description, "ok");
});

test("statusRows provide first-open actions", () => {
  const rows = statusRows();
  assert.equal(rows[0].label, "Project status not loaded");
  assert.equal(rows[0].command?.command, "govkb.showStatus");
  assert.equal(rows[1].command?.command, "govkb.oneClickSetup");
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
