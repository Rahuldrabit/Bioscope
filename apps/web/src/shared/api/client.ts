import createClient from "openapi-fetch";

import type { paths } from "./generated/schema";

const defaultBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function createApiClient(baseUrl: string = defaultBaseUrl) {
  return createClient<paths>({ baseUrl });
}

export const apiClient = createApiClient();
