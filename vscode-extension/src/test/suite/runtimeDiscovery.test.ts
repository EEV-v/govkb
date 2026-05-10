import test from "node:test";
import assert from "node:assert/strict";
import {
  defaultGovkbCommandCandidates,
  resolveDefaultGovkbCommand,
  withResolvedGovkbRuntime
} from "../../runtimeDiscovery";
import { defaultSettings } from "../../settings";

test("defaultGovkbCommandCandidates includes common GUI-missing PATH locations", () => {
  const candidates = defaultGovkbCommandCandidates("/Users/example");
  assert.deepEqual(candidates, [
    "/Users/example/.local/bin/govkb",
    "/opt/homebrew/bin/govkb",
    "/usr/local/bin/govkb",
    "/Users/example/code/govkb/scripts/govkb-dev",
    "/Users/example/code/govkb/.venv/bin/govkb"
  ]);
});

test("resolveDefaultGovkbCommand keeps explicit commands unchanged", () => {
  const command = resolveDefaultGovkbCommand("/custom/govkb", ["/Users/example/.local/bin/govkb"], () => true);
  assert.equal(command, "/custom/govkb");
});

test("resolveDefaultGovkbCommand uses first executable candidate for default govkb", () => {
  const command = resolveDefaultGovkbCommand(
    "govkb",
    ["/missing/govkb", "/Users/example/code/govkb/scripts/govkb-dev"],
    (path) => path.endsWith("govkb-dev")
  );
  assert.equal(command, "/Users/example/code/govkb/scripts/govkb-dev");
});

test("resolveDefaultGovkbCommand leaves default command when no candidates exist", () => {
  const command = resolveDefaultGovkbCommand("govkb", ["/missing/govkb"], () => false);
  assert.equal(command, "govkb");
});

test("withResolvedGovkbRuntime updates only the command field", () => {
  const settings = { ...defaultSettings(), codexHome: "/tmp/codex-home" };
  const resolved = withResolvedGovkbRuntime(settings);
  assert.equal(resolved.codexHome, "/tmp/codex-home");
  assert.ok(resolved.command === "govkb" || resolved.command.endsWith("govkb") || resolved.command.endsWith("govkb-dev"));
});

