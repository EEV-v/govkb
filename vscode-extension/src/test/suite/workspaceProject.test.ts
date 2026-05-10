import test from "node:test";
import assert from "node:assert/strict";
import { storedProjectRootForWorkspace, workspaceRoots } from "../../workspaceProject";

test("workspaceRoots extracts folder paths", () => {
  assert.deepEqual(workspaceRoots([{ name: "repo", uri: { fsPath: "/repo" } }]), ["/repo"]);
});

test("storedProjectRootForWorkspace reuses a remembered root in multi-root workspaces", () => {
  const folders = [
    { name: "one", uri: { fsPath: "/one" } },
    { name: "two", uri: { fsPath: "/two" } }
  ];
  assert.equal(storedProjectRootForWorkspace(folders, "/two"), "/two");
});

test("storedProjectRootForWorkspace falls back to single folder", () => {
  assert.equal(storedProjectRootForWorkspace([{ name: "repo", uri: { fsPath: "/repo" } }], undefined), "/repo");
});

test("storedProjectRootForWorkspace avoids stale remembered roots", () => {
  assert.equal(storedProjectRootForWorkspace([{ name: "repo", uri: { fsPath: "/repo" } }], "/old"), "/repo");
  assert.equal(
    storedProjectRootForWorkspace(
      [
        { name: "one", uri: { fsPath: "/one" } },
        { name: "two", uri: { fsPath: "/two" } }
      ],
      "/old"
    ),
    undefined
  );
});
