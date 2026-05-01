import { buildGovkbCommand } from "./govkbCli";
import { CliCommand, GovkbSettings } from "./types";

export interface RuntimeCheckResult {
  ok: boolean;
  blocker?: {
    title: string;
    action: string;
    detail?: string;
  };
}

export type RuntimeProbe = (command: CliCommand) => Promise<boolean>;

export async function checkGovkbRuntime(settings: GovkbSettings, probe: RuntimeProbe): Promise<RuntimeCheckResult> {
  const command = buildGovkbCommand(settings, ["--help"]);
  const ok = await probe(command);
  if (ok) {
    return { ok: true };
  }
  return {
    ok: false,
    blocker: {
      title: "GovKB runtime is not available",
      action: settings.setupMode === "useExisting" ? "Configure govkb.command" : "Install GovKB or configure govkb.command",
      detail: `${command.executable} ${command.args.join(" ")}`
    }
  };
}

