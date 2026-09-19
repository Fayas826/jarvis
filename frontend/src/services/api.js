import axios from "axios";
import { runtimeConfig } from "@/config/runtime";

const NEXUS_CONFIG = { headers: { "X-Nexus-Priority": runtimeConfig.nexusPriority } };

const apiClient = axios.create({
  baseURL: runtimeConfig.coreApiBaseUrl,
});

const enterpriseClient = axios.create({
  baseURL: runtimeConfig.enterpriseApiBaseUrl,
  headers: {
    "x-api-key": import.meta.env.VITE_ENTERPRISE_API_KEY || "jarvis_secret_key_2026"
  }
});

let cachedToken = localStorage.getItem("zenith_token");

apiClient.interceptors.request.use(async (config) => {
  if (config.url === "/auth/handshake" || config.url === "/health" || config.url === "/") {
    return config;
  }

  if (!cachedToken) {
    try {
      const res = await axios.post(`${runtimeConfig.coreApiBaseUrl}/auth/handshake`, { pin: runtimeConfig.zenithPin });
      cachedToken = res.data.access_token;
      localStorage.setItem("zenith_token", cachedToken);
    } catch (err) {
      console.error("[AUTH_FAIL] Neural handshake rejected. Invalid PIN.", err);
    }
  }

  if (cachedToken) {
    config.headers.Authorization = `Bearer ${cachedToken}`;
  }
  return config;
}, (error) => Promise.reject(error));

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem("zenith_token");
      cachedToken = null;
      return Promise.reject(error);
    }

    if (!config || !config.url || (error.response && error.response.status < 500)) {
      return Promise.reject(error);
    }

    config.__retryCount = config.__retryCount || 0;

    if (config.__retryCount >= MAX_RETRIES) {
      console.error(`[BACKEND_FAILURE] Max retries reached for ${config.url}`);
      return Promise.reject(error);
    }

    config.__retryCount += 1;
    const backoffDelay = RETRY_DELAY * Math.pow(2, config.__retryCount - 1);

    console.warn(`[SELF_HEAL] API disconnected. Retrying ${config.url} (${config.__retryCount}/${MAX_RETRIES}) in ${backoffDelay}ms...`);

    await new Promise(resolve => setTimeout(resolve, backoffDelay));
    return apiClient(config);
  }
);

export const api = {
  getVitals: () => apiClient.get("/bio/vitals"),
  getIotState: () => apiClient.get("/iot/state"),
  getForesight: () => apiClient.get("/sentience/foresight", NEXUS_CONFIG),
  getEvolution: () => apiClient.get("/sentience/evolution", NEXUS_CONFIG),
  getGhostSync: (taskId = null) => {
    const url = taskId ? `/ghost_sync?task_id=${taskId}` : "/ghost_sync";
    return apiClient.get(url, NEXUS_CONFIG);
  },
  getResonanceVitals: () => apiClient.get("/resonance/vitals", NEXUS_CONFIG),
  getSpeechQueue: () => apiClient.get("/sonic/speech_queue", NEXUS_CONFIG),
  postJarvis: (message, extra = {}) => apiClient.post("/jarvis", { message, ...extra }, NEXUS_CONFIG),
  postOsControl: (command, value) => apiClient.post("/os_control", { command, value }, NEXUS_CONFIG),
  postOptimize: () => apiClient.post("/resonance/optimize", {}, NEXUS_CONFIG),
  postPowerMode: (mode) => apiClient.post("/resonance/power_mode", { mode }, NEXUS_CONFIG),
  postDominionRoutine: (routineId) => apiClient.post("/dominion/routine", { routine_id: routineId }, NEXUS_CONFIG),
  postDominionDevice: (device, action) => apiClient.post("/dominion", { device, action }, NEXUS_CONFIG),
  getSystemDiagnostic: () => apiClient.get("/system_diagnostic", NEXUS_CONFIG),
  postForgeExecute: (files) => apiClient.post("/forge/execute", { files }, NEXUS_CONFIG),
  postVisionFocalPlane: () => apiClient.post("/vision/focal_plane", {}, NEXUS_CONFIG),
  getNexusIntel: () => apiClient.get("/nexus/intel", NEXUS_CONFIG),
  getThoughtStream: () => apiClient.get("/sentience/thought_stream", NEXUS_CONFIG),
  getMissionLogs: () => apiClient.get("/mission_logs", NEXUS_CONFIG),
  postRecoveryLog: (data) => apiClient.post("/recovery/log", data),
  getHealth: () => apiClient.get("/health"),
  getWorldState: () => apiClient.get("/world/state", NEXUS_CONFIG),
  postWorldEvent: (event) => apiClient.post("/world/event", event, NEXUS_CONFIG),
  postActionExecute: (intent, payload = {}) => apiClient.post("/action/execute", { intent, ...payload }, NEXUS_CONFIG),
  postAgentsRoute: (situation, payload = {}) => apiClient.post("/agents/route", { situation, ...payload }, NEXUS_CONFIG),
  getAgentsStatus: () => apiClient.get("/agents/status", NEXUS_CONFIG),
  getMemoryLoad: () => apiClient.get("/memory/load", NEXUS_CONFIG),
  postMemorySync: (prefs) => apiClient.post("/memory/sync", prefs, NEXUS_CONFIG),
  getMemoryIntegrity: () => apiClient.get("/memory/integrity", NEXUS_CONFIG),
  getVisionAnalysis: () => apiClient.get("/vision/analyze", NEXUS_CONFIG),
  postAgentExecute: (sequenceId) => apiClient.post("/agent/execute", { sequence_id: sequenceId }, NEXUS_CONFIG),
  postCognitiveAnticipate: () => apiClient.get("/cognitive/anticipate", NEXUS_CONFIG),
  postGovernanceArbitrate: (event, data) => apiClient.post("/governance/arbitrate", { event, data }, NEXUS_CONFIG),
  postGovernanceVerify: (intent, confidence) => apiClient.post("/governance/verify", { intent, confidence }, NEXUS_CONFIG),
  postGovernanceYield: () => apiClient.post("/governance/yield", {}, NEXUS_CONFIG),
  getGovernancePolicy: () => apiClient.get("/governance/policy", NEXUS_CONFIG),
  postEvolutionLogFailure: (event, context) => apiClient.post("/evolution/log/failure", { event, context }, NEXUS_CONFIG),
  postEvolutionLogSuccess: (event, context) => apiClient.post("/evolution/log/success", { event, context }, NEXUS_CONFIG),
  postEvolutionLogResource: (component, load) => apiClient.post("/evolution/log/resource", { component, load }, NEXUS_CONFIG),
  getEvolutionOptimizations: () => apiClient.get("/evolution/optimizations", NEXUS_CONFIG),
  postStrategyForecast: (signals) => apiClient.post("/strategy/forecast", { signals }, NEXUS_CONFIG),
  postStrategyDecompose: (goal) => apiClient.post("/strategy/decompose", { goal }, NEXUS_CONFIG),
  postStrategyAnalyze: (signals, trends) => apiClient.post("/strategy/analyze", { signals, trends }, NEXUS_CONFIG),
  postCollectiveDebate: (intent, context) => apiClient.post("/collective/debate", { intent, context }, NEXUS_CONFIG),
  getProjectDiagnostic: () => apiClient.get("/project/diagnostic", NEXUS_CONFIG),
  postOrchestratorStart: () => apiClient.post("/orchestrator/start", {}, NEXUS_CONFIG),
  getOrchestratorStatus: () => apiClient.get("/orchestrator/status", NEXUS_CONFIG),
  postSelfFix: (actionName, payload = {}) => apiClient.post("/orchestrator/self_fix", { action_name: actionName, ...payload }, NEXUS_CONFIG),
  getEnterpriseTasks: () => enterpriseClient.get("/tasks"),
  postEnterpriseTask: (data) => enterpriseClient.post("/tasks", data),
  getEnterpriseProjects: () => enterpriseClient.get("/projects"),
  postEnterpriseProject: (data) => enterpriseClient.post("/projects", data),
  postMemoryRemember: (content, source, category, importance, trust) => apiClient.post("/memory/sync", { content, source, category, importance, trust }, NEXUS_CONFIG),
  postReason: (prompt, context) => apiClient.post("/reason", { prompt, context }, NEXUS_CONFIG),
  postToolPrepare: (tool, intent, payload) => apiClient.post("/tools/prepare", { tool, intent, payload }, NEXUS_CONFIG),
  postToolExecute: (id, result) => apiClient.post("/tools/execute", { id, result }, NEXUS_CONFIG),
  postToolRollback: (id) => apiClient.post("/tools/rollback", { id }, NEXUS_CONFIG),
  getToolLedger: () => apiClient.get("/tools/ledger", NEXUS_CONFIG),
  postPerceptionSession: (action) => apiClient.post("/perception/session", { action }, NEXUS_CONFIG)
};
