import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";

test(".vscodeignore excludes local private and generated state", () => {
  const ignore = readFileSync(join(__dirname, "..", "..", "..", ".vscodeignore"), "utf8");
  assert.match(ignore, /\.governed\/\*\*/);
  assert.match(ignore, /\*\*\/memories\/govkb\/\*\*/);
  assert.match(ignore, /out\/test\/\*\*/);
  assert.match(ignore, /node_modules\/\*\*/);
});

test("package manifest contributes report and output affordances", () => {
  const manifest = JSON.parse(readFileSync(join(__dirname, "..", "..", "..", "package.json"), "utf8"));
  const commands = new Set(manifest.contributes.commands.map((command: { command: string }) => command.command));
  assert.equal(commands.has("govkb.refreshReports"), true);
  assert.equal(commands.has("govkb.openLatestReport"), true);
  assert.equal(commands.has("govkb.openOutput"), true);
  assert.equal(commands.has("govkb.reviewMemoryApply"), true);
  assert.equal(commands.has("govkb.promoteAuto"), true);
  assert.equal(commands.has("govkb.refreshPromotions"), true);
  assert.match(manifest.contributes.configuration.properties["govkb.codexHome"].description, /memory review/);
  assert.match(manifest.contributes.configuration.properties["govkb.reviewMaxSessions"].description, /keep this low/);
  assert.match(manifest.contributes.configuration.properties["govkb.autoRefreshOnStartup"].description, /workspace opens/);
  assert.match(manifest.contributes.configuration.properties["govkb.monitorIntervalSeconds"].description, /read-only refresh interval/);
});
