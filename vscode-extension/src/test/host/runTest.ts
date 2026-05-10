import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { runTests } from "@vscode/test-electron";

function vscodeExecutablePath(): string | undefined {
  if (process.env.VSCODE_EXECUTABLE_PATH?.trim()) {
    return process.env.VSCODE_EXECUTABLE_PATH;
  }
  const macPath = "/Applications/Visual Studio Code.app/Contents/MacOS/Electron";
  return existsSync(macPath) ? macPath : undefined;
}

async function main(): Promise<void> {
  const extensionDevelopmentPath = resolve(__dirname, "../../..");
  const extensionTestsPath = resolve(__dirname, "suite", "index");
  const executablePath = vscodeExecutablePath();
  await runTests({
    extensionDevelopmentPath,
    extensionTestsPath,
    vscodeExecutablePath: executablePath,
    launchArgs: [
      "--disable-extensions",
      "--disable-workspace-trust",
      "--skip-welcome",
      "--skip-release-notes"
    ]
  });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});

