import { useCallback, useEffect, useState } from "react";
import { api } from "@/services/api";

const INITIAL_HEALTH = {
  status: "BOOTING",
  latency_ms: null,
  memory: "UNKNOWN",
  agents: "UNKNOWN",
  voice: "UNKNOWN",
  world_engine: "UNKNOWN",
  confidence: 0,
  risk: { level: "UNKNOWN", score: 0 }
};

export function useWorldEngine({ enabled = true, addLog } = {}) {
  const [healthState, setHealthState] = useState(INITIAL_HEALTH);
  const [worldState, setWorldState] = useState(null);
  const [agentState, setAgentState] = useState(null);
  const [actionResults, setActionResults] = useState([]);

  const recordAction = useCallback((result) => {
    setActionResults((prev) => [result, ...prev].slice(0, 12));
  }, []);

  const refresh = useCallback(async () => {
    const [health, world, agents] = await Promise.allSettled([
      api.getHealth(),
      api.getWorldState(),
      api.getAgentsStatus()
    ]);

    if (health.status === "fulfilled") setHealthState(health.value.data);
    if (world.status === "fulfilled") setWorldState(world.value.data);
    if (agents.status === "fulfilled") setAgentState(agents.value.data);

    if (health.status === "rejected" || world.status === "rejected") {
      setHealthState((prev) => ({ ...prev, status: "OFFLINE", world_engine: "OFFLINE" }));
    }
  }, []);

  const executeVerifiedAction = useCallback(async (intent, payload = {}) => {
    try {
      const res = await api.postActionExecute(intent, payload);
      recordAction(res.data);
      if (res.data.status === "needs_approval") {
        addLog?.(`ACTION_GATE: ${intent} requires approval (${res.data.risk?.level})`);
      } else {
        addLog?.(`ACTION_VERIFIED: ${intent}`);
      }
      await refresh();
      return res.data;
    } catch (err) {
      const result = {
        status: "failed",
        intent,
        error: err.message || "action execution failed",
        risk: { level: "UNKNOWN", score: 0 }
      };
      recordAction(result);
      addLog?.(`ACTION_FAILED: ${intent}`);
      return result;
    }
  }, [addLog, recordAction, refresh]);

  const routeSituation = useCallback(async (situation, payload = {}) => {
    try {
      const res = await api.postAgentsRoute(situation, payload);
      setAgentState((prev) => ({ ...(prev || {}), last_route: res.data }));
      addLog?.(`AGENT_ROUTED: ${res.data.agent_name || res.data.topic || "NO_AGENT"}`);
      await refresh();
      return res.data;
    } catch (err) {
      const result = { status: "FAILED", situation, error: err.message };
      setAgentState((prev) => ({ ...(prev || {}), last_route: result }));
      addLog?.("AGENT_ROUTE_FAILED");
      return result;
    }
  }, [addLog, refresh]);

  const recordWorldEvent = useCallback(async (type, payload = {}, source = "hud") => {
    try {
      const res = await api.postWorldEvent({ type, payload, source });
      setWorldState(res.data.world);
      return res.data;
    } catch {
      return null;
    }
  }, []);

  useEffect(() => {
    if (!enabled) return undefined;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, [enabled, refresh]);

  return {
    healthState,
    worldState,
    agentState,
    actionResults,
    refreshWorldState: refresh,
    executeVerifiedAction,
    routeSituation,
    recordWorldEvent
  };
}
