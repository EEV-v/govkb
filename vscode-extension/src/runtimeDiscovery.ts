import { statSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { GovkbSettings } from "./types";

function isExecutableFile(path: string): boolean {
  try {
    const stat = statSync(path);
    return stat.isFile() && (stat.mode & 0o111) !== 0;
  } catch {
    return false;
  }
}

export function defaultGovkbCommandCandidates(home = homedir()): string[] {
  return [
    join(home, ".local", "bin", "govkb"),
    "/opt/homebrew/bin/govkb",
    "/usr/local/bin/govkb",
    join(home, "code", "govkb", "scripts", "govkb-dev"),
    join(home, "code", "govkb", ".venv", "bin", "govkb")
  ];
}

export function resolveDefaultGovkbCommand(
  command: string,
  candidates = defaultGovkbCommandCandidates(),
  executableFile: (path: string) => boolean = isExecutableFile
): string {
  if (command !== "govkb") {
    return command;
  }
  return candidates.find((candidate) => executableFile(candidate)) ?? command;
}

export function withResolvedGovkbRuntime(settings: GovkbSettings): GovkbSettings {
  return {
    ...settings,
    command: resolveDefaultGovkbCommand(settings.command)
  };
}

