import createClient from "openapi-fetch";

import type { components, paths } from "./generated/schema";

export const defaultApiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function createApiClient(baseUrl: string = defaultApiBaseUrl, demoUserId?: string) {
  return createClient<paths>({
    baseUrl,
    headers: demoUserId ? { "X-Demo-User-ID": demoUserId } : undefined,
  });
}

export const apiClient = createApiClient();

/** Browser multipart is kept narrow because OpenAPI describes files as binary strings. */
export async function uploadAssetContent(
  endpoint: string,
  uploadToken: string,
  file: File,
): Promise<{ data?: components["schemas"]["AssetResponse"]; error?: unknown }> {
  const body = new FormData();
  body.set("upload_token", uploadToken);
  body.set("file", file);
  const response = await fetch(`${defaultApiBaseUrl}${endpoint}`, { method: "POST", body });
  if (!response.ok) return { error: await response.json() };
  return { data: (await response.json()) as components["schemas"]["AssetResponse"] };
}
