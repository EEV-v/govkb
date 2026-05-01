import { GovkbSettings, ReasoningEffort, SetupMode } from "./types";

export interface ConfigurationReader {
  get<T>(key: string, defaultValue: T): T;
}

const reasoningValues = new Set(["low", "medium", "high", "xhigh"]);
const setupModeValues = new Set(["auto", "useExisting", "guidedInstall"]);

function asOptionalReasoning(value: string): ReasoningEffort | undefined {
  return reasoningValues.has(value) ? (value as ReasoningEffort) : undefined;
}

function asSetupMode(value: string): SetupMode {
  return setupModeValues.has(value) ? (value as SetupMode) : "guidedInstall";
}

export function defaultSettings(): GovkbSettings {
  return {
    command: "govkb",
    pythonPath: "python3",
    setupMode: "guidedInstall",
    codexHome: undefined,
    classifierModel: undefined,
    classifierReasoning: undefined,
    reviewTimeoutSeconds: undefined,
    reviewMaxSessions: 1,
    defaultDryRun: true
  };
}

export function resolveSettings(config: ConfigurationReader): GovkbSettings {
  const defaults = defaultSettings();
  const codexHome = config.get("codexHome", "");
  const classifierModel = config.get("classifierModel", "");
  const classifierReasoning = config.get("classifierReasoning", "");
  const timeout = config.get("reviewTimeoutSeconds", 0);
  const maxSessions = config.get("reviewMaxSessions", defaults.reviewMaxSessions);
  return {
    command: config.get("command", defaults.command).trim() || defaults.command,
    pythonPath: config.get("pythonPath", defaults.pythonPath).trim() || defaults.pythonPath,
    setupMode: asSetupMode(config.get("setupMode", defaults.setupMode)),
    codexHome: codexHome.trim() || undefined,
    classifierModel: classifierModel.trim() || undefined,
    classifierReasoning: asOptionalReasoning(classifierReasoning),
    reviewTimeoutSeconds: Number.isFinite(timeout) && timeout > 0 ? Math.floor(timeout) : undefined,
    reviewMaxSessions: Number.isFinite(maxSessions) && maxSessions > 0 ? Math.floor(maxSessions) : defaults.reviewMaxSessions,
    defaultDryRun: config.get("defaultDryRun", defaults.defaultDryRun)
  };
}
