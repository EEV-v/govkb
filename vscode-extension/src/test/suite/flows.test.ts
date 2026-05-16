import test from "node:test";
import assert from "node:assert/strict";
import {
  applyPromotionToProject,
  archivePromotion,
  convertSkillToGoverned,
  discoverLearning,
  listPromotions,
  markPromotionReviewed,
  mergeGovernedSkills,
  renameGovernedSkill,
  runAutoPromote,
  runLearningReviewBatch,
  runMemoryReviewApply,
  runMemoryReviewDryRun,
  runOneClickApply,
  runOneClickSetup
} from "../../flows";
import { defaultSettings } from "../../settings";
import { CliCommand, CliResult, CliRunOptions, CliRunner, LearningRunState } from "../../types";

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

const learningInventoryJson = JSON.stringify({
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
});

const learningProgressJsonl = [
  '{"event":"run_started","runId":"run-1","dryRun":true,"lookbackDays":90,"maxSessions":5}',
  '{"event":"session_selected","runId":"run-1","sessionId":"session-1","status":"queued"}',
  '{"event":"run_finished","runId":"run-1","reviewed":1,"skipped":0,"deferred":0,"failed":0,"applied":0,"staged":0,"rejected":0,"existingSkillUpdates":0,"stagedCandidates":0}'
].join("\n") + "\n";

const conversionJson = JSON.stringify({
  sourcePath: "/tmp/codex-home/skills/release-helper",
  sourceName: "release-helper",
  capabilityId: "release-helper",
  capabilityName: "Release Helper",
  packagePath: "/repo/.governed/capabilities/release-helper",
  parityLevel: "Exact content copy",
  strictStatus: "passed",
  strictIssues: []
});

class FakeRunner implements CliRunner {
  readonly commands: CliCommand[] = [];

  async run(command: CliCommand, options?: CliRunOptions): Promise<CliResult> {
    this.commands.push(command);
    const stdout =
      command.args[0] === "promotions" && command.args[1] === "list"
        ? promotionsJson
        : command.args[0] === "convert"
          ? conversionJson
        : command.args.includes("--inventory-json")
          ? learningInventoryJson
          : command.args.includes("--progress-jsonl")
            ? learningProgressJsonl
            : command.args.includes("--json")
              ? statusJson
              : "";
    if (stdout && command.args.includes("--progress-jsonl")) {
      options?.onStdout?.(stdout);
    }
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

test("discoverLearning parses inventory payload", async () => {
  const runner = new FakeRunner();
  const result = await discoverLearning(defaultSettings(), "/repo", runner);
  assert.equal(result.ok, true);
  assert.equal(result.learningInventory?.sessions.selectedForReview, 5);
  assert.equal(result.commands[0].args.includes("--inventory-json"), true);
});

test("runLearningReviewBatch reduces progress stream", async () => {
  const runner = new FakeRunner();
  const states: LearningRunState[] = [];
  const result = await runLearningReviewBatch(defaultSettings(), "/repo", runner, true, (state) => states.push(state));
  assert.equal(result.ok, true);
  assert.equal(result.learningRun?.summary?.reviewed, 1);
  assert.equal(result.commands[0].args.includes("--progress-jsonl"), true);
  assert.equal(states.length > 0, true);
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
  const applied = await applyPromotionToProject(defaultSettings(), "/repo", "run-1", runner);
  const archived = await archivePromotion(defaultSettings(), "/repo", "run-1", "Done.", runner);
  assert.equal(reviewed.promotions[0].runId, "run-1");
  assert.equal(applied.promotions[0].runId, "run-1");
  assert.equal(archived.promotions[0].runId, "run-1");
  assert.deepEqual(
    runner.commands.map((command) => command.args.slice(0, 2).join(" ")),
    ["promotions mark-reviewed", "promotions list", "promotions apply", "promotions list", "promotions archive", "promotions list"]
  );
});

test("governed skill management flows run expected CLI commands", async () => {
  const runner = new FakeRunner();
  const converted = await convertSkillToGoverned(defaultSettings(), "/repo", "release-helper", "release-helper", runner, true);
  const renamed = await renameGovernedSkill(defaultSettings(), "/repo", "release-helper", "release-review", runner);
  const merged = await mergeGovernedSkills(defaultSettings(), "/repo", "release-review", "project-knowledge-steward", runner);
  assert.equal(converted.ok, true);
  assert.equal(renamed.ok, true);
  assert.equal(merged.ok, true);
  assert.deepEqual(
    runner.commands.map((command) => command.args.slice(0, 3).join(" ")),
    ["convert skill release-helper", "capabilities rename release-helper", "capabilities merge release-review"]
  );
});

test("convertSkillToGoverned blocks strict-failed preview before write", async () => {
  const runner = new (class extends FakeRunner {
    override async run(command: CliCommand): Promise<CliResult> {
      this.commands.push(command);
      return {
        command,
        exitCode: 0,
        stdout: JSON.stringify({
          sourcePath: "/tmp/codex-home/skills/grading",
          sourceName: "grading",
          capabilityId: "grading",
          capabilityName: "Grading",
          packagePath: "/repo/.governed/capabilities/grading",
          parityLevel: "Exact content copy",
          strictStatus: "failed",
          strictIssues: [
            {
              location: "/repo/.governed/capabilities/grading/instructions.md:10",
              message: "repo-relative or package-relative path does not exist: missing.md",
              ruleId: "GSK-PATH-001",
              severity: "error"
            }
          ]
        }),
        stderr: ""
      };
    }
  })();

  const result = await convertSkillToGoverned(defaultSettings(), "/repo", "grading", "grading", runner, false);

  assert.equal(result.ok, false);
  assert.equal(result.blocker?.title, "GovKB skill conversion is not strict-ready");
  assert.match(result.blocker?.detail ?? "", /missing\.md/);
});

test("convertSkillToGoverned reports removed package after failed write", async () => {
  const runner = new (class extends FakeRunner {
    override async run(command: CliCommand): Promise<CliResult> {
      this.commands.push(command);
      return {
        command,
        exitCode: 1,
        stdout: JSON.stringify({
          sourcePath: "/tmp/codex-home/skills/grading",
          sourceName: "grading",
          capabilityId: "grading",
          capabilityName: "Grading",
          packagePath: "/repo/.governed/capabilities/grading",
          parityLevel: "Exact content copy",
          strictStatus: "failed",
          strictIssues: [
            {
              location: "/repo/.governed/capabilities/grading/instructions.md:10",
              message: "repo-relative or package-relative path does not exist: missing.md",
              ruleId: "GSK-PATH-001",
              severity: "error"
            }
          ],
          createdPackage: "/repo/.governed/capabilities/grading",
          packageRemoved: true
        }),
        stderr: ""
      };
    }
  })();

  const result = await convertSkillToGoverned(defaultSettings(), "/repo", "grading", "grading", runner, true);

  assert.equal(result.ok, false);
  assert.match(result.blocker?.detail ?? "", /package was removed/);
});
