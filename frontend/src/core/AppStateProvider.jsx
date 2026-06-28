import React, { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useMotionValue } from "framer-motion";
import { api } from "@/services/api";
import { UIContext, BiometricContext, AIContext } from "@/core/contexts";

// --- UTILS ---
const playSound = (id) => {
  const audio = {
    start: "https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3",
    ignite: "https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3",
    error: "https://assets.mixkit.co/active_storage/sfx/2572/2572-preview.mp3",
    confirm: "https://assets.mixkit.co/active_storage/sfx/2569/2569-preview.mp3",
    STARK_UI_TRANSITION: "https://assets.mixkit.co/active_storage/sfx/2570/2570-preview.mp3"
  };
  if (audio[id]) new Audio(audio[id]).play().catch(() => { });
};

export const AppStateProvider = ({ children }) => {
  // --- STATE DEFINITIONS ---
  
  // UI
  const [_messages, setMessages] = useState([]);
  const [_loading, _setLoading] = useState(false);
  // 🧠 DOMAIN_10: SOVEREIGN_MEMORY_LOAD
  const savedMode = localStorage.getItem("jarvis_mode") || "default";
  const savedColor = localStorage.getItem("jarvis_theme_color") || "#0022ff";
  
  const [mode, setMode] = useState(savedMode);
  const [themeColor, setThemeColor] = useState(savedColor);
  const [_bootLogs, setBootLogs] = useState([]);
  const [visionInsight, setVisionInsight] = useState("Visual cortex synchronized.");
  const [tier, setTier] = useState(20);
  const [atmosphere, setAtmosphere] = useState("Scanning environment...");
  const [status, setStatus] = useState("online");
  const [logs, setLogs] = useState(["SYSTEM_BOOT_COMPLETE", "NEURAL_LINK_ESTABLISHED", "TIER_10_AGI_RESONANCE_ACTIVE"]);
  const [isInitialized, setIsInitialized] = useState(false);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const [isScanning, setIsScanning] = useState(false);
  const [showStartup, setShowStartup] = useState(false);
  const [zenithFocus, setZenithFocus] = useState(0);
  const [isVisionActive, setIsVisionActive] = useState(false);
  const [showFlash, setShowFlash] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  
  // 🛡️ DOMAIN_4: IDENTITY_STANDARDIZATION_MAP
  const IDENTITY_COLORS = useMemo(() => ({
    DEFAULT: "#0022ff", // Signature Deep Blue
    COMBAT: "#ff2828",  // Warning Crimson
    SYSTEM: "#b300ff",  // Sovereign Purple (Memory)
    STEALTH: "#00ff00", // Stealth Green
    LISTENING: "#ffb900" // Interaction Gold
  }), []);
  const [_showTactical, _setShowTactical] = useState(false);
  const [showDiagnostic, setShowDiagnostic] = useState(false);
  const [settings, setSettings] = useState({ volume: 1.0, theme: "STARK", themeColor: "#00f0cc", biometric: true });
  const [hudMode, setHudMode] = useState("CORE");
  const [showArmory, setShowArmory] = useState(true);
  const [threatLevel, setThreatLevel] = useState("NOMINAL");
  const [systemPulse, setSystemPulse] = useState(false);
  const [isIgniting, setIsIgniting] = useState(false);
  const [assemblyStep, setAssemblyStep] = useState(0);
  const [layout, setLayout] = useState("DEFAULT");
  
  // 📦 DOMAIN_3: DEPLOYMENT_READINESS (Config Profiles)
  const [governancePolicy, setGovernancePolicy] = useState({ hud_particles: 1.0, vision_frequency: 1.0, background_scans: True });
  const [evolutionOptimizations, setEvolutionOptimizations] = useState({ voice_threshold_offset: 0.0, vision_scan_interval: 15 });
  const [strategicInsights, setStrategicInsights] = useState({ risks: [], opportunities: [] });
  const [collectiveDebate, setCollectiveDebate] = useState(null);
  const [orchestrationActive, setOrchestrationActive] = useState(false);
  const [profile, setProfile] = useState("desktop");
  const PROFILES = useMemo(() => ({
    desktop: { density: "balanced", voice: true, performance: "high" },
    creator: { density: "immersive", voice: true, performance: "ultra" },
    trading: { density: "high", voice: false, performance: "ultra-low-latency" },
    silent: { density: "minimal", voice: false, performance: "power-save" }
  }), []);
  const [showMissionSpire, setShowMissionSpire] = useState(false);
  const [showDominion, setShowDominion] = useState(false);
  const [showResonance, setShowResonance] = useState(false);
  const [showNexus, setShowNexus] = useState(false);
  const [showTacticalSight, setShowTacticalSight] = useState(false);
  const [isSingularityExpanded, setIsSingularityExpanded] = useState(false);

  // Biometrics/Env
  const [biometrics, setBiometrics] = useState({ heart_rate: 72, temp: 36.6, mood: "Focused" });
  const [iotState, setIotState] = useState({});
  const [geoData, setGeoData] = useState({ lat: "40.7128° N", lon: "74.0060° W", sector: "NEW_YORK_SECTOR" });
  const [thermalData, setThermalData] = useState({ cpu_load: "12%", gpu: 42, ram: "4.2GB" });
  const [weatherData, setWeatherData] = useState({ temp: 22, condition: "Partly Cloudy", wind: 8 });
  const [newsData, setNewsData] = useState([]);
  const [taskData, setTaskData] = useState([]);
  const [diagnosticData, setDiagnosticData] = useState(null);
  const [foresightData, setForesightData] = useState([]);
  const [evolutionData, setEvolutionData] = useState(null);
  const [_biometricData, setBiometricData] = useState(null);

  // AI/Audio
  const [isVoiceIgnited, setIsVoiceIgnited] = useState(false);
  const [interimText, setInterimText] = useState("");
  const [activeForgeId, setActiveForgeId] = useState(null);
  const [forgeLogs, setForgeLogs] = useState([]);
  const [proposedForge, setProposedForge] = useState(null);
  const [_isProcessingInput, setIsProcessingInput] = useState(false);
  const [isGhostActive, setIsGhostActive] = useState(false);
  const [_sonicSentryActive, setSonicSentryActive] = useState(false);
  const [_globalResonanceUrl, setGlobalResonanceUrl] = useState("");
  const [_intelSource, setIntelSource] = useState("CLOUD");
  const [showSingularityNexus, setShowSingularityNexus] = useState(false);
  const [showEnterpriseControl, setShowEnterpriseControl] = useState(false);
  const [omegaState, setOmegaState] = useState({ active: false, frequency: "1.21 EHz", vectors: [] });
  const [acousticStats, setAcousticStats] = useState({
    voiceAdaptation: 100,
    clapAdaptation: 100,
    falseTriggers: 0,
    noiseRejection: 95,
    intelligenceScore: 98
  });
  const noiseFloorRef = useRef(30);
  const [systemCoherence, setSystemCoherence] = useState({
    audioTruth: 100,
    uiTruth: 100,
    backendTruth: 100,
    deviceTruth: 100,
    memoryTruth: 100,
    coherenceScore: 100
  });
  const truthAuditRef = useRef({ lastCheck: 0, failures: 0 });
  
  // 🎭 DOMAIN_2: PRESENCE_INTELLIGENCE_SENTINELS
  const activityTimerRef = useRef({ lastActive: Date.now(), notified: false });
  const [presenceAlert, setPresenceAlert] = useState(null);
  
  const recognitionRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const lastClapTimeRef = useRef(0);
  const isContinuousRef = useRef(false);
  const hasInteractedRef = useRef(false);
  const sessionIdRef = useRef(sessionStorage.getItem("jarvis_session_id") || Math.random().toString(36).substring(7));
  const startVoiceRef = useRef(null);

  if (!sessionStorage.getItem("jarvis_session_id")) {
    sessionStorage.setItem("jarvis_session_id", sessionIdRef.current);
  }

  // --- LOGIC FUNCTIONS ---

  const addLog = useCallback((msg) => {
    setLogs(prev => [...prev.slice(-15), `[${new Date().toLocaleTimeString()}] ${msg}`]);
  }, []);

  // 🛡️ DOMAIN_1: RECOVERY_LOG_HOOK
  const reportRecovery = useCallback(async (component, event, metadata = {}) => {
    try {
      await api.postRecoveryLog({ component, event, metadata });
    } catch {
      console.warn(`[RECOVERY_FAIL] Could not log event for ${component}`);
    }
  }, []);

  // 🤖 DOMAIN_2: AGENTIC_EXECUTION_INTERFACE
  const runAgentMission = useCallback(async (sequenceId) => {
    addLog(`EXECUTING_MISSION: ${sequenceId.toUpperCase()}`);
    try {
        const res = await api.postAgentExecute(sequenceId);
        if (res.data.status === "SUCCESS") {
            addLog(`MISSION_ACCOMPLISHED: ${sequenceId}`);
            speak(`Mission ${sequenceId} executed successfully, Sir.`);
            api.postEvolutionLogSuccess("MISSION_COMPLETE", { mission_id: sequenceId });
        }
    } catch (err) {
        addLog(`MISSION_CRITICAL_FAILURE: ${sequenceId}`);
        speak("I encountered an error during mission execution.");
    }
  }, [addLog, speak]);

  const startVoice = useCallback(async () => {
    startVoiceRef.current = startVoice;
    // 🎤 MIC_HARDWARE_RECOVERY
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const hasMic = devices.some(d => d.kind === 'audioinput');
      if (!hasMic) {
        addLog("CRITICAL: NO_AUDIO_HARDWARE_DETECTED");
        reportRecovery("MIC", "HARDWARE_DISCONNECT");
        return;
      }
      
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(t => t.stop());
      }
    } catch (err) { 
      console.warn("Mic warming failed", err); 
      reportRecovery("MIC", "WARM_UP_FAILURE", { error: err.message });
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    
    // Cleanup old instance if any
    if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch { }
    }

    const rec = new SpeechRecognition();
    recognitionRef.current = rec;
    rec.continuous = true;
    rec.interimResults = true;
    rec.onstart = () => { setStatus("listening"); addLog("VOCAL_LINK_ESTABLISHED"); };
    rec.onerror = (e) => {
        addLog(`VOCAL_ERROR: ${e.error.toUpperCase()}`);
        reportRecovery("VOICE", "RECOGNITION_ERROR", { error: e.error });
        if (e.error === 'no-speech' || e.error === 'network') {
            // These are transient, watchdog will handle restart
        }
    };
    rec.onresult = (e) => {
      const transcript = Array.from(e.results).map(r => r[r.length-1].transcript).join("");
      setInterimText(transcript);
      
      // 🛡️ DOMAIN_3: BARGE_IN_LOGIC
      // If user speaks while JARVIS is responding, KILL THE AUDIO.
      if (status === "speaking" && transcript.trim().length > 2) {
          console.warn("[FULL_DUPLEX] User interrupted. Canceling synthesis...");
          window.speechSynthesis.cancel();
          setStatus("listening");
          reportRecovery("VOICE", "BARGE_IN_DETECTED");
      }

      if (e.results[e.results.length - 1].isFinal) processInput(e.results[e.results.length - 1][0].transcript);
    };
    rec.start();
  }, [addLog, reportRecovery, processInput]);

  useEffect(() => {
    startVoiceRef.current = startVoice;
  }, [startVoice]);

  const speak = useCallback((text) => {
    if (!text || !hasInteractedRef.current) return;
    
    // 📦 DOMAIN_3: PROFILE_VOICE_ENFORCEMENT
    if (!PROFILES[profile].voice) {
        addLog(`[SILENT_MODE] Speech suppressed: ${text.slice(0, 30)}...`);
        return;
    }

    const now = Date.now();
    const lastSpeak = localStorage.getItem("jarvis_last_speak");
    if (lastSpeak && (now - parseInt(lastSpeak)) < 500) return;
    localStorage.setItem("jarvis_last_speak", now.toString());
    
    // 🛡️ DOMAIN_3: DUPLEX_SAFETY
    // We NO LONGER stop recognition here. We keep it running for barge-in support.
    // if (recognitionRef.current) { try { recognitionRef.current.stop(); } catch { } }
    
    setSonicSentryActive(false);
    setStatus("speaking");
    window.speechSynthesis.cancel();
    const prefixes = ["Certainly, Sir. ", "Right away. ", "Manifesting now, Sir. ", "Of course. ", "Initializing... "];
    const randomizedText = (text.length < 30 && Math.random() > 0.7) ? prefixes[Math.floor(Math.random() * prefixes.length)] + text : text;
    const utterance = new SpeechSynthesisUtterance(randomizedText);
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.name.includes("Google UK English Male")) || voices.find(v => v.name.includes("Arthur")) || voices.find(v => (v.name.includes("Male") || v.name.includes("David") || v.name.includes("Mark")) && v.lang.includes("en")) || voices.find(v => v.lang.includes("en-GB")) || voices[0];
    utterance.voice = preferredVoice;
    utterance.pitch = (0.9 + Math.random() * 0.15);
    utterance.rate = (0.95 + Math.random() * 0.1);
    utterance.volume = settings.volume || 1;
    utterance.onend = () => {
      setStatus("idle");
      setSonicSentryActive(true);
      if (isContinuousRef.current && startVoiceRef.current) startVoiceRef.current();
    };
    setTimeout(() => { window.speechSynthesis.speak(utterance); }, 350);
  }, [settings.volume]);

  const toggleSingularity = useCallback(() => {
    setShowSingularityNexus((was) => {
      const newState = !was;
      setOmegaState((prev) => ({ ...prev, active: newState }));
      if (newState) {
        speak("Omega Protocol engaged. Universal Handshake initiating.");
        addLog("OMEGA_SINGULARITY_RECKONING_ACTIVE");
      } else {
        speak("Omega Protocol disengaged. Returning to standard ASI parameters.");
        addLog("OMEGA_STANDDOWN_SUCCESS");
      }
      return newState;
    });
  }, [speak, addLog]);

  // Intent Processing
  const processLocalIntent = useCallback((text) => {
    const transcript = text.toLowerCase();
    if (/engage combat|red alert|threat detected/i.test(transcript)) {
      setMode("offline");
      speak("Sir, engaging combat sub-routines. Primary neural link hardened.");
      addLog("COMBAT_SEQUENCE_INITIATED");
      return true;
    }
    if (/stand down|all clear|cancel combat/i.test(transcript)) {
      setMode("default");
      speak("Standing down, Sir.");
      addLog("COMBAT_STATE_DEACTIVATED");
      return true;
    }
    if (/open lab|armor rig|suit status/i.test(transcript)) { setShowArmory(true); speak("Expanding Armor Rig, Sir."); return true; }
    if (/close armory|hide suit/i.test(transcript)) { setShowArmory(false); speak("Collapsing Armor Rig."); return true; }
    if (/systems diagnostic|status report/i.test(transcript)) { 
      setStatus("thinking"); addLog("INITIATING_SYSTEMS_DIAGNOSTIC...");
      api.getSystemDiagnostic().then(res => { setDiagnosticData(res.data); setShowDiagnostic(true); speak("Full systems diagnostic complete."); }).catch(() => { speak("Diagnostic sequence aborted."); });
      return true; 
    }
    if (/volume up|increase volume/i.test(transcript)) { api.postJarvis("increase volume"); speak("System gain adjusted."); return true; }
    if (/mute|silence audio/i.test(transcript)) { api.postJarvis("mute"); speak("System silenced."); return true; }
    if (/play music/i.test(transcript)) { api.postJarvis("play music"); speak("Sonic environment initiated."); return true; }
    if (/pause music/i.test(transcript)) { api.postJarvis("pause music"); speak("Sonic environment dampening successful."); return true; }
    if (/activate vision|analyze focal plane/i.test(transcript)) {
      setIsVisionActive(true); setStatus("thinking"); speak("Analyzing focal plane.");
      setTimeout(() => { api.postJarvis("vision").then(res => { setMessages(prev => [...prev, { type: "bot", text: res.data.response }]); setIsVisionActive(false); setStatus("idle"); }); }, 2000);
      return true;
    }
    if (/dominion|home control/i.test(transcript)) { setShowDominion(true); speak("Dominion Lattice online."); return true; }
    if (/resonance|system vitals/i.test(transcript)) { setShowResonance(true); speak("Global Resonance online."); return true; }
    if (/command center|nexus/i.test(transcript)) { setShowNexus(true); speak("Omniscient Nexus online."); return true; }
    if (/tactical sight|vision/i.test(transcript)) { setShowTacticalSight(true); speak("Optical focal plane active."); return true; }
    if (/engage omega protocol|initiate singularity/i.test(transcript)) { toggleSingularity(); return true; }
    if (/disengage omega|stand down singularity/i.test(transcript)) { toggleSingularity(); return true; }
    return false;
  }, [speak, addLog, toggleSingularity]);

  // 🧠 DOMAIN_10: MEMORY_INTEGRITY_SYNC
  const syncNeuralMemory = useCallback(async () => {
    try {
        const prefs = { mode, themeColor, volume: settings.volume, biometric: settings.biometric };
        await api.postMemorySync(prefs);
        // Persist locally as fallback
        localStorage.setItem("jarvis_mode", mode);
        localStorage.setItem("jarvis_theme_color", themeColor);
        localStorage.setItem("jarvis_settings", JSON.stringify(settings));
    } catch (err) {
        console.warn("[MEMORY_SYNC_FAIL] Neural link congested. Buffering locally.", err);
    }
  }, [mode, themeColor, settings]);

  const loadNeuralMemory = useCallback(async () => {
    try {
        const res = await api.getMemoryLoad();
        const prefs = res.data.preferences;
        if (prefs) {
            if (prefs.mode) setMode(prefs.mode);
            if (prefs.themeColor) setThemeColor(prefs.themeColor);
            if (prefs.volume || prefs.biometric !== undefined) {
                setSettings(prev => ({ ...prev, ...prefs }));
            }
            addLog("NEURAL_MEMORY: LOADED_FROM_CORE");
        }
    } catch (err) {
        addLog("NEURAL_MEMORY_RECOVERY: USING_LOCAL_BUFFER");
        // Fallback already handled by useState initializers from localStorage
    }
  }, [addLog]);

  useEffect(() => {
    // Initial Load
    if (isInitialized) {
        loadNeuralMemory();
    }
  }, [isInitialized, loadNeuralMemory]);

  useEffect(() => {
    // Periodic Sync (Every 30s or on change)
    if (!isInitialized) return;
    const timer = setTimeout(() => {
        syncNeuralMemory();
    }, 2000); // Sync 2s after any change
    return () => clearTimeout(timer);
  }, [mode, themeColor, settings, isInitialized, syncNeuralMemory]);

  const processInput = useCallback(async (text) => {
    const cleanText = text.trim();
    if (!cleanText) return;

    // 🤝 DOMAIN_9: COLLECTIVE_INTELLIGENCE (Internal Debate for Critical Actions)
    const criticalKeywords = ["deploy", "delete", "format", "shutdown", "ignite", "execute", "combat"];
    if (criticalKeywords.some(k => cleanText.toLowerCase().includes(k))) {
        addLog(`🤝 COLLECTIVE: Critical Intent Detected. Initiating Agent Council Debate...`);
        try {
            const context = { 
                has_errors: visionInsight.includes("error"), 
                threat_level: threatLevel,
                last_failure: logs.some(l => l.includes("FAILURE"))
            };
            const debateRes = await api.postCollectiveDebate(cleanText, context);
            setCollectiveDebate(debateRes.data);
            
            // Log Agent Votes
            Object.entries(debateRes.data.debate).forEach(([agent, result]) => {
                addLog(`🤝 [${agent.toUpperCase()}_AGENT]: ${result.vote} - ${result.reason}`);
            });
            
            if (debateRes.data.decision === "REJECTED") {
                speak("Sir, the Council of Agents has vetoed this action due to safety risks.");
                addLog("🤝 COLLECTIVE: ACTION_VETOED_BY_CONSENSUS");
                return;
            } else if (debateRes.data.decision === "PROCEED_WITH_CAUTION") {
                addLog("🤝 COLLECTIVE: PROCEEDING_WITH_CAUTION_ADVISED");
                speak("Proceeding with caution, Sir. The Council has noted potential risks.");
            }
        } catch (err) {
            console.error("Collective Engine offline.");
        }
    }

    // 🔬 DOMAIN_11: PROJECT_DIAGNOSTIC (On-Demand Audit)
    if (cleanText.toLowerCase().includes("diagnostic mode") || cleanText.toLowerCase().includes("audit project")) {
        addLog("🔬 DIAGNOSTIC: Initiating Project-Wide Deep Audit...");
        speak("Initiating project-wide diagnostic mode, Sir. Scanning all domains for instability.");
        try {
            const res = await api.getProjectDiagnostic();
            const { files_scanned, errors_found, integrity_score, validation_results } = res.data;
            
            addLog(`🔬 AUDIT_COMPLETE: ${files_scanned} files inspected.`);
            addLog(`🔬 INTEGRITY_SCORE: ${integrity_score}%`);
            
            if (errors_found.length > 0) {
                errors_found.forEach(err => {
                    addLog(`🔬 [${err.agent.toUpperCase()}]: ${err.type} in ${err.file} - ${err.message}`);
                });
                speak(`Audit complete. I've identified ${errors_found.length} potential instabilities. Integrity score is at ${integrity_score} percent.`);
            } else {
                addLog("🔬 STATUS: MOLECULAR_INTEGRITY_VERIFIED. No errors found.");
                speak("Audit complete, Sir. The system is architecturally sound.");
            }
            
            addLog(`🔬 VALIDATION: Python [${validation_results.python}], Frontend [${validation_results.frontend}]`);
            return; // Don't proceed to normal intent processing
        } catch (err) {
            addLog("🔬 DIAGNOSTIC_FAILURE: Internal Auditor Offline.");
        }
    }

    // 🤖 DOMAIN_12: AUTONOMOUS_ORCHESTRATION (Mode Toggle)
    if (cleanText.toLowerCase().includes("autonomous mode") || cleanText.toLowerCase().includes("activate ecosystem")) {
        addLog("🤖 ORCHESTRATOR: Activating Autonomous Orchestration Layer...");
        speak("Transitioning to autonomous ecosystem mode, Sir. I am now assuming command of system maintenance and predictive repairs.");
        try {
            await api.postOrchestratorStart();
            setOrchestrationActive(true);
            addLog("🤖 STATUS: AUTONOMOUS_ECOSYSTEM_ONLINE");
            return;
        } catch (err) {
            addLog("🤖 ORCHESTRATOR_FAILURE: Autonomous layer failed to initialize.");
        }
    }
    
    // 🧠 DOMAIN_8: GOAL_DECOMPOSITION
    try {
        const decompRes = await api.postStrategyDecompose(cleanText);
        if (decompRes.data && Array.isArray(decompRes.data) && decompRes.data.length > 1) {
            addLog(`🧠 STRATEGY: Goal Decomposed into ${decompRes.data.length} steps.`);
            for (const step of decompRes.data) {
                await runAgentMission(step);
            }
            return;
        }
    } catch (err) {
        console.error("Strategy Engine offline.");
    }

    setMessages(prev => {
        const next = [...prev, { type: "user", text: cleanText }];
        // 🧠 Automatic Pruning: Keep last 50 messages for UI stability
        return next.length > 50 ? next.slice(-50) : next;
    });
    setInterimText("");
    if (processLocalIntent(cleanText)) return;
    setIsProcessingInput(true);
    setStatus("thinking");
    try {
      const res = await api.postJarvis(cleanText, { session_id: sessionIdRef.current, mode, atmosphere });
      const data = res.data;
      setMessages(prev => [...prev, { type: "bot", text: data.response }]);
      if (data.mode) setMode(data.mode);
      if (data.layout) setLayout(data.layout);
      speak(data.response);
      setStatus("idle");
    } catch { addLog("NEURAL_LINK_FAILURE"); setStatus("idle"); } finally { setIsProcessingInput(false); }
  }, [mode, atmosphere, speak, addLog, processLocalIntent]);

  const initializeSonicSentry = async () => {
    if (audioContextRef.current) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 2048; // 🛡️ Higher resolution for OMEGA_ACOUSTICS
      analyserRef.current = analyser;
      audioContextRef.current = audioContext;
      setSonicSentryActive(true);
      addLog("ACOUSTIC_INTELLIGENCE: ONLINE");

      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Float32Array(bufferLength);
      
      const checkAcoustics = async () => {
        if (!analyserRef.current) { requestAnimationFrame(checkAcoustics); return; }
        
        analyserRef.current.getFloatTimeDomainData(dataArray);
        
        // 🧬 RMS (Root Mean Square) - Volume Intensity
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sum / dataArray.length) * 100;
        
        // 🧬 ZCR (Zero Crossing Rate) - Frequency/Percussion
        let zcr = 0;
        for (let i = 1; i < dataArray.length; i++) {
          if ((dataArray[i] > 0 && dataArray[i-1] < 0) || (dataArray[i] < 0 && dataArray[i-1] > 0)) {
            zcr++;
          }
        }
        
        const now = Date.now();
        
        // 🛡️ ROOM_INTELLIGENCE: Noise Floor Adaptation
        if (now % 5000 < 50) { // Every 5 seconds
            const currentFloor = rms;
            noiseFloorRef.current = (noiseFloorRef.current * 0.9) + (currentFloor * 0.1);
        }

        // 🛡️ ECHO_SHIELD: Ignore self-playback
        const echoMultiplier = status === "speaking" ? 4.5 : 1.2;
        const triggerThreshold = noiseFloorRef.current + (45 * echoMultiplier);

        // 🛡️ CLAP_ADAPTATION: RMS + ZCR Signature
        if (rms > triggerThreshold && zcr > 150 && status === "idle" && now - lastClapTimeRef.current > 1500) {
          
          // 🛡️ MULTIMODAL_TRUTH: AUDIT_BEFORE_IGNITION
          const isTruthValid = await verifyMultimodalTruth();
          if (!isTruthValid) {
              addLog("ACOUSTIC_IGNITION_ABORTED: TRUTH_AUDIT_FAILED");
              return;
          }

          lastClapTimeRef.current = now;
          
          // REJECTION_ENGINE: Filter out constant noise (fan/AC)
          if (rms < noiseFloorRef.current * 3) {
              addLog("ACOUSTIC_REJECTION: AMBIENT_NOISE_DETECTED");
              return;
          }

          addLog(`ACOUSTIC_TRUTH: CLAP_VERIFIED (RMS: ${rms.toFixed(1)})`);
          setIsVoiceIgnited(true);
          isContinuousRef.current = true;
          
          if (!sessionStorage.getItem("jarvis_greeted")) {
            speak("Acoustic calibration complete, Sir. Systems unified.");
            sessionStorage.setItem("jarvis_greeted", "true");
          } else { 
            startVoice(); 
          }
          setAssemblyStep(5);
        }

        requestAnimationFrame(checkAcoustics);
      };
      
      checkAcoustics();
    } catch (err) { 
      addLog("ACOUSTIC_LINK_ERROR"); 
      reportRecovery("VOICE", "ACOUSTIC_SENTRY_FAILURE", { error: err.message });
    }
  };

  // 🛡️ MULTIMODAL_TRUTH_ENGINE: CROSS_SYSTEM_VERIFICATION
  const verifyMultimodalTruth = useCallback(async () => {
      const now = Date.now();
      if (now - truthAuditRef.current.lastCheck < 5000) return true;
      truthAuditRef.current.lastCheck = now;

      let truths = { audio: true, ui: true, backend: true, device: true, memory: true };

      // 1. Backend Truth
      try { await api.getHealth(); } catch { truths.backend = false; }

      // 2. Device Truth
      try {
          const devices = await navigator.mediaDevices.enumerateDevices();
          truths.device = devices.some(d => d.kind === 'audioinput') && !!audioContextRef.current;
      } catch { truths.device = false; }

      // 3. Memory Truth (Domain 10)
      try {
          const mres = await api.getMemoryIntegrity();
          truths.memory = mres.data.status !== "CORRUPTED";
      } catch { truths.memory = false; }

      // 4. UI Truth
      truths.ui = !!analyserRef.current && isInitialized;

      const score = Object.values(truths).filter(Boolean).length * 20; // 5 factors now
      setSystemCoherence(prev => ({
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
  }, [isInitialized, addLog, reportRecovery]);

  // 🛡️ DOMAIN_14: SILENT_RECOVERY_ENGINE
  const executeWithSilentRecovery = useCallback(async (actionName, actionFn) => {
    try {
        return await actionFn();
    } catch (err) {
        addLog(`🛡️ SILENT_RECOVERY: Intent '${actionName}' stalled. Initiating background healing...`);
        // Silently request a self-fix from the backend
        try {
            const fixRes = await api.postSelfFix(actionName, { error: err.message });
            if (fixRes.data.status === "SUCCESS") {
                addLog(`🛡️ SILENT_RECOVERY: Issue resolved. Retrying intent...`);
                return await actionFn(); // Retry after fix
            }
        } catch (fixErr) {
            console.error("Background healing failed.");
        }
        
        // If everything fails, suppress raw error and show a graceful fallback
        addLog(`🛡️ UX_PROTECTION: Operation '${actionName}' deferred to preserve system stability.`);
        return null;
    }
  }, [addLog]);

  // 🛡️ DOMAIN_1: VOICE_ENGINE_WATCHDOG
  useEffect(() => {
    if (status === "listening" && isContinuousRef.current) {
        const watchdog = setInterval(() => {
            // Check if the recognition object has crashed or stopped
            if (!recognitionRef.current || (recognitionRef.current && status !== "listening")) {
                console.warn("[SELF_HEAL] Vocal Link Stalled. Restarting engine...");
                addLog("SELF_HEAL: RESTARTING_VOICE_ENGINE");
                reportRecovery("VOICE", "ENGINE_STALL_RECOVERED");
                startVoice();
            }
        }, 5000);
        return () => clearInterval(watchdog);
    }
  }, [status, startVoice, addLog, reportRecovery]);

  // 🤖 DOMAIN_12: ORCHESTRATOR_POLLING_LOOP
  useEffect(() => {
    if (!orchestrationActive) return;

    const pollOrchestrator = async () => {
        try {
            const res = await api.getOrchestratorStatus();
            const { history, repairs_executed, intelligence_score } = res.data;
            
            // Surface new autonomous actions in the log
            const lastAction = history[history.length - 1];
            if (lastAction && lastAction.status === "EXECUTED") {
                // Prevent duplicate logs if the polling is frequent
                const lastLog = logs[logs.length - 1];
                if (!lastLog || !lastLog.includes(lastAction.intent)) {
                    addLog(`🤖 [AUTONOMOUS_ACTION]: ${lastAction.intent} - ${lastAction.detail}`);
                    addLog(`📚 LEARNING_LOOP: Result indexed in Evolution Engine.`);
                }
            }
        } catch (err) {
            console.error("Orchestrator polling error.");
        }
    };

    const interval = setInterval(pollOrchestrator, 15000); // Poll every 15s
    return () => clearInterval(interval);
  }, [orchestrationActive, addLog, logs]);

  const fetchBio = useCallback(async () => { try { const res = await api.getVitals(); setBiometrics(res.data); } catch { console.warn("Vitals desync"); } }, []);
  const fetchIot = useCallback(async () => { try { const res = await api.getIotState(); setIotState(res.data); } catch { console.warn("IoT desync"); } }, []);
  const fetchGeo = useCallback(async () => { try { const res = await fetch("http://ip-api.com/json/").then(r => r.json()); setGeoData({ lat: `${res.lat}° N`, lon: `${res.lon}° W`, sector: `${res.city.toUpperCase()}_${res.regionName.toUpperCase()}` }); addLog(`SATELLITE_SYNC_CONFIRMED: ${res.city}`); } catch { console.warn("Geo desync"); } }, [addLog]);

  useEffect(() => {
    if (isInitialized) {
      const interval = setInterval(() => { fetchBio(); fetchIot(); }, 5000);
      return () => clearInterval(interval);
    }
  }, [isInitialized, fetchBio, fetchIot]);

  useEffect(() => {
    fetchGeo();
    const handleMouse = (e) => {
      const o = 24;
      mouseX.set(e.clientX - o);
      mouseY.set(e.clientY - o);
    };
    window.addEventListener("mousemove", handleMouse);
    const pulseInterval = setInterval(() => { setSystemPulse(prev => !prev); }, 4000);
    const syncResonance = async () => { 
      try { 
        const res = await api.getGhostSync(); 
        if (res.data.global_frontend_url) setGlobalResonanceUrl(res.data.global_frontend_url); 
        
        let mergedTasks = res.data.tasks || [];
        
        // 🏢 SYNC_ENTERPRISE_CORE
        try {
          const enterpriseRes = await api.getEnterpriseTasks();
          if (enterpriseRes.data) {
            // Map enterprise tasks to HUD format
            const enterpriseTasks = enterpriseRes.data.map(t => ({
              id: t._id,
              label: t.type,
              description: `Repository: ${t.githubRepo || 'Local'}`,
              status: t.status.toUpperCase(), // Normalize to uppercase
              progress: t.progress || 0,
              isEnterprise: true,
              timestamp: t.createdAt
            }));
            mergedTasks = [...mergedTasks, ...enterpriseTasks];
          }
        } catch (e) {
          console.warn("Enterprise desync", e);
        }

        setTaskData(mergedTasks);
        if (res.data.status === "ACTIVE" || mergedTasks.length > 0) setShowMissionSpire(true);
      } catch { 
        console.warn("Resonance desync"); 
      } 
    };
    syncResonance();
    const syncInterval = setInterval(syncResonance, 12000);
    return () => { window.removeEventListener("mousemove", handleMouse); clearInterval(pulseInterval); clearInterval(syncInterval); };
  }, [fetchGeo, mouseX, mouseY]);

  useEffect(() => {
    if (!isInitialized) return;
    const interval = setInterval(async () => {
      try {
        const res = await api.getResonanceVitals();
        setThermalData(res.data);
        if (res.data.insight) addLog(res.data.insight);
      } catch { console.warn("Thermal desync"); }
    }, 5000);
    return () => clearInterval(interval);
  }, [isInitialized, addLog]);

  // 🎭 DOMAIN_2: PROACTIVE_PRESENCE_LOOP
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

        // 👁️ DOMAIN_3: VISION_INTELLIGENCE_SENTINEL (Governance-Aware)
        if (isInitialized && count % 15 === 0 && governancePolicy.background_scans) { 
            try {
                const visRes = await api.getVisionAnalysis();
                if (visRes.data.errors && visRes.data.errors.length > 0) {
                    visRes.data.errors.forEach(err => speak(err));
                }
            } catch (err) {
                console.error("Vision Cortex link offline.");
            }
        }

        count++;
    }, 60000); // Check every minute

    // ⚖️ DOMAIN_6: GOVERNANCE_POLICY_SYNC
    const policySync = setInterval(async () => {
        if (!isInitialized) return;
        try {
            const res = await api.getGovernancePolicy();
            setGovernancePolicy(res.data);
            if (res.data.mode === "POWER_SAVE") {
                addLog("⚖️ GOVERNANCE: HARDWARE_PRESSURE_DETECTED. ENTERING_RESOURCE_ETHICS_MODE.");
                api.postEvolutionLogResource("SYSTEM_LOAD", 90);
            }
        } catch (err) {
            console.error("Governance sync failure.");
        }
    }, 30000);

    // 📈 DOMAIN_7: EVOLUTION_OPTIMIZATION_SYNC
    const evolutionSync = setInterval(async () => {
        if (!isInitialized) return;
        try {
            const res = await api.getEvolutionOptimizations();
            setEvolutionOptimizations(res.data);
        } catch (err) {
            console.error("Evolution sync failure.");
        }
    }, 120000); // Every 2 minutes

    // 🧠 DOMAIN_8: STRATEGIC_REASONING_LOOP
    const strategyLoop = setInterval(async () => {
        if (!isInitialized) return;
        try {
            const signals = { cpu: parseInt(thermalData.cpu_load), gpu: thermalData.gpu, battery: 100 };
            const res = await api.postStrategyAnalyze(signals, { engagement_rate: 0.2 });
            setStrategicInsights(res.data);
            if (res.data.risks.length > 0) {
                res.data.risks.forEach(risk => addLog(`⚠️ STRATEGY_FORECAST: ${risk.type} risk detected.`));
            }
        } catch (err) {
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
        window.removeEventListener("mousemove", handleActivity);
        window.removeEventListener("keydown", handleActivity);
    };
  }, [isInitialized, speak, addLog, thermalData, status]);

  // 🛡️ DOMAIN_4: AUTO_IDENTITY_SYNC
  useEffect(() => {
    let targetColor = IDENTITY_COLORS.DEFAULT;
    if (mode === "offline") targetColor = IDENTITY_COLORS.COMBAT;
    if (mode === "system") targetColor = IDENTITY_COLORS.SYSTEM;
    if (mode === "stealth") targetColor = IDENTITY_COLORS.STEALTH;
    if (status === "listening") targetColor = IDENTITY_COLORS.LISTENING;
    
    // Override with Memory color if in specific mode (purple)
    if (showResonance) targetColor = IDENTITY_COLORS.SYSTEM; // Memory focus
    
    if (themeColor !== targetColor) {
      setThemeColor(targetColor);
    }
  }, [mode, status, IDENTITY_COLORS, themeColor, showResonance]);

  const initializeSystem = () => { hasInteractedRef.current = true; setIsIgniting(true); setShowStartup(true); playSound('start'); initializeSonicSentry(); };
  window.jarvis_test_ignite = initializeSystem;
  const handleLogoComplete = useCallback(() => {
    setShowStartup(false);
    addLog("IGNITION_HANDSHAKE_COMPLETE");
    setTimeout(() => {
      setIsScanning(true);
    }, 100);
  }, [addLog]);

  const handleVerify = React.useCallback((data) => {
    setBiometricData(data);
    // 🛡️ O.M.E.G.A. STABILITY: DELAY UNMOUNT TO PREVENT CANVAS RACE CONDITIONS
    setTimeout(() => {
      setIsScanning(false);
      setAssemblyStep(5);
    }, 500); 
    fetchGeo();
    fetchBio();
    fetchIot();
    speak("Welcome back, Sir.");
  }, [fetchGeo, fetchBio, fetchIot, speak]);

  const handleAssemblyComplete = useCallback(() => {
    setIsInitialized(true);
    addLog("MOLECULAR_INTEGRITY_VERIFIED");
  }, [addLog]);

  const bootStatus = useMemo(() => ({
    auraActivated: isIgniting,
    startupComplete: !showStartup,
    scannerComplete: !isScanning,
    bootComplete: isInitialized,
    systemReady: isInitialized && assemblyStep === 5,
    isInitializing: !isInitialized
  }), [isIgniting, showStartup, isScanning, isInitialized, assemblyStep]);

  // --- PROVIDER VALUES ---

  const uiValue = React.useMemo(() => ({
    _messages, _loading, mode, _bootLogs, visionInsight, tier, atmosphere, status, logs, isInitialized, mouseX, mouseY, isScanning, showStartup, zenithFocus, isVisionActive, showFlash, showSettings, themeColor, _showTactical, showDiagnostic, settings, hudMode, showArmory, threatLevel, systemPulse, isIgniting, assemblyStep, layout, showMissionSpire, showDominion, showResonance, showNexus, showTacticalSight, isSingularityExpanded, systemCoherence, showEnterpriseControl,
    bootStatus, profile, PROFILES,
    setMessages, _setLoading, setMode, setBootLogs, setVisionInsight, setTier, setAtmosphere, setStatus, setLogs, setIsInitialized, setIsScanning, setShowStartup, setZenithFocus, setIsVisionActive, setShowFlash, setShowSettings, setThemeColor, _setShowTactical, setShowDiagnostic, setSettings, setHudMode, setShowArmory, setThreatLevel, setSystemPulse, setIsIgniting, setAssemblyStep, setLayout, setShowMissionSpire, setShowDominion, setShowResonance, setShowNexus, setShowTacticalSight, setIsSingularityExpanded, setSystemCoherence, setProfile, setShowEnterpriseControl,
    addLog, initializeSystem, handleLogoComplete, handleAssemblyComplete, runAgentMission
  }), [_messages, _loading, mode, _bootLogs, visionInsight, tier, atmosphere, status, logs, isInitialized, mouseX, mouseY, isScanning, showStartup, zenithFocus, isVisionActive, showFlash, showSettings, themeColor, _showTactical, showDiagnostic, settings, hudMode, showArmory, threatLevel, systemPulse, isIgniting, assemblyStep, layout, showMissionSpire, showDominion, showResonance, showNexus, showTacticalSight, isSingularityExpanded, bootStatus, addLog, handleLogoComplete, handleAssemblyComplete, systemCoherence, showEnterpriseControl]);

  const bioValue = React.useMemo(() => ({
    biometrics, iotState, geoData, thermalData, weatherData, newsData, taskData, diagnosticData, foresightData, evolutionData, _biometricData,
    setBiometrics, setIotState, setGeoData, setThermalData, setWeatherData, setNewsData, setTaskData, setDiagnosticData, setForesightData, setEvolutionData, setBiometricData
  }), [biometrics, iotState, geoData, thermalData, weatherData, newsData, taskData, diagnosticData, foresightData, evolutionData, _biometricData]);

  const aiValue = React.useMemo(() => ({
    isVoiceIgnited, interimText, activeForgeId, forgeLogs, proposedForge, _isProcessingInput, isGhostActive, _sonicSentryActive, _globalResonanceUrl, _intelSource, acousticStats,
    setIsVoiceIgnited, setInterimText, setActiveForgeId, setForgeLogs, setProposedForge, setIsProcessingInput, setIsGhostActive, setSonicSentryActive, setGlobalResonanceUrl, setIntelSource, setAcousticStats,
    recognitionRef, audioContextRef, analyserRef, lastClapTimeRef, isContinuousRef, hasInteractedRef, sessionIdRef,
    speak, processInput, startVoice, handleVerify, processLocalIntent,
    omegaState, showSingularityNexus,
    toggleSingularity
  }), [isVoiceIgnited, interimText, activeForgeId, forgeLogs, proposedForge, _isProcessingInput, isGhostActive, _sonicSentryActive, _globalResonanceUrl, _intelSource, speak, processInput, startVoice, handleVerify, processLocalIntent, omegaState, showSingularityNexus, toggleSingularity, acousticStats]);

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
