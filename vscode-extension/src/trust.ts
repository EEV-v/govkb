export interface TrustResult {
  trusted: boolean;
  blocker?: {
    title: string;
    action: string;
  };
}

export async function ensureWorkspaceTrusted(isTrusted: boolean, requestTrust?: () => Promise<boolean>): Promise<TrustResult> {
  if (isTrusted) {
    return { trusted: true };
  }
  const granted = requestTrust ? await requestTrust() : false;
  if (granted) {
    return { trusted: true };
  }
  return {
    trusted: false,
    blocker: {
      title: "Workspace Trust is required",
      action: "Trust this workspace before running GovKB commands"
    }
  };
}

