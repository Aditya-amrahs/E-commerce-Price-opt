const defaultApiBaseUrl = "https://backend.calmsea-8a56c76a.eastasia.azurecontainerapps.io";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? defaultApiBaseUrl;

export function apiUrl(path: string) {
  const normalizedBase = API_BASE_URL.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}
