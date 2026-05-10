import { WorkspaceFolderLike } from "./projectSelection";

export const LAST_PROJECT_ROOT_KEY = "govkb.lastProjectRoot";

export function workspaceRoots(folders: readonly WorkspaceFolderLike[] | undefined): string[] {
  return folders?.map((folder) => folder.uri.fsPath) ?? [];
}

export function storedProjectRootForWorkspace(
  folders: readonly WorkspaceFolderLike[] | undefined,
  storedRoot: string | undefined
): string | undefined {
  const roots = workspaceRoots(folders);
  if (storedRoot && roots.includes(storedRoot)) {
    return storedRoot;
  }
  return roots.length === 1 ? roots[0] : undefined;
}
