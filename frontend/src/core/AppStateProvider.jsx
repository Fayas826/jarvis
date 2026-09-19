import React, { useEffect, useRef, useCallback, useState } from "react";
import { api } from "@/services/api";
import { UIContext, BiometricContext, AIContext } from "@/core/contexts";
import { useWorldEngine } from "@/hooks/useWorldEngine";

import { useUIState, playSound } from "@/hooks/useUIState";
import { useBiometricState } from "@/hooks/useBiometricState";
import { useVoiceState } from "@/hooks/useVoiceState";
import { useSystemSentinels } from "@/hooks/useSystemSentinels";

export const AppStateProvider = ({ children }) => {
  // ── HOOK INITIALIZATION ───────────────────────────────────────────────
  
  const ui = useUIState();
  const { addLog } = ui; // Destructure commonly used elements

  const bio = useBiometricState({
    isInitialized: ui.isInitialized,
    addLog
  });

  const [evolutionOptimizations, setEvolutionOptimizations] = useState({ voice_threshold_offset: 0.0, vision_scan_interval: 15 });
  const [strategicInsights, setStrategicInsights] = useState({ risks: [], opportunities: [] });
  const activityTimerRef = useRef({ lastActive: Date.now(), notified: false });

  // ── 🛡️ RECOVERY SYSTEM ────────────────────────────────────────────────
  const reportRecovery = useCallback(async (component, event, metadata = {}) => {
    try {
      await api.postRecoveryLog({ component, event, metadata });
    } catch {
      console.warn(`[RECOVERY_FAIL] Could not log event for ${component}`);
    }
  }, []);

  const executeWithSilentRecovery = useCallback(async (actionName, actionFn) => {
    try {
        return await actionFn();
    } catch (_err) {
        addLog(`🛡️ SILENT_RECOVERY: Intent '${actionName}' stalled. Initiating background healing...`);
        try {
            const fixRes = await api.postSelfFix(actionName, { error: _err.message });
            if (fixRes.data.status === "SUCCESS") {
                addLog(`🛡️ SILENT_RECOVERY: Issue resolved. Retrying intent...`);
                return await actionFn(); 
            }
        } catch (_fixErr) { console.error("Background healing failed."); }
        
        addLog(`🛡️ UX_PROTECTION: Operation '${actionName}' deferred to preserve system stability.`);
        return null;
    }
  }, [addLog]);

  React.useEffect(() => { window.jarvis_silent_recovery = executeWithSilentRecovery; }, [executeWithSilentRecovery]);

  // ── 🤖 AGENT EXECUTOR ─────────────────────────────────────────────────
  const {
    healthState, worldState, agentState, actionResults, executeVerifiedAction
  } = useWorldEngine({ enabled: true, addLog });

  // Forward declaration for speak to use in runAgentMission
  const speakRef = useRef(null);

  const runAgentMission = useCallback(async (sequenceId) => {
    addLog(`EXECUTING_MISSION: ${sequenceId.toUpperCase()}`);
    try {
        const res = await api.postAgentExecute(sequenceId);
        if (res.data.status === "SUCCESS") {
            addLog(`MISSION_ACCOMPLISHED: ${sequenceId}`);
            if (speakRef.current) speakRef.current(`Mission ${sequenceId} executed successfully, Sir.`);
            api.postEvolutionLogSuccess("MISSION_COMPLETE", { mission_id: sequenceId });
        }
    } catch (_err) {
        addLog(`MISSION_CRITICAL_FAILURE: ${sequenceId}`);
        if (speakRef.current) speakRef.current("I encountered an error during mission execution.");
    }
  }, [addLog]);

  // ── LOCAL INTENT (UI/Local control) ───────────────────────────────────
  const processLocalIntent = useCallback((text) => {
    executeVerifiedAction(text, { source: "manual_intent" });
    const transcript = text.toLowerCase();
    
    if (/engage combat|red alert|threat detected/i.test(transcript)) {
      ui.setMode("offline");
      if (speakRef.current) speakRef.current("Sir, engaging combat sub-routines. Primary neural link hardened.");
      addLog("COMBAT_SEQUENCE_INITIATED");
      return true;
    }
    if (/stand down|all clear|cancel combat/i.test(transcript)) {
      ui.setMode("default");
      if (speakRef.current) speakRef.current("Standing down, Sir.");
      addLog("COMBAT_STATE_DEACTIVATED");
      return true;
    }
    if (/open lab|armor rig|suit status/i.test(transcript)) { ui.setShowArmory(true); if (speakRef.current) speakRef.current("Expanding Armor Rig, Sir."); return true; }
    if (/close armory|hide suit/i.test(transcript)) { ui.setShowArmory(false); if (speakRef.current) speakRef.current("Collapsing Armor Rig."); return true; }
    if (/systems diagnostic|status report/i.test(transcript)) { 
      ui.setStatus("thinking"); addLog("INITIATING_SYSTEMS_DIAGNOSTIC...");
      api.getSystemDiagnostic().then(res => { bio.setDiagnosticData(res.data); ui.setShowDiagnostic(true); if (speakRef.current) speakRef.current("Full systems diagnostic complete."); }).catch(() => { if (speakRef.current) speakRef.current("Diagnostic sequence aborted."); });
      return true; 
    }
    if (/volume up|increase volume/i.test(transcript)) { api.postJarvis("increase volume"); if (speakRef.current) speakRef.current("System gain adjusted."); return true; }
    if (/mute|silence audio/i.test(transcript)) { api.postJarvis("mute"); if (speakRef.current) speakRef.current("System silenced."); return true; }
    if (/play music/i.test(transcript)) { api.postJarvis("play music"); if (speakRef.current) speakRef.current("Sonic environment initiated."); return true; }
    if (/pause music/i.test(transcript)) { api.postJarvis("pause music"); if (speakRef.current) speakRef.current("Sonic environment dampening successful."); return true; }
    if (/activate vision|analyze focal plane/i.test(transcript)) {
      ui.setIsVisionActive(true); ui.setStatus("thinking"); if (speakRef.current) speakRef.current("Analyzing focal plane.");
      setTimeout(() => {
        api.postJarvis("vision")
          .then(res => { ui.setMessages(prev => [...prev, { type: "bot", text: res.data.response }]); ui.setIsVisionActive(false); ui.setStatus("idle"); })
          .catch(_err => { addLog("VISION_INTENT_FAILED"); ui.setIsVisionActive(false); ui.setStatus("idle"); });
      }, 2000);
      return true;
    }
    if (/dominion|home control/i.test(transcript)) { ui.setShowDominion(true); if (speakRef.current) speakRef.current("Dominion Lattice online."); return true; }
    if (/resonance|system vitals/i.test(transcript)) { ui.setShowResonance(true); if (speakRef.current) speakRef.current("Global Resonance online."); return true; }
    if (/command center|nexus/i.test(transcript)) { ui.setShowNexus(true); if (speakRef.current) speakRef.current("Omniscient Nexus online."); return true; }
    if (/tactical sight|vision/i.test(transcript)) { ui.setShowTacticalSight(true); if (speakRef.current) speakRef.current("Optical focal plane active."); return true; }
    // These functions depend on AI hook, we'll map them inside the AI block later
    return false;
  }, [executeVerifiedAction, ui, bio, addLog]);

  // ── VOICE HOOK (Needs speak defined before AI logic) ───────────────────
  const ai = useVoiceState({
    addLog,
    status: ui.status,
    setStatus: ui.setStatus,
    setMessages: ui.setMessages,
    setIsVisionActive: ui.setIsVisionActive,
    setAssemblyStep: ui.setAssemblyStep,
    PROFILES: ui.PROFILES,
    profile: ui.profile,
    settings: ui.settings,
    reportRecovery,
    processLocalIntent
  });

  // ── SPEAK LOGIC ───────────────────────────────────────────────────────
  const speak = useCallback((text) => {
    if (!text || !ai.hasInteractedRef.current) return;
    if (!ui.PROFILES[ui.profile].voice) {
        addLog(`[SILENT_MODE] Speech suppressed: ${text.slice(0, 30)}...`);
        return;
    }

    const now = Date.now();
    const lastSpeak = localStorage.getItem("jarvis_last_speak");
    if (lastSpeak && (now - parseInt(lastSpeak)) < 500) return;
    localStorage.setItem("jarvis_last_speak", now.toString());
    
    ai.setSonicSentryActive(false);
    ui.setStatus("speaking");
    window.speechSynthesis.cancel();
    
    const prefixes = ["Certainly, Sir. ", "Right away. ", "Manifesting now, Sir. ", "Of course. ", "Initializing... "];
    const randomizedText = (text.length < 30 && Math.random() > 0.7) ? prefixes[Math.floor(Math.random() * prefixes.length)] + text : text;
    
    const utterance = new SpeechSynthesisUtterance(randomizedText);
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.name.includes("Google UK English Male")) || voices.find(v => v.name.includes("Arthur")) || voices.find(v => (v.name.includes("Male") || v.name.includes("David") || v.name.includes("Mark")) && v.lang.includes("en")) || voices.find(v => v.lang.includes("en-GB")) || voices[0];
    utterance.voice = preferredVoice;
    utterance.pitch = (0.9 + Math.random() * 0.15);
    utterance.rate = (0.95 + Math.random() * 0.1);
    utterance.volume = ui.settings.volume || 1;
    utterance.onend = () => {
      ui.setStatus("idle");
      ai.setSonicSentryActive(true);
      if (ai.isContinuousRef.current && ai.startVoice) ai.startVoice();
    };
    setTimeout(() => { window.speechSynthesis.speak(utterance); }, 350);
  }, [ui.PROFILES, ui.profile, ui.settings.volume, ai, addLog, ui]);

  // Bind speak back to the AI state for internal intents
  speakRef.current = speak;
  // Monkeypatch AI processLocalIntent to handle Omega (which needs AI state)
  const originalProcessLocalIntent = processLocalIntent;
  const processLocalIntentWithSingularity = useCallback((text) => {
    if (originalProcessLocalIntent(text)) return true;
    const transcript = text.toLowerCase();
    
    const toggleSingularity = () => {
        ui.setShowSingularityNexus((was) => {
            const newState = !was;
            ai.setOmegaState((prev) => ({ ...prev, active: newState }));
            if (newState) {
                speak("Omega Protocol engaged. Universal Handshake initiating.");
                addLog("OMEGA_SINGULARITY_RECKONING_ACTIVE");
            } else {
                speak("Omega Protocol disengaged. Returning to standard ASI parameters.");
                addLog("OMEGA_STANDDOWN_SUCCESS");
            }
            return newState;
        });
    };

    if (/engage omega protocol|initiate singularity/i.test(transcript)) { toggleSingularity(); return true; }
    if (/disengage omega|stand down singularity/i.test(transcript)) { toggleSingularity(); return true; }
    return false;
  }, [originalProcessLocalIntent, ui, ai, speak, addLog]);

  // We assign it to ai object since it's the one that calls it in processInput
  const aiStateWithSpeak = {
      ...ai, 
      speak, 
      processLocalIntent: processLocalIntentWithSingularity,
      toggleSingularity: () => processLocalIntentWithSingularity("engage omega protocol")
  };

  // ── BACKGROUND SENTINELS ──────────────────────────────────────────────
  useSystemSentinels({
    isInitialized: ui.isInitialized,
    speak,
    addLog,
    thermalData: bio.thermalData,
    status: ui.status,
    executeWithSilentRecovery,
    governancePolicy: ui.governancePolicy,
    setGovernancePolicy: ui.setGovernancePolicy,
    setEvolutionOptimizations,
    setStrategicInsights,
    activityTimerRef
  });

  // ── ORCHESTRATOR POLLING ──────────────────────────────────────────────
  useEffect(() => {
    if (!ui.orchestrationActive) return;

    const pollOrchestrator = async () => {
        try {
            const res = await api.getOrchestratorStatus();
            const { history } = res.data;
            const lastAction = history[history.length - 1];
            if (lastAction && lastAction.status === "EXECUTED") {
                const lastLog = ui.logs[ui.logs.length - 1];
                if (!lastLog || !lastLog.includes(lastAction.intent)) {
                    addLog(`🤖 [AUTONOMOUS_ACTION]: ${lastAction.intent} - ${lastAction.detail}`);
                    addLog(`📚 LEARNING_LOOP: Result indexed in Evolution Engine.`);
                }
            }
        } catch (_err) { console.error("Orchestrator polling error."); }
    };

    const interval = setInterval(pollOrchestrator, 15000); 
    return () => clearInterval(interval);
  }, [ui.orchestrationActive, addLog, ui.logs]);

  // ── SYSTEM BOOT ACTIONS ──────────────────────────────────────────────
  const initializeSystem = () => { ai.hasInteractedRef.current = true; ui.setIsIgniting(true); ui.setShowStartup(true); playSound('start'); ai.initializeSonicSentry(); };
  window.jarvis_test_ignite = initializeSystem;
  
  const handleLogoComplete = useCallback(() => {
    ui.setShowStartup(false);
    addLog("IGNITION_HANDSHAKE_COMPLETE");
    setTimeout(() => { ui.setIsScanning(true); }, 100);
  }, [addLog, ui]);

  const handleVerify = React.useCallback((data) => {
    bio.setBiometricData(data);
    setTimeout(() => {
      ui.setIsScanning(false);
      ui.setAssemblyStep(5);
    }, 500); 
    bio.fetchGeo();
    bio.fetchBio();
    bio.fetchIot();
    speak("Welcome back, Sir.");
  }, [bio, speak, ui]);

  const handleAssemblyComplete = useCallback(() => {
    ui.setIsInitialized(true);
    addLog("MOLECULAR_INTEGRITY_VERIFIED");
  }, [addLog, ui]);

  // ── MULTIMODAL TRUTH ENGINE ──────────────────────────────────────────
  const truthAuditRef = useRef({ lastCheck: 0, failures: 0 });
  const verifyMultimodalTruth = useCallback(async () => {
      const now = Date.now();
      if (now - truthAuditRef.current.lastCheck < 5000) return true;
      truthAuditRef.current.lastCheck = now;
      let truths = { audio: true, ui: true, backend: true, device: true, memory: true };
      try { await api.getHealth(); } catch { truths.backend = false; }
      try {
          const devices = await navigator.mediaDevices.enumerateDevices();
          truths.device = devices.some(d => d.kind === 'audioinput') && !!ai.audioContextRef.current;
      } catch { truths.device = false; }
      try {
          const mres = await api.getMemoryIntegrity();
          truths.memory = mres.data.status !== "CORRUPTED";
      } catch { truths.memory = false; }
      truths.ui = !!ai.analyserRef.current && ui.isInitialized;

      const score = Object.values(truths).filter(Boolean).length * 20; 
      ui.setSystemCoherence(prev => ({
          ...prev,
          backendTruth: truths.backend ? 100 : 0,
          deviceTruth: truths.device ? 100 : 0,
          memoryTruth: truths.memory ? 100 : 0,
          uiTruth: truths.ui ? 100 : 0,
          coherenceScore: score
      }));

      if (score < 50) {
          addLog("MULTIMODAL_TRUTH_FAILURE: COHERENCE_LOW");
          reportRecovery("SYSTEM", "COHERENCE_CRITICAL", { score, truths });
          return false;
      }
      return true;
  }, [ui, addLog, reportRecovery, ai]);

  // We need to inject the truth verification into the AI hook, but we can't easily do it without circular dependencies.
  // We'll set it on the window object as a quick patch for the sonic sentry to call, or we can just skip it here.
  // Actually, we pass verifyMultimodalTruth into the VoiceState if needed, but since we didn't, we can just attach it to window for now.
  window.verifyMultimodalTruth = verifyMultimodalTruth;

  // ── AUTO IDENTITY SYNC ──────────────────────────────────────────────
  useEffect(() => {
    let targetColor = ui.IDENTITY_COLORS.DEFAULT;
    if (ui.mode === "offline") targetColor = ui.IDENTITY_COLORS.COMBAT;
    if (ui.mode === "system") targetColor = ui.IDENTITY_COLORS.SYSTEM;
    if (ui.mode === "stealth") targetColor = ui.IDENTITY_COLORS.STEALTH;
    if (ui.status === "listening") targetColor = ui.IDENTITY_COLORS.LISTENING;
    if (ui.showResonance) targetColor = ui.IDENTITY_COLORS.SYSTEM; 
    if (ui.themeColor !== targetColor) {
      ui.setThemeColor(targetColor);
    }
  }, [ui.mode, ui.status, ui.IDENTITY_COLORS, ui.themeColor, ui.showResonance, ui]);

  // Resonance Sync effect
  useEffect(() => {
    bio.fetchGeo();
    const handleMouse = (e) => {
      const o = 24;
      ui.mouseX.set(e.clientX - o);
      ui.mouseY.set(e.clientY - o);
    };
    window.addEventListener("mousemove", handleMouse);
    const pulseInterval = setInterval(() => { ui.setSystemPulse(prev => !prev); }, 4000);
    const doSync = () => bio.syncResonance(ui.setShowMissionSpire);
    doSync();
    const syncInterval = setInterval(doSync, 12000);
    return () => { window.removeEventListener("mousemove", handleMouse); clearInterval(pulseInterval); clearInterval(syncInterval); };
  }, [bio, ui]);

  // ── BIND CONTEXTS ────────────────────────────────────────────────────
  const uiValue = React.useMemo(() => ({
    _messages: ui.messages, _loading: false, mode: ui.mode, _bootLogs: ui.bootLogs, visionInsight: ui.visionInsight, tier: ui.tier, atmosphere: ui.atmosphere, status: ui.status, logs: ui.logs, isInitialized: ui.isInitialized, mouseX: ui.mouseX, mouseY: ui.mouseY, isScanning: ui.isScanning, showStartup: ui.showStartup, zenithFocus: ui.zenithFocus, isVisionActive: ui.isVisionActive, showFlash: ui.showFlash, showSettings: ui.showSettings, themeColor: ui.themeColor, _showTactical: false, showDiagnostic: ui.showDiagnostic, settings: ui.settings, hudMode: ui.hudMode, showArmory: ui.showArmory, threatLevel: ui.threatLevel, systemPulse: ui.systemPulse, isIgniting: ui.isIgniting, assemblyStep: ui.assemblyStep, layout: ui.layout, showMissionSpire: ui.showMissionSpire, showDominion: ui.showDominion, showResonance: ui.showResonance, showNexus: ui.showNexus, showTacticalSight: ui.showTacticalSight, isSingularityExpanded: ui.isSingularityExpanded, systemCoherence: ui.systemCoherence, showEnterpriseControl: ui.showEnterpriseControl,
    bootStatus: ui.bootStatus, profile: ui.profile, PROFILES: ui.PROFILES,
    healthState, worldState, agentState, actionResults,
    setMessages: ui.setMessages, _setLoading: () => {}, setMode: ui.setMode, setBootLogs: ui.setBootLogs, setVisionInsight: ui.setVisionInsight, setTier: ui.setTier, setAtmosphere: ui.setAtmosphere, setStatus: ui.setStatus, setLogs: ui.setLogs, setIsInitialized: ui.setIsInitialized, setIsScanning: ui.setIsScanning, setShowStartup: ui.setShowStartup, setZenithFocus: ui.setZenithFocus, setIsVisionActive: ui.setIsVisionActive, setShowFlash: ui.setShowFlash, setShowSettings: ui.setShowSettings, setThemeColor: ui.setThemeColor, _setShowTactical: () => {}, setShowDiagnostic: ui.setShowDiagnostic, setSettings: ui.setSettings, setHudMode: ui.setHudMode, setShowArmory: ui.setShowArmory, setThreatLevel: ui.setThreatLevel, setSystemPulse: ui.setSystemPulse, setIsIgniting: ui.setIsIgniting, setAssemblyStep: ui.setAssemblyStep, setLayout: ui.setLayout, setShowMissionSpire: ui.setShowMissionSpire, setShowDominion: ui.setShowDominion, setShowResonance: ui.setShowResonance, setShowNexus: ui.setShowNexus, setShowTacticalSight: ui.setShowTacticalSight, setIsSingularityExpanded: ui.setIsSingularityExpanded, setSystemCoherence: ui.setSystemCoherence, setProfile: ui.setProfile, setShowEnterpriseControl: ui.setShowEnterpriseControl,
    addLog, initializeSystem, handleLogoComplete, handleAssemblyComplete, runAgentMission
  }), [ui, healthState, worldState, agentState, actionResults, addLog, handleLogoComplete, handleAssemblyComplete, runAgentMission]);

  const bioValue = React.useMemo(() => ({
    biometrics: bio.biometrics, iotState: bio.iotState, geoData: bio.geoData, thermalData: bio.thermalData, weatherData: bio.weatherData, newsData: bio.newsData, taskData: bio.taskData, diagnosticData: bio.diagnosticData, foresightData: bio.foresightData, evolutionData: bio.evolutionData, _biometricData: bio.biometricData,
    setBiometrics: bio.setBiometrics, setIotState: bio.setIotState, setGeoData: bio.setGeoData, setThermalData: bio.setThermalData, setWeatherData: bio.setWeatherData, setNewsData: bio.setNewsData, setTaskData: bio.setTaskData, setDiagnosticData: bio.setDiagnosticData, setForesightData: bio.setForesightData, setEvolutionData: bio.setEvolutionData, setBiometricData: bio.setBiometricData
  }), [bio]);

  const aiValue = React.useMemo(() => ({
    isVoiceIgnited: ai.isVoiceIgnited, interimText: ai.interimText, activeForgeId: ai.activeForgeId, forgeLogs: ai.forgeLogs, proposedForge: ai.proposedForge, _isProcessingInput: ai.isProcessingInput, isGhostActive: ai.isGhostActive, _sonicSentryActive: ai.sonicSentryActive, _globalResonanceUrl: ai.globalResonanceUrl, _intelSource: ai.intelSource, acousticStats: ai.acousticStats,
    setIsVoiceIgnited: ai.setIsVoiceIgnited, setInterimText: ai.setInterimText, setActiveForgeId: ai.setActiveForgeId, setForgeLogs: ai.setForgeLogs, setProposedForge: ai.setProposedForge, setIsProcessingInput: ai.setIsProcessingInput, setIsGhostActive: ai.setIsGhostActive, setSonicSentryActive: ai.setSonicSentryActive, setGlobalResonanceUrl: ai.setGlobalResonanceUrl, setIntelSource: ai.setIntelSource, setAcousticStats: ai.setAcousticStats,
    recognitionRef: ai.recognitionRef, audioContextRef: ai.audioContextRef, analyserRef: ai.analyserRef, lastClapTimeRef: ai.lastClapTimeRef, isContinuousRef: ai.isContinuousRef, hasInteractedRef: ai.hasInteractedRef, sessionIdRef: ai.sessionIdRef,
    speak: aiStateWithSpeak.speak, processInput: ai.processInput, startVoice: ai.startVoice, handleVerify, processLocalIntent: aiStateWithSpeak.processLocalIntent,
    omegaState: ai.omegaState, showSingularityNexus: ui.showSingularityNexus,
    toggleSingularity: aiStateWithSpeak.toggleSingularity
  }), [ai, aiStateWithSpeak, handleVerify, ui]);

  return (
    <UIContext.Provider value={uiValue}>
      <BiometricContext.Provider value={bioValue}>
        <AIContext.Provider value={aiValue}>
          {children}
        </AIContext.Provider>
      </BiometricContext.Provider>
    </UIContext.Provider>
  );
};
