export function defaultPromotionReviewReason(decision: "accepted" | "rejected"): string {
  return decision === "accepted" ? "Accepted after reviewing the generated promotion digest." : "";
}

export function normalizePromotionReviewReason(value: string | undefined): string | undefined {
  const reason = value?.trim();
  return reason ? reason : undefined;
}
