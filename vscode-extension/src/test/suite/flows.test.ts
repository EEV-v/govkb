import test from "node:test";
import assert from "node:assert/strict";
import { runMemoryReviewApply, runMemoryReviewDryRun, runOneClickApply, runOneClickSetup } from "../../flows";
import { defaultSettings } from "../../settings";
import { CliCommand, CliResult, CliRunner } from "../../types";

const statusJson = JSON.stringify({
  schemaVersion: 1,
  projectRoot: "/repo",
  governedRoot: "/repo/.governed",
  project: { id: "repo", currentRelease: "unreleased" },
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
  }
});

class FakeRunner implements CliRunner {
  readonly commands: CliCommand[] = [];

  async run(command: CliCommand): Promise<CliResult> {
    this.commands.push(command);
    const stdout = command.args.includes("--json") ? statusJson : "";
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
