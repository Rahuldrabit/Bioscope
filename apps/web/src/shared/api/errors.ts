export function apiErrorMessage(error: unknown, fallback: string): string {
  if (!error || typeof error !== "object") return fallback;
  const record = error as Record<string, unknown>;
  const envelope = record.error;
  if (envelope && typeof envelope === "object") {
    const message = (envelope as Record<string, unknown>).message;
    if (typeof message === "string") return message;
  }
  const detail = record.detail;
  if (typeof detail === "string") return detail;
  return fallback;
}
