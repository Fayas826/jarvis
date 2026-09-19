/**
 * useUIState — UI Domain
 * Manages: themes, modes, HUD panel toggles, layout, system coherence, logs
 * Consumers re-render ONLY when UI state changes (not voice/biometric ticks)
 */
import { useState, useCallback, useMemo } from "react";
import { useMotionValue } from "framer-motion";
import { api } from "@/services/api";

const SOUND_MAP = {
  start:               "https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3",
  ignite:              "https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3",
  error:               "https://assets.mixkit.co/active_storage/sfx/2572/2572-preview.mp3",
  confirm:             "https://assets.mixkit.co/active_storage/sfx/2569/2569-preview.mp3",
  STARK_UI_TRANSITION: "https://assets.mixkit.co/active_storage/sfx/2570/2570-preview.mp3",
};

export const playSound = (id) => {
  if (SOUND_MAP[id]) new Audio(SOUND_MAP[id]).play().catch(() => {});
};

export const IDENTITY_COLORS_MAP = {
  DEFAULT:   "#0022ff",
  COMBAT:    "#ff2828",
  SYSTEM:    "#b300ff",
  STEALTH:   "#00ff00",
  LISTENING: "#ffb900",
};

export function useUIState() {
  const savedMode  = localStorage.getItem("jarvis_mode")        || "default";
  const savedColor = localStorage.getItem("jarvis_theme_color") || "#0022ff";

  // ── Core UI ──────────────────────────────────────────────────────────
  const [messages,    setMessages]    = useState([]);
  const [mode,        setMode]        = useState(savedMode);
  const [themeColor,  setThemeColor]  = useState(savedColor);
  const [bootLogs,    setBootLogs]    = useState([]);
  const [visionInsight, setVisionInsight] = useState("Visual cortex synchronized.");
  const [tier,        setTier]        = useState(20);
  const [atmosphere,  setAtmosphere]  = useState("Scanning environment...");
  const [status,      setStatus]      = useState("online");
  const [logs,        setLogs]        = useState(["SYSTEM_BOOT_COMPLETE", "NEURAL_LINK_ESTABLISHED", "TIER_10_AGI_RESONANCE_ACTIVE"]);
  const [isInitialized, setIsInitialized] = useState(false);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // ── Boot / Scanning sequence ──────────────────────────────────────────
  const [isScanning,  setIsScanning]  = useState(false);
  const [showStartup, setShowStartup] = useState(false);
  const [isIgniting,  setIsIgniting]  = useState(false);
  const [assemblyStep, setAssemblyStep] = useState(0);

  // ── HUD panels ───────────────────────────────────────────────────────
  const [zenithFocus,          setZenithFocus]          = useState(0);
  const [isVisionActive,       setIsVisionActive]       = useState(false);
  const [showFlash,            setShowFlash]            = useState(false);
  const [showSettings,         setShowSettings]         = useState(false);
  const [showDiagnostic,       setShowDiagnostic]       = useState(false);
  const [showArmory,           setShowArmory]           = useState(true);
  const [showMissionSpire,     setShowMissionSpire]     = useState(false);
  const [showDominion,         setShowDominion]         = useState(false);
  const [showResonance,        setShowResonance]        = useState(false);
  const [showNexus,            setShowNexus]            = useState(false);
  const [showTacticalSight,    setShowTacticalSight]    = useState(false);
  const [isSingularityExpanded,setIsSingularityExpanded] = useState(false);
  const [showEnterpriseControl,setShowEnterpriseControl] = useState(false);
  const [showSingularityNexus, setShowSingularityNexus] = useState(false);

  // ── System settings ───────────────────────────────────────────────────
  const [hudMode,     setHudMode]     = useState("CORE");
  const [layout,      setLayout]      = useState("DEFAULT");
  const [settings,    setSettings]    = useState({ volume: 1.0, theme: "STARK", themeColor: "#00f0cc", biometric: true });
  const [threatLevel, setThreatLevel] = useState("NOMINAL");
  const [systemPulse, setSystemPulse] = useState(false);
  const [systemCoherence, setSystemCoherence] = useState({
    audioTruth: 100, uiTruth: 100, backendTruth: 100,
    deviceTruth: 100, memoryTruth: 100, coherenceScore: 100
  });

  // ── Profile / governance ──────────────────────────────────────────────
  const [profile, setProfile] = useState("desktop");
  const [governancePolicy, setGovernancePolicy] = useState({
    hud_particles: 1.0, vision_frequency: 1.0, background_scans: true
  });
  const [orchestrationActive, setOrchestrationActive] = useState(false);

  const PROFILES = useMemo(() => ({
    desktop:  { density: "balanced",  voice: true,  performance: "high" },
    creator:  { density: "immersive", voice: true,  performance: "ultra" },
    trading:  { density: "high",      voice: false, performance: "ultra-low-latency" },
    silent:   { density: "minimal",   voice: false, performance: "power-save" },
  }), []);

  const IDENTITY_COLORS = useMemo(() => IDENTITY_COLORS_MAP, []);

  // ── Shared log writer ─────────────────────────────────────────────────
  const addLog = useCallback((msg) => {
    setLogs(prev => [...prev.slice(-15), `[${new Date().toLocaleTimeString()}] ${msg}`]);
  }, []);

  // ── Memory sync ───────────────────────────────────────────────────────
  const syncNeuralMemory = useCallback(async () => {
    try {
      const prefs = { mode, themeColor, volume: settings.volume, biometric: settings.biometric };
      await api.postMemorySync(prefs);
      localStorage.setItem("jarvis_mode",        mode);
      localStorage.setItem("jarvis_theme_color", themeColor);
      localStorage.setItem("jarvis_settings",    JSON.stringify(settings));
    } catch (_err) {
      console.warn("[MEMORY_SYNC_FAIL] Buffering locally.", _err.message);
    }
  }, [mode, themeColor, settings]);

  const loadNeuralMemory = useCallback(async () => {
    try {
      const res  = await api.getMemoryLoad();
      const prefs = res.data.preferences;
      if (prefs) {
        if (prefs.mode)      setMode(prefs.mode);
        if (prefs.themeColor) setThemeColor(prefs.themeColor);
        if (prefs.volume !== undefined || prefs.biometric !== undefined)
          setSettings(prev => ({ ...prev, ...prefs }));
        addLog("NEURAL_MEMORY: LOADED_FROM_CORE");
      }
    } catch {
      addLog("NEURAL_MEMORY_RECOVERY: USING_LOCAL_BUFFER");
    }
  }, [addLog]);

  const bootStatus = useMemo(() => ({
    auraActivated:   isIgniting,
    startupComplete: !showStartup,
    scannerComplete: !isScanning,
    bootComplete:    isInitialized,
    systemReady:     isInitialized && assemblyStep === 5,
    isInitializing:  !isInitialized,
  }), [isIgniting, showStartup, isScanning, isInitialized, assemblyStep]);

  return {
    // state
    messages, mode, themeColor, bootLogs, visionInsight, tier, atmosphere, status,
    logs, isInitialized, mouseX, mouseY, isScanning, showStartup, zenithFocus,
    isVisionActive, showFlash, showSettings, showDiagnostic, settings, hudMode,
    showArmory, threatLevel, systemPulse, isIgniting, assemblyStep, layout,
    showMissionSpire, showDominion, showResonance, showNexus, showTacticalSight,
    isSingularityExpanded, systemCoherence, showEnterpriseControl, showSingularityNexus,
    bootStatus, profile, PROFILES, IDENTITY_COLORS, governancePolicy, orchestrationActive,
    // setters
    setMessages, setMode, setThemeColor, setBootLogs, setVisionInsight, setTier,
    setAtmosphere, setStatus, setLogs, setIsInitialized, setIsScanning, setShowStartup,
    setZenithFocus, setIsVisionActive, setShowFlash, setShowSettings, setShowDiagnostic,
    setSettings, setHudMode, setShowArmory, setThreatLevel, setSystemPulse, setIsIgniting,
    setAssemblyStep, setLayout, setShowMissionSpire, setShowDominion, setShowResonance,
    setShowNexus, setShowTacticalSight, setIsSingularityExpanded, setSystemCoherence,
    setShowEnterpriseControl, setShowSingularityNexus, setProfile, setGovernancePolicy,
    setOrchestrationActive,
    // actions
    addLog, syncNeuralMemory, loadNeuralMemory,
  };
}
