import test from "node:test";
import assert from "node:assert/strict";
import {
  archivePromotion,
  listPromotions,
  markPromotionReviewed,
  runAutoPromote,
  runMemoryReviewApply,
  runMemoryReviewDryRun,
  runOneClickApply,
  runOneClickSetup
} from "../../flows";
import { defaultSettings } from "../../settings";
import { CliCommand, CliResult, CliRunner } from "../../types";

const statusJson = JSON.stringify({
  schemaVersion: 1,
  projectRoot: "/repo",
  governedRoot: "/repo/.governed",
  project: { id: "repo", currentRelease: "unreleased", gitRevision: "abc", governedDirty: false, governedStatus: [] },
  validation: { status: "ok", warnings: [], errors: [] },
  kbHealth: { warnings: [], suggestedRemediation: null },
  capabilities: [],
  adapters: ["codex"],
  releases: [],
  installState: {
    codex: {
      status: "missing",
      statePath: null,
      appliedRevision: null,
      appliedRelease: null,
      appliedAt: null,
      materializedCapabilities: []
    }
  },
  skillUpdates: {
    state: "not-applied",
    repoRevision: null,
    appliedRevision: null,
    governedDirty: false,
    pendingLocalMemory: {
      available: false,
      safePromotionCount: 0,
      rejectedCount: 0,
      pendingCount: 0,
      items: []
    }
  }
});

const promotionsJson = JSON.stringify({
  schemaVersion: 1,
  projectRoot: "/repo",
  codexHome: "/tmp/codex-home",
  projectId: "repo",
  promotionsRoot: "/tmp/codex-home/memories/govkb/worktrees/repo",
  promotions: [
    {
      runId: "run-1",
      branch: "codex/govkb-auto-promote/repo/run-1",
      head: "abc123",
      worktreeRoot: "/tmp/codex-home/memories/govkb/worktrees/repo/run-1",
      digestPath: "/tmp/codex-home/memories/govkb/worktrees/repo/run-1/.governed/reports/promotions/latest-promotion-digest.md",
      reportPaths: [],
      status: [" M .governed/capabilities/workflow/references/long-term-memory.md"],
      state: "ready-for-review",
      metadataPath: "/tmp/codex-home/memories/govkb/promotions/repo/run-1.json",
      review: null,
      archive: null
    }
  ]
});

class FakeRunner implements CliRunner {
  readonly commands: CliCommand[] = [];

  async run(command: CliCommand): Promise<CliResult> {
    this.commands.push(command);
    const stdout = command.args[0] === "promotions" && command.args[1] === "list"
      ? promotionsJson
      : command.args.includes("--json")
        ? statusJson
        : "";
    return { command, exitCode: 0, stdout, stderr: "" };
  }
}

test("one-click setup stops on one missing runtime blocker", async () => {
  const runner = new FakeRunner();
  const result = await runOneClickSetup(defaultSettings(), "/repo", runner, async () => false);
  assert.equal(result.ok, false);
  assert.equal(result.commands.length, 0);
  assert.equal(result.blocker?.action, "Install GovKB or configure govkb.command");
});

test("one-click setup runs install, init-kb, validate, status", async () => {
  const runner = new FakeRunner();
  const result = await runOneClickSetup(defaultSettings(), "/repo", runner, async () => true);
  assert.equal(result.ok, true);
  assert.deepEqual(
    result.commands.map((command) => command.args[0]),
    ["install", "init-kb", "validate", "status"]
  );
  assert.equal(result.statusJson?.project.id, "repo");
});

test("one-click apply runs apply then status only", async () => {
  const runner = new FakeRunner();
  const result = await runOneClickApply(defaultSettings(), "/repo", runner);
  assert.equal(result.ok, true);
  assert.deepEqual(
    result.commands.map((command) => command.args.slice(0, 2).join(" ")),
    ["status /repo", "apply codex", "status /repo"]
  );
});

test("one-click apply asks for setup when project is not initialized", async () => {
  const runner = new (class extends FakeRunner {
    override async run(command: CliCommand): Promise<CliResult> {
      this.commands.push(command);
      return {
        command,
        exitCode: 1,
        stdout: JSON.stringify({
          schemaVersion: 1,
          validation: { status: "error", errors: [{ message: "missing governed root" }] }
        }),
        stderr: ""
      };
    }
  })();
  const result = await runOneClickApply(defaultSettings(), "/repo", runner);
  assert.equal(result.ok, false);
  assert.equal(result.commands.length, 1);
  assert.equal(result.blocker?.action, "Run GovKB: One-Click Setup Current Project");
});

test("memory review dry-run does not run apply mode", async () => {
  const runner = new FakeRunner();
  const result = await runMemoryReviewDryRun(defaultSettings(), "/repo", runner);
  assert.equal(result.ok, true);
  assert.deepEqual(result.commands[0].args.slice(0, 6), [
    "review-memory",
    "--assistant",
    "codex",
    "--project-root",
    "/repo",
    "--dry-run"
  ]);
});

test("memory review apply runs without dry-run flag", async () => {
  const runner = new FakeRunner();
  const result = await runMemoryReviewApply(defaultSettings(), "/repo", runner);
  assert.equal(result.ok, true);
  assert.deepEqual(result.commands[0].args.slice(0, 5), [
    "review-memory",
    "--assistant",
    "codex",
    "--project-root",
    "/repo"
  ]);
  assert.equal(result.commands[0].args.includes("--dry-run"), false);
});

test("auto promote runs promote then refreshes promotions", async () => {
  const runner = new FakeRunner();
  const result = await runAutoPromote(defaultSettings(), "/repo", runner);
  assert.equal(result.ok, true);
  assert.deepEqual(
    result.commands.map((command) => command.args.slice(0, 2).join(" ")),
    ["promote /repo", "promotions list"]
  );
  assert.equal(result.promotionsJson?.promotions[0].runId, "run-1");
});

test("listPromotions parses promotion lifecycle payload", async () => {
  const runner = new FakeRunner();
  const payload = await listPromotions(defaultSettings(), "/repo", runner);
  assert.equal(payload.promotions[0].state, "ready-for-review");
});

test("promotion lifecycle updates refresh list after sidecar mutation", async () => {
  const runner = new FakeRunner();
  const reviewed = await markPromotionReviewed(defaultSettings(), "/repo", "run-1", "accepted", "Looks good.", runner);
  const archived = await archivePromotion(defaultSettings(), "/repo", "run-1", "Done.", runner);
  assert.equal(reviewed.promotions[0].runId, "run-1");
  assert.equal(archived.promotions[0].runId, "run-1");
  assert.deepEqual(
    runner.commands.map((command) => command.args.slice(0, 2).join(" ")),
    ["promotions mark-reviewed", "promotions list", "promotions archive", "promotions list"]
  );
});
