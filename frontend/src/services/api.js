import axios from "axios";

const API_BASE_URL = "/api";
const ENTERPRISE_BASE_URL = "http://localhost:4000/api/v1";
const NEXUS_CONFIG = { headers: { 'X-Nexus-Priority': 'AURORA' } };

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

const enterpriseClient = axios.create({
  baseURL: ENTERPRISE_BASE_URL,
  headers: {
    'x-api-key': 'jarvis_secret_key_2026'
  }
});

let cachedToken = localStorage.getItem("zenith_token");

// 🛡️ O.M.E.G.A. TIER_10: AUTH_INTERCEPTOR
apiClient.interceptors.request.use(async (config) => {
  // Public endpoints bypass auth
  if (config.url === "/auth/handshake" || config.url === "/health" || config.url === "/") {
    return config;
  }

  if (!cachedToken) {
    try {
      const pin = import.meta.env.VITE_ZENITH_PIN || "4422"; // Non-sensitive handshake PIN
      const res = await axios.post(`${API_BASE_URL}/auth/handshake`, { pin });
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

// 🛡️ DOMAIN_1: BACKEND_RECOVERY_PROTOCOL
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // Base delay in ms

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    
    // Handle auth failures normally
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem("zenith_token");
      cachedToken = null;
      return Promise.reject(error);
    }

    // If it's a network error or 5xx, and we haven't exceeded retries
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
    
    console.warn(`[SELF_HEAL] API Disconnected. Retrying ${config.url} (${config.__retryCount}/${MAX_RETRIES}) in ${backoffDelay}ms...`);
    
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
  
  // New endpoints for modular components
  postVisionFocalPlane: () => apiClient.post("/vision/focal_plane", {}, NEXUS_CONFIG),
  getNexusIntel: () => apiClient.get("/nexus/intel", NEXUS_CONFIG),
  getThoughtStream: () => apiClient.get("/sentience/thought_stream", NEXUS_CONFIG),
  getMissionLogs: () => apiClient.get("/mission_logs", NEXUS_CONFIG),
  postRecoveryLog: (data) => apiClient.post("/recovery/log", data),
  getHealth: () => apiClient.get("/health"),
  
  // 🧠 DOMAIN_10: NEURAL_MEMORY_SYNC
  getMemoryLoad: () => apiClient.get("/memory/load", NEXUS_CONFIG),
  postMemorySync: (prefs) => apiClient.post("/memory/sync", prefs, NEXUS_CONFIG),
  getMemoryIntegrity: () => apiClient.get("/memory/integrity", NEXUS_CONFIG),
  
  // 👁️ DOMAIN_3: VISION_INTELLIGENCE
  getVisionAnalysis: () => apiClient.get("/vision/analyze", NEXUS_CONFIG),
  
  // 🤖 DOMAIN_2: AGENTIC_EXECUTION
  postAgentExecute: (sequenceId) => apiClient.post("/agent/execute", { sequence_id: sequenceId }, NEXUS_CONFIG),
  postCognitiveAnticipate: () => apiClient.get("/cognitive/anticipate", NEXUS_CONFIG),

  // ⚖️ DOMAIN_6: SOVEREIGN_GOVERNANCE
  postGovernanceArbitrate: (event, data) => apiClient.post("/governance/arbitrate", { event, data }, NEXUS_CONFIG),
  postGovernanceVerify: (intent, confidence) => apiClient.post("/governance/verify", { intent, confidence }, NEXUS_CONFIG),
  postGovernanceYield: () => apiClient.post("/governance/yield", {}, NEXUS_CONFIG),
  getGovernancePolicy: () => apiClient.get("/governance/policy", NEXUS_CONFIG),

  // 📈 DOMAIN_7: EVOLUTION_ENGINE
  postEvolutionLogFailure: (event, context) => apiClient.post("/evolution/log/failure", { event, context }, NEXUS_CONFIG),
  postEvolutionLogSuccess: (event, context) => apiClient.post("/evolution/log/success", { event, context }, NEXUS_CONFIG),
  postEvolutionLogResource: (component, load) => apiClient.post("/evolution/log/resource", { component, load }, NEXUS_CONFIG),
  getEvolutionOptimizations: () => apiClient.get("/evolution/optimizations", NEXUS_CONFIG),

  // 🧠 DOMAIN_8: STRATEGIC_REASONING
  postStrategyForecast: (signals) => apiClient.post("/strategy/forecast", { signals }, NEXUS_CONFIG),
  postStrategyDecompose: (goal) => apiClient.post("/strategy/decompose", { goal }, NEXUS_CONFIG),
  postStrategyAnalyze: (signals, trends) => apiClient.post("/strategy/analyze", { signals, trends }, NEXUS_CONFIG),

  // 🤝 DOMAIN_9: COLLECTIVE_INTELLIGENCE
  postCollectiveDebate: (intent, context) => apiClient.post("/collective/debate", { intent, context }, NEXUS_CONFIG),

  // 🔬 DOMAIN_11: PROJECT_DIAGNOSTIC
  getProjectDiagnostic: () => apiClient.get("/project/diagnostic", NEXUS_CONFIG),

  // 🤖 DOMAIN_12: AUTONOMOUS_ORCHESTRATION
  postOrchestratorStart: () => apiClient.post("/orchestrator/start", {}, NEXUS_CONFIG),
  getOrchestratorStatus: () => apiClient.get("/orchestrator/status", NEXUS_CONFIG),

  // 🏢 DOMAIN_13: ENTERPRISE_CORE
  getEnterpriseTasks: () => enterpriseClient.get("/tasks"),
  postEnterpriseTask: (data) => enterpriseClient.post("/tasks", data),
  getEnterpriseProjects: () => enterpriseClient.get("/projects"),
  postEnterpriseProject: (data) => enterpriseClient.post("/projects", data)
};
