import test from "node:test";
import assert from "node:assert/strict";
import { resolveProjectRoot } from "../../projectSelection";

test("single workspace resolves directly", async () => {
  const result = await resolveProjectRoot([{ name: "repo", uri: { fsPath: "/repo" } }]);
  assert.equal(result.projectRoot, "/repo");
});

test("multi-root without picker returns explicit blocker", async () => {
  const result = await resolveProjectRoot([
    { name: "one", uri: { fsPath: "/one" } },
    { name: "two", uri: { fsPath: "/two" } }
  ]);
  assert.equal(result.blocker?.action, "Select one GovKB project root");
});

test("multi-root uses selected root", async () => {
  const result = await resolveProjectRoot(
    [
      { name: "one", uri: { fsPath: "/one" } },
      { name: "two", uri: { fsPath: "/two" } }
    ],
    async (roots) => roots[1]
  );
  assert.equal(result.projectRoot, "/two");
});

