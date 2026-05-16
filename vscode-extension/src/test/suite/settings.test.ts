import test from "node:test";
import assert from "node:assert/strict";
import { ConfigurationReader, defaultSettings, resolveSettings } from "../../settings";

class FakeConfig implements ConfigurationReader {
  constructor(private readonly values: Record<string, unknown>) {}

  get<T>(key: string, defaultValue: T): T {
    return (this.values[key] ?? defaultValue) as T;
  }
}

test("resolveSettings applies first-slice defaults", () => {
  assert.deepEqual(resolveSettings(new FakeConfig({})), defaultSettings());
});

test("resolveSettings sanitizes invalid enum and timeout values", () => {
  const settings = resolveSettings(
    new FakeConfig({
      classifierReasoning: "wild",
      setupMode: "silentDownload",
      reviewTimeoutSeconds: -10,
      reviewMaxSessions: -2,
      monitorIntervalSeconds: 10
    })
  );
  assert.equal(settings.classifierReasoning, undefined);
  assert.equal(settings.setupMode, "guidedInstall");
  assert.equal(settings.reviewTimeoutSeconds, undefined);
  assert.equal(settings.reviewLookbackDays, 90);
  assert.equal(settings.reviewMaxSessions, 5);
  assert.equal(settings.monitorIntervalSeconds, undefined);
});

test("resolveSettings keeps optional classifier overrides only when configured", () => {
  const defaults = resolveSettings(new FakeConfig({}));
  assert.equal(defaults.classifierModel, undefined);
  assert.equal(defaults.classifierReasoning, undefined);
  assert.equal(defaults.reviewTimeoutSeconds, 180);

  const settings = resolveSettings(
    new FakeConfig({
      classifierModel: "gpt-5.4-mini",
      classifierReasoning: "low",
      reviewTimeoutSeconds: 600
    })
  );
  assert.equal(settings.classifierModel, "gpt-5.4-mini");
  assert.equal(settings.classifierReasoning, "low");
  assert.equal(settings.reviewTimeoutSeconds, 600);
});

test("resolveSettings keeps configured command and Codex home", () => {
  const settings = resolveSettings(
    new FakeConfig({
      command: "python-module",
      pythonPath: "/usr/bin/python3",
      codexHome: "/tmp/codex-home"
    })
  );
  assert.equal(settings.command, "python-module");
  assert.equal(settings.pythonPath, "/usr/bin/python3");
  assert.equal(settings.codexHome, "/tmp/codex-home");
});

test("resolveSettings keeps startup and monitoring preferences", () => {
  const settings = resolveSettings(
    new FakeConfig({
      autoRefreshOnStartup: false,
      monitorIntervalSeconds: 120
    })
  );
  assert.equal(settings.autoRefreshOnStartup, false);
  assert.equal(settings.monitorIntervalSeconds, 120);
});
