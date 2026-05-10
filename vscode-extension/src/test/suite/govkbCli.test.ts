import test from "node:test";
import assert from "node:assert/strict";
import {
  applyCodexCommand,
  buildGovkbCommand,
  candidatesJsonCommand,
  initKbCommand,
  installCommand,
  promoteAutoCommand,
  promotionArchiveCommand,
  promotionMarkReviewedCommand,
  promotionShowCommand,
  promotionsListJsonCommand,
  reviewMemoryApplyCommand,
  reviewMemoryCommand,
  reviewMemoryDryRunCommand,
  runCliCommand,
  statusJsonCommand,
  validateCommand
} from "../../govkbCli";
import { defaultSettings } from "../../settings";

test("buildGovkbCommand uses executable plus argument array", () => {
  const settings = { ...defaultSettings(), command: "govkb" };
  const command = buildGovkbCommand(settings, ["status", "/repo", "--json"]);
  assert.equal(command.executable, "govkb");
  assert.deepEqual(command.args, ["status", "/repo", "--json"]);
});

test("buildGovkbCommand supports python module mode", () => {
  const settings = { ...defaultSettings(), command: "python-module", pythonPath: "python3" };
  const command = buildGovkbCommand(settings, ["--help"]);
  assert.equal(command.executable, "python3");
  assert.deepEqual(command.args, ["-m", "govkb.cli", "--help"]);
});

test("command builders preserve first-slice CLI contracts", () => {
  const settings = { ...defaultSettings(), codexHome: "/tmp/codex-home" };
  assert.deepEqual(installCommand(settings, "/repo").args, ["install", "/repo", "--codex-home", "/tmp/codex-home"]);
  assert.deepEqual(initKbCommand(settings, "/repo").args, ["init-kb", "/repo", "--all", "--codex-home", "/tmp/codex-home"]);
  assert.deepEqual(validateCommand(settings, "/repo").args, ["validate", "/repo"]);
  assert.deepEqual(statusJsonCommand(settings, "/repo").args, ["status", "/repo", "--codex-home", "/tmp/codex-home", "--json"]);
  assert.deepEqual(applyCodexCommand(settings, "/repo").args, ["apply", "codex", "--project-root", "/repo", "--codex-home", "/tmp/codex-home"]);
  assert.deepEqual(candidatesJsonCommand(settings, "/repo").args, ["candidates", "list", "/repo", "--json"]);
});

test("promotion command builders preserve lifecycle CLI contracts", () => {
  const settings = { ...defaultSettings(), codexHome: "/tmp/codex-home" };
  assert.deepEqual(promoteAutoCommand(settings, "/repo").args, ["promote", "/repo", "--auto", "--codex-home", "/tmp/codex-home"]);
  assert.deepEqual(promotionsListJsonCommand(settings, "/repo").args, [
    "promotions",
    "list",
    "/repo",
    "--codex-home",
    "/tmp/codex-home",
    "--json"
  ]);
  assert.deepEqual(promotionShowCommand(settings, "/repo", "run-1").args, [
    "promotions",
    "show",
    "run-1",
    "--project-root",
    "/repo",
    "--codex-home",
    "/tmp/codex-home"
  ]);
  assert.deepEqual(promotionMarkReviewedCommand(settings, "/repo", "run-1", "accepted", "Looks good.", "reviewer").args, [
    "promotions",
    "mark-reviewed",
    "run-1",
    "--project-root",
    "/repo",
    "--decision",
    "accepted",
    "--reason",
    "Looks good.",
    "--reviewer",
    "reviewer",
    "--codex-home",
    "/tmp/codex-home",
    "--json"
  ]);
  assert.deepEqual(promotionArchiveCommand(settings, "/repo", "run-1", "Done.").args, [
    "promotions",
    "archive",
    "run-1",
    "--project-root",
    "/repo",
    "--reason",
    "Done.",
    "--codex-home",
    "/tmp/codex-home",
    "--json"
  ]);
});

test("memory review command is dry-run and passes bounded classifier defaults", () => {
  const command = reviewMemoryDryRunCommand(defaultSettings(), "/repo");
  assert.deepEqual(command.args, [
    "review-memory",
    "--assistant",
    "codex",
    "--project-root",
    "/repo",
    "--dry-run",
    "--max-sessions",
    "1",
    "--codex-timeout",
    "180"
  ]);
});

test("memory review apply command omits dry-run flag", () => {
  const command = reviewMemoryApplyCommand(defaultSettings(), "/repo");
  assert.deepEqual(command.args, [
    "review-memory",
    "--assistant",
    "codex",
    "--project-root",
    "/repo",
    "--max-sessions",
    "1",
    "--codex-timeout",
    "180"
  ]);
});

test("memory review command honors configured default mode", () => {
  const command = reviewMemoryCommand({ ...defaultSettings(), defaultDryRun: false }, "/repo");
  assert.equal(command.args.includes("--dry-run"), false);
});

test("memory review command includes configured classifier overrides", () => {
  const command = reviewMemoryDryRunCommand(
    {
      ...defaultSettings(),
      classifierModel: "gpt-5.4-mini",
      classifierReasoning: "low",
      reviewTimeoutSeconds: 180
    },
    "/repo"
  );
  assert.deepEqual(command.args, [
    "review-memory",
    "--assistant",
    "codex",
    "--project-root",
    "/repo",
    "--dry-run",
    "--max-sessions",
    "1",
    "--codex-model",
    "gpt-5.4-mini",
    "--codex-reasoning",
    "low",
    "--codex-timeout",
    "180"
  ]);
});

test("memory review command uses configured Codex home as CODEX_HOME", () => {
  const command = reviewMemoryDryRunCommand({ ...defaultSettings(), codexHome: "/tmp/codex-home" }, "/repo");
  assert.deepEqual(command.env, { CODEX_HOME: "/tmp/codex-home" });
});

test("runCliCommand streams stdout and stderr while collecting final output", async () => {
  const stdoutChunks: string[] = [];
  const stderrChunks: string[] = [];
  const result = await runCliCommand(
    {
      executable: process.execPath,
      args: ["-e", "process.stdout.write('out'); process.stderr.write('err');"]
    },
    {
      onStdout: (chunk) => stdoutChunks.push(chunk),
      onStderr: (chunk) => stderrChunks.push(chunk)
    }
  );
  assert.equal(result.exitCode, 0);
  assert.equal(result.stdout, "out");
  assert.equal(result.stderr, "err");
  assert.deepEqual(stdoutChunks, ["out"]);
  assert.deepEqual(stderrChunks, ["err"]);
});
