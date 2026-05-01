export interface WorkspaceFolderLike {
  name: string;
  uri: {
    fsPath: string;
  };
}

export interface ProjectSelectionResult {
  projectRoot?: string;
  blocker?: {
    title: string;
    action: string;
  };
}

export type ProjectPicker = (roots: string[]) => Promise<string | undefined>;

export async function resolveProjectRoot(
  folders: readonly WorkspaceFolderLike[] | undefined,
  picker?: ProjectPicker
): Promise<ProjectSelectionResult> {
  if (!folders || folders.length === 0) {
    return {
      blocker: {
        title: "No workspace folder is open",
        action: "Open a local workspace folder"
      }
    };
  }
  const roots = folders.map((folder) => folder.uri.fsPath);
  if (roots.length === 1) {
    return { projectRoot: roots[0] };
  }
  if (!picker) {
    return {
      blocker: {
        title: "Multiple workspace folders are open",
        action: "Select one GovKB project root"
      }
    };
  }
  const selected = await picker(roots);
  return selected
    ? { projectRoot: selected }
    : {
        blocker: {
          title: "Project selection was cancelled",
          action: "Select one GovKB project root"
        }
      };
}

