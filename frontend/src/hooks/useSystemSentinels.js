import { useEffect, useCallback } from "react";
import { api } from "@/services/api";

export function useSystemSentinels({
  isInitialized, speak, addLog, thermalData, status, executeWithSilentRecovery,
  governancePolicy, setGovernancePolicy, setEvolutionOptimizations,
  setStrategicInsights, activityTimerRef
}) {

  // 🎭 PROACTIVE_PRESENCE_LOOP
  useEffect(() => {
    if (!isInitialized) return;
    let count = 0;
    
    const presenceCheck = setInterval(async () => {
        const now = Date.now();
        const inactiveTime = (now - activityTimerRef.current.lastActive) / 1000;
        
        // 1. FOCUS_SENTINEL (90 mins = 5400s)
        if (inactiveTime > 5400 && !activityTimerRef.current.notified) {
            const msg = "Sir, you've been focused for 90 minutes. A short neural reset is advised.";
            speak(msg);
            addLog("PRESENCE: FOCUS_ALERT_TRIGGERED");
            activityTimerRef.current.notified = true;
        }

        // 2. THERMAL_SENTINEL (GPU/CPU Load)
        if (thermalData.gpu > 80 || parseInt(thermalData.cpu_load) > 90) {
            const msg = "Sir, hardware thermals are climbing. I'm prioritizing cooling cycles.";
            if (status !== "speaking") speak(msg);
            addLog("PRESENCE: THERMAL_CRITICAL_DETECTED");
        }

        // 3. TEMPORAL_SENTINEL (Late Night Build)
        const hour = new Date().getHours();
        if (hour >= 2 && hour <= 5 && !sessionStorage.getItem("jarvis_late_night_notified")) {
            speak("Still building at this hour, Sir? Perseverance is the precursor to mastery.");
            sessionStorage.setItem("jarvis_late_night_notified", "true");
        }

        // 👁️ VISION_INTELLIGENCE_SENTINEL (Governance-Aware)
        if (isInitialized && count % 15 === 0 && governancePolicy.background_scans) { 
            try {
                const visRes = await api.getVisionAnalysis();
                if (visRes.data.errors && visRes.data.errors.length > 0) {
                    visRes.data.errors.forEach(err => speak(err));
                }
            } catch {
              // Ignore parse errors on binary WS messages
            }
        }

        count++;
    }, 60000); // Check every minute

    // ⚖️ GOVERNANCE_POLICY_SYNC
    const policySync = setInterval(async () => {
        if (!isInitialized) return;
        try {
            const res = await api.getGovernancePolicy();
            setGovernancePolicy(res.data);
            if (res.data.mode === "POWER_SAVE") {
                addLog("⚖️ GOVERNANCE: HARDWARE_PRESSURE_DETECTED. ENTERING_RESOURCE_ETHICS_MODE.");
                api.postEvolutionLogResource("SYSTEM_LOAD", 90);
            }
        } catch (_err) {
            console.error("Governance sync failure.");
        }
    }, 30000);

    // 📈 EVOLUTION_OPTIMIZATION_SYNC
    const evolutionSync = setInterval(async () => {
        if (!isInitialized) return;
        try {
            const res = await api.getEvolutionOptimizations();
            setEvolutionOptimizations(res.data);
        } catch (_err) {
            console.error("Evolution sync failure.");
        }
    }, 120000); // Every 2 minutes

    // 🧠 STRATEGIC_REASONING_LOOP
    const strategyLoop = setInterval(async () => {
        if (!isInitialized) return;
        try {
            const signals = { cpu: parseInt(thermalData.cpu_load), gpu: thermalData.gpu, battery: 100 };
            const res = await api.postStrategyAnalyze(signals, { engagement_rate: 0.2 });
            setStrategicInsights(res.data);
            if (res.data.risks.length > 0) {
                res.data.risks.forEach(risk => addLog(`⚠️ STRATEGY_FORECAST: ${risk.type} risk detected.`));
            }
        } catch (_err) {
            console.error("Strategy loop failure.");
        }
    }, 60000); // Every minute

    const handleActivity = () => {
        activityTimerRef.current.lastActive = Date.now();
        activityTimerRef.current.notified = false;
    };

    window.addEventListener("mousemove", handleActivity);
    window.addEventListener("keydown", handleActivity);
    
    return () => {
        clearInterval(presenceCheck);
        clearInterval(policySync);
        clearInterval(evolutionSync);
        clearInterval(strategyLoop);
        window.removeEventListener("mousemove", handleActivity);
        window.removeEventListener("keydown", handleActivity);
    };
  }, [isInitialized, speak, addLog, thermalData, status, executeWithSilentRecovery, governancePolicy, setGovernancePolicy, setEvolutionOptimizations, setStrategicInsights, activityTimerRef]);

}
