import React, { Suspense } from "react";
import { createPortal } from "react-dom";
import { api } from "@/services/api";
import { motion, AnimatePresence } from "framer-motion";

import ArcReactor from "@/features/core/ArcReactor";
import StarField from "@/features/simulations/Stars";
import Sidebar from "@/features/hud/Sidebar";
import CommandFeed from "@/features/hud/CommandFeed";
import ErrorBoundary from "@/features/core/ErrorBoundary";
import HoloMetadata from "@/features/hud/HoloMetadata";
import ParallaxField from "@/features/simulations/ParallaxField";
import GlobalScanner from "@/features/scanners/GlobalScanner";
import VitalsMonitor from "@/features/hud/VitalsMonitor";
import SpotifyWidget from "@/features/hud/SpotifyWidget";
import WeatherWidget from "@/features/hud/WeatherWidget";
import IntelligenceBrief from "@/features/hud/IntelligenceBrief";
import NewsTicker from "@/features/hud/NewsTicker";
import TopMetrics from "@/features/hud/TopMetrics";
import HardwareHeatMap from "@/features/simulations/HardwareHeatMap";
import AuraHUD from "@/features/hud/SystemCoherenceHUD";
import StartupLogo from "@/features/core/StartupLogo";
import ForgeHandshake from "@/features/core/ForgeHandshake";
import CinematicOverlay from "@/features/hud/CinematicOverlay";
import LeftPanel from "@/features/hud/LeftPanel";
import MolecularAssembly from "@/features/hud/MolecularAssembly";
import DominionHUD from "@/features/hud/DominionHUD";
import DiagnosticHUD from "@/features/hud/DiagnosticHUD";
import SettingsHUD from "@/features/hud/SettingsHUD";
import ResonanceHUD from "@/features/hud/ResonanceHUD";
import TacticalSight from "@/features/scanners/TacticalSight";
import NeuralIntercept from "@/features/hud/NeuralIntercept";
import NexusHUD from "@/features/hud/NexusHUD";
import MissionLabHUD from "@/features/hud/MissionLabHUD";
import ForesightHUD from "@/features/hud/ForesightHUD";
import SentienceEvolution from "@/features/simulations/SentienceEvolution";
import NetworkPresence from "@/features/hud/NetworkPresence";
import CommandExecutionPanel from "@/features/hud/CommandExecutionPanel";
import HologramProjector from "@/features/hud/HologramProjector";
import TacticalThreatScanner from "@/features/scanners/TacticalThreatScanner";
import PerceptionHUD from "@/features/hud/PerceptionHUD";
import PersonalityHUD from "@/features/hud/PersonalityHUD";
import NotificationCenter from "@/features/hud/NotificationCenter";

// 🚀 HEAVY_MODULE_LAZY_LOADING
const ZenithPortal = React.lazy(() => import("@/features/simulations/ZenithPortal"));
const SingularityNexus = React.lazy(() => import("@/features/simulations/SingularityNexus"));
const Armory = React.lazy(() => import("@/features/simulations/Armory"));
const FaceScanner = React.lazy(() => import("@/features/scanners/FaceScanner"));
const SingularityCanvas = React.lazy(() => import("@/features/simulations/SingularityCanvas"));
const SatelliteMap = React.lazy(() => import("@/features/simulations/SatelliteMap"));
const NetworkHeatmap = React.lazy(() => import("@/features/simulations/NetworkHeatmap"));

import { Canvas } from "@react-three/fiber";
import { View, Preload } from "@react-three/drei";

import { useAppState } from "@/core/contexts";

// 🧊 STABLE_GL_CONFIG: Prevent renderer re-initialization on state changes
const GL_CONFIG = { 
  antialias: true, 
  alpha: true, 
  powerPreference: "high-performance",
  preserveDrawingBuffer: true 
};

// 🛡️ MEMOIZED_CANVAS: The Singleton WebGL Engine
const SovereignCanvas = React.memo(({ eventSource }) => (
  <div className="fixed inset-0 z-[10] pointer-events-none">
    <Canvas
      eventSource={eventSource}
      camera={{ position: [0, 0, 8], fov: 60 }}
      dpr={[1, 2]}
      gl={GL_CONFIG}
      shadows
    >
      <Suspense fallback={null}>
         <View.Port />
         <Preload all />
      </Suspense>
    </Canvas>
  </div>
));

export default function MainLayout() {
  /* eslint-disable no-unused-vars -- merged app context; panels reserve many fields */
  const {
    mode,
    tier,
    status,
    logs,
    isInitialized,
    biometrics,
    iotState,
    geoData,
    isScanning,
    showStartup,
    zenithFocus,
    visionInsight,
    thermalData,
    weatherData,
    newsData,
    taskData,
    diagnosticData,
    isVisionActive,
    showFlash,
    showSettings,
    themeColor,
    showDiagnostic,
    settings,
    isSuitActive,
    isProjecting,
    hudMode,
    isStabilized,
    showArmory,
    threatLevel,
    systemPulse,
    isIgniting,
    assemblyStep,
    isVoiceIgnited,
    activeForgeId,
    forgeLogs,
    proposedForge,
    showDominion,
    showResonance,
    showNexus,
    showTacticalSight,
    isSingularityExpanded,
    layout,
    showMissionSpire,
    foresightData,
    evolutionData,
    interimText,
    setMessages,
    setMode,
    setStatus,
    setLogs,
    setIsInitialized,
    setShowStartup,
    setZenithFocus,
    setThermalData,
    setWeatherData,
    setNewsData,
    setTaskData,
    setDiagnosticData,
    setIsVisionActive,
    setShowFlash,
    setShowSettings,
    setThemeColor,
    setHudMode,
    setShowDiagnostic,
    setSettings,
    setShowArmory,
    setThreatLevel,
    setSystemPulse,
    setIsIgniting,
    setAssemblyStep,
    setIsVoiceIgnited,
    setActiveForgeId,
    setForgeLogs,
    setProposedForge,
    setShowDominion,
    setShowResonance,
    setShowNexus,
    setShowTacticalSight,
    setIsSingularityExpanded,
    setLayout,
    setShowMissionSpire,
    setForesightData,
    setEvolutionData,
    setInterimText,
    mouseX,
    mouseY,
    acousticStats,
    systemCoherence,
    initializeSystem,
    processInput,
    addLog,
    handleVerify,
    processLocalIntent,
    handleOSControl,
    handleOptimize,
    handleDominionControl,
    startVoice,
    handleLogoComplete,
    handleAssemblyComplete
  } = useAppState();
  /* eslint-enable no-unused-vars */

  const containerRef = React.useRef(null);

  // 🛡️ WEBGL_WATCHDOG: RENDERING PIPELINE HARDENING
  React.useEffect(() => {
    const canvas = containerRef.current?.querySelector('canvas');
    if (!canvas) return;

    const handleLost = (e) => {
      e.preventDefault();
      addLog("CRITICAL: GPU_CONTEXT_LOST. INITIATING_NEURAL_RECOVERY...");
    };

    const handleRestored = () => {
      addLog("SUCCESS: GPU_CONTEXT_RESTORED. REBINDING_PIPELINE...");
    };

    canvas.addEventListener('webglcontextlost', handleLost, false);
    canvas.addEventListener('webglcontextrestored', handleRestored, false);
    return () => {
      canvas.removeEventListener('webglcontextlost', handleLost);
      canvas.removeEventListener('webglcontextrestored', handleRestored);
    };
  }, [addLog]);

  const cursorLayer =
    typeof document !== "undefined"
      ? createPortal(
          <motion.div
            id="custom-cursor"
            className="fixed pointer-events-none"
            style={{
              x: mouseX,
              y: mouseY,
              zIndex: 2147483647,
              left: 0,
              top: 0,
              willChange: "transform",
            }}
          >
            <div className="relative flex items-center justify-center w-12 h-12">
              <motion.div
                animate={{ rotate: 360, scale: status === "speaking" ? [1, 1.3, 1] : 1 }}
                transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
                className="absolute w-12 h-12 border-2 border-cyan-400/30 rounded-full border-t-cyan-400"
              />
              <div className="w-px h-8 bg-cyan-400/80 absolute shadow-[0_0_10px_cyan]" />
              <div className="h-px w-8 bg-cyan-400/80 absolute shadow-[0_0_10px_cyan]" />
              <motion.div
                animate={{ scale: [1, 1.5, 1] }}
                transition={{ duration: 0.5, repeat: Infinity }}
                className="w-1.5 h-1.5 bg-white rounded-full shadow-[0_0_15px_white]"
              />
            </div>
          </motion.div>,
          document.body
        )
      : null;

  return (
    <>
    <div
      ref={containerRef}
      className="h-screen w-full flex text-white font-sans relative overflow-hidden bg-black"
      style={{
        "--stark-glow": themeColor,
        "--stark-glow-rgb": themeColor === "#00f0ff" ? "0, 240, 255" :
          themeColor === "#ffb900" ? "255, 185, 0" :
            themeColor === "#ff0000" ? "255, 0, 0" : "255, 0, 255"
      }}
    >
      {/* 🔮 OMEGA_SINGULARITY_NEXUS */}
      <AnimatePresence>
        {showNexus && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-3000"
          >
            <Suspense fallback={<div className="fixed inset-0 bg-black z-500 flex items-center justify-center text-cyan-500 font-mono tracking-[0.5em] animate-pulse">INITIATING_SINGULARITY_NEXUS...</div>}>
              <ErrorBoundary>
                <SingularityNexus themeColor={themeColor} />
              </ErrorBoundary>
            </Suspense>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isVisionActive && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 pointer-events-none z-1000"
          >
            <div className="fixed inset-0 bg-black/90 backdrop-blur-md z-499" />
            <motion.div
              animate={{ y: ["-100vh", "100vh"] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              className="w-full h-px bg-cyan-400 shadow-[0_0_20px_cyan] opacity-60"
            />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-500/5 rounded-full blur-[120px] animate-pulse z-2000">
              <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-cyan-400" />
              <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-cyan-400" />
              <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-cyan-400" />
              <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-cyan-400" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {proposedForge && (
          <ForgeHandshake
            manifest={proposedForge}
            onIgnite={async () => {
              const files = proposedForge.files;
              setActiveForgeId(proposedForge.forge_id);
              setForgeLogs(prev => [...prev, { action: "IGNITING", target: proposedForge.forge_id }]);
              setProposedForge(null);
              try {
                const res = await api.postForgeExecute(files);
                addLog(`FORGE_SUCCESS: ${res.data.response}`);
              } catch {
                addLog("FORGE_CRITICAL_FAILURE: Manifest corrupted.");
              }
            }}
            onAbort={() => setProposedForge(null)}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {!isInitialized && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute top-8 left-8 z-20 pointer-events-none"
          >
            <div className="flex flex-col gap-1">
              <div className="w-12 h-px bg-cyan-500/40" />
              <span className="text-[10px] font-mono text-cyan-500/40 uppercase tracking-[0.4em]">SECURE_AUTH_V20.0</span>
              <h1 className="text-xl font-black text-white tracking-[0.5em] uppercase">
                Property of Stark Industries
              </h1>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <StarField active={isSuitActive} />
      <AnimatePresence>
        {isInitialized && <ParallaxField mouseX={mouseX} mouseY={mouseY} />}
      </AnimatePresence>
      <div className="absolute inset-0 scanline-overlay z-501 pointer-events-none opacity-50" />
      <div className="absolute inset-0 tactical-grid opacity-25 pointer-events-none z-0" />

      {!isInitialized ? (
        <div className="fixed inset-0 z-[5] flex flex-col items-center justify-center bg-black overflow-hidden">
          <motion.div
            initial={{ scale: 1.1, x: -20 }}
            animate={{ scale: 1, x: 20 }}
            transition={{ duration: 30, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" }}
            className="absolute inset-0 z-200 pointer-events-none"
          >
            <img src="/init_bg.png" alt="Stark Penthouse" className="w-full h-full object-cover opacity-60" />
          </motion.div>

          <CinematicOverlay active={!showStartup && !isScanning}>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <Suspense fallback={null}>
                <ErrorBoundary>
                  <SingularityCanvas highPerf={true} mode="initializing" />
                </ErrorBoundary>
              </Suspense>

              <div className="relative z-10 flex flex-col items-center gap-12">
                <AnimatePresence mode="wait">
                  {showStartup ? (
                    <StartupLogo key="startup" onComplete={handleLogoComplete} />
                  ) : !isScanning ? (
                    <motion.div
                      key="aura"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 1.2, filter: "blur(20px)" }}
                      className="w-[500px] h-[500px] flex items-center justify-center cursor-pointer pointer-events-auto"
                      onClick={initializeSystem}
                    >
                      <AuraHUD 
                        mode={mode} 
                        isIgniting={isIgniting} 
                        themeColor={themeColor} 
                        systemCoherence={systemCoherence} 
                      />
                    </motion.div>
                  ) : (
                    <motion.div
                      key="scanner"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 1.1 }}
                      className="w-screen h-screen flex flex-col items-center justify-center bg-black"
                    >
                      <React.Suspense fallback={<div className="text-cyan-500 font-mono text-sm tracking-widest">INITIALIZING BIOMETRICS...</div>}>
                        <FaceScanner onVerify={handleVerify} />
                      </React.Suspense>
                    </motion.div>
                  )}
                </AnimatePresence>

                <MolecularAssembly 
                  step={assemblyStep} 
                  onComplete={handleAssemblyComplete} 
                />
              </div>
            </div>
          </CinematicOverlay>
        </div>
      ) : (
        <div className="fixed inset-0 z-[5] bg-[#000508] overflow-hidden">
          <Suspense fallback={null}>
            <ErrorBoundary>
              <SingularityCanvas highPerf={true} mode="stable" />
            </ErrorBoundary>
          </Suspense>
          <main className="h-screen w-screen relative z-10 overflow-hidden pointer-events-none flex flex-col items-center justify-center">
            
            {/* Left Interface Nodes */}
            <div className="absolute left-8 top-8 w-72 flex flex-col gap-5 pointer-events-none">
              <div className="pointer-events-auto"><VitalsMonitor status={status} threatLevel={threatLevel} /></div>
              <div className="pointer-events-auto"><IntelligenceBrief active={isInitialized} /></div>
            </div>

            {/* Armory / Sentience Node */}
            <AnimatePresence>
              {showArmory && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0, width: isSingularityExpanded ? "500px" : "18rem" }}
                  exit={{ opacity: 0, y: 20 }}
                  className="absolute left-8 bottom-8 pointer-events-auto z-110"
                >
                  <div className="flex flex-col-reverse gap-2">
                    <Suspense fallback={<div className="h-48 animate-pulse bg-white/5" />}>
                      <Armory
                        status={status}
                        systemPulse={systemPulse}
                        themeColor={themeColor}
                        vitals={thermalData}
                        isExpanded={isSingularityExpanded}
                        onToggleSentience={() => setIsSingularityExpanded(prev => !prev)}
                        onDiagnostic={() => processLocalIntent("systems diagnostic")}
                      />
                    </Suspense>
                    {isSingularityExpanded && (
                      <motion.div initial={{ opacity: 0, scaleY: 0 }} animate={{ opacity: 1, scaleY: 1 }} className="rounded-sm border border-cyan-500/30 bg-black/80 p-4">
                        <SentienceEvolution />
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Right Interface Nodes */}
            <div className="absolute right-4 top-4 w-72 flex flex-col gap-3 items-end pointer-events-none">
              <div className="pointer-events-auto w-full"><TopMetrics status={status} onDiagnostic={() => processLocalIntent("systems diagnostic")} /></div>
              <div className="pointer-events-auto w-full stark-widget p-2 bg-black/40 border border-cyan-500/10"><WeatherWidget data={weatherData} /></div>
              <div className="pointer-events-auto w-full"><TacticalThreatScanner active={isInitialized} /></div>
              <div className="pointer-events-auto w-full"><CommandExecutionPanel actions={forgeLogs} /></div>
              
              <div className="pointer-events-auto w-full mt-4 stark-widget p-4 bg-black/40 border border-cyan-500/10">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[8px] text-cyan-400 font-black tracking-[0.3em] uppercase">NEURAL_LATENCY</span>
                  <div className="h-px bg-linear-to-r from-transparent via-cyan-500/20 to-transparent flex-1" />
                </div>
                <Suspense fallback={<div className="h-20 animate-pulse" />}><NetworkHeatmap /></Suspense>
              </div>
            </div>

            {/* Central Aura & Zenith Portal */}
            <div className="relative z-10 flex flex-col items-center justify-center p-24 w-full h-full">
              <AnimatePresence>
                {interimText && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 0.8, y: -40 }} className="absolute top-1/4 font-mono text-[11px] text-cyan-300 tracking-[0.6em] z-200">
                    {interimText}
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.div
                animate={{ scale: systemPulse ? 1.05 : 1, opacity: systemPulse ? 1 : 0.8 }}
                onClick={startVoice}
                className="relative z-200 pointer-events-auto cursor-pointer flex items-center justify-center w-[500px] h-[500px]"
              >
                <div className="absolute -inset-full opacity-20 scale-[1.5] pointer-events-none">
                  <AuraHUD 
                    isOnline={true} 
                    mode={mode} 
                    isIgniting={false} 
                    themeColor={themeColor} 
                    systemCoherence={systemCoherence} 
                  />
                </div>
                <Suspense fallback={null}>
                  <ZenithPortal
                    hudMode={hudMode}
                    status={status}
                    mode={mode}
                    themeColor={themeColor}
                    systemPulse={systemPulse}
                    focusValue={zenithFocus}
                    vitals={biometrics}
                    iotState={iotState}
                    showArmory={showArmory}
                    onClick={(e) => {
                      e.stopPropagation();
                      setHudMode(m => m === "CORE" ? "GLOBE" : "CORE");
                    }}
                  />
                </Suspense>
              </motion.div>

              <AnimatePresence>
                {assemblyStep >= 4 && (
                  <motion.div initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} className="fixed bottom-12 mx-auto w-[600px] z-300 pointer-events-auto">
                    <NeuralIntercept status={status} mode={mode} focusValue={zenithFocus} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-[600px] flex flex-col items-center gap-4 pointer-events-none z-400">
              <div className="pointer-events-auto w-full px-8"><NewsTicker news={newsData} /></div>
              <div className="pointer-events-auto"><NetworkPresence active={isInitialized} /></div>
            </div>

            <CommandFeed logs={logs} status={status} />
            <ForesightHUD predictions={foresightData} onAction={processLocalIntent} />

            <AnimatePresence>
              {showDiagnostic && <DiagnosticHUD data={diagnosticData} onComplete={() => setShowDiagnostic(false)} />}
              {showSettings && <SettingsHUD settings={settings} onUpdate={setSettings} onClose={() => setShowSettings(false)} onOSControl={handleOSControl} />}
              {showDominion && <DominionHUD onClose={() => setShowDominion(false)} onControl={handleDominionControl} />}
              {showResonance && <ResonanceHUD onClose={() => setShowResonance(false)} onOptimize={handleOptimize} />}
              {showMissionSpire && <MissionLabHUD tasks={taskData} onClose={() => setShowMissionSpire(false)} />}
            </AnimatePresence>

            <PerceptionHUD insight={visionInsight} />
            <PersonalityHUD status={status} mode={mode} />
            <NotificationCenter />

            <MolecularAssembly
              step={assemblyStep}
              onComplete={handleAssemblyComplete}
            />

            {/* Flash Overlay */}
            <AnimatePresence>
              {showFlash && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-1000 bg-white mix-blend-screen" />}
            </AnimatePresence>

          </main>
          <SatelliteMap location={geoData} />
        </div>
      )}

      <SovereignCanvas eventSource={containerRef} />
    </div>
    {cursorLayer}
    </>
  );
}
