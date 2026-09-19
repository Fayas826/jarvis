const trimTrailingSlash = (value) => value.replace(/\/$/, "");

export const runtimeConfig = {
  coreApiBaseUrl: trimTrailingSlash(import.meta.env.VITE_CORE_API_BASE_URL || "/api"),
  enterpriseApiBaseUrl: trimTrailingSlash(import.meta.env.VITE_ENTERPRISE_API_BASE_URL || "http://localhost:4000/api/v1"),
  zenithPin: import.meta.env.VITE_ZENITH_PIN || "4422",
  nexusPriority: import.meta.env.VITE_NEXUS_PRIORITY || "AURORA"
};
