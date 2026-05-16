import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { allActionDefinitions } from "../../actionRegistry";

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
  assert.equal(commands.has("govkb.openHome"), true);
  assert.equal(commands.has("govkb.refreshReports"), true);
  assert.equal(commands.has("govkb.openLatestReport"), true);
  assert.equal(commands.has("govkb.openOutput"), true);
  assert.equal(commands.has("govkb.reviewMemoryApply"), true);
  assert.equal(commands.has("govkb.discoverLearning"), true);
  assert.equal(commands.has("govkb.reviewLearningDryRun"), true);
  assert.equal(commands.has("govkb.reviewLearningApply"), true);
  assert.equal(commands.has("govkb.promoteAuto"), true);
  assert.equal(commands.has("govkb.refreshPromotions"), true);
  assert.equal(commands.has("govkb.previewPromotionCleanup"), true);
  assert.equal(commands.has("govkb.cleanupPromotions"), true);
  assert.equal(commands.has("govkb.applyPromotionToProject"), true);
  assert.equal(commands.has("govkb.finalizeAcceptedPromotion"), true);
  assert.equal(commands.has("govkb.openCandidate"), true);
  for (const definition of allActionDefinitions()) {
    assert.equal(commands.has(definition.command), true, `${definition.command} must be contributed in package.json`);
  }
  const homeView = manifest.contributes.views.govkb.find((view: { id: string }) => view.id === "govkb.home");
  assert.equal(homeView?.type, "webview");
  assert.equal(manifest.contributes.views.govkb.some((view: { id: string }) => view.id === "govkb.learning"), true);
  assert.equal(manifest.contributes.views.govkb.some((view: { id: string }) => view.id === "govkb.candidates"), true);
  assert.equal(manifest.contributes.views.govkb.some((view: { id: string }) => view.id === "govkb.reports"), true);
  assert.match(manifest.contributes.configuration.properties["govkb.codexHome"].description, /memory review/);
  assert.match(manifest.contributes.configuration.properties["govkb.reviewLookbackDays"].description, /Lookback window/);
  assert.match(manifest.contributes.configuration.properties["govkb.reviewMaxSessions"].description, /one batch/);
  assert.match(manifest.contributes.configuration.properties["govkb.autoRefreshOnStartup"].description, /workspace opens/);
  assert.match(manifest.contributes.configuration.properties["govkb.monitorIntervalSeconds"].description, /read-only refresh interval/);
});
