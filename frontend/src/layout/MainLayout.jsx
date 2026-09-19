import React, { Suspense } from "react";
import { createPortal } from "react-dom";
import { api } from "@/services/api";
import { motion, AnimatePresence } from "framer-motion";

import ErrorBoundary from "@/features/core/ErrorBoundary";
import StartupLogo from "@/features/core/StartupLogo";
import ForgeHandshake from "@/features/core/ForgeHandshake";
import CinematicOverlay from "@/features/hud/CinematicOverlay";
import ManualChatInput from "@/features/hud/ManualChatInput";
import MolecularAssembly from "@/features/hud/MolecularAssembly";
import DominionHUD from "@/features/hud/DominionHUD";
import DiagnosticHUD from "@/features/hud/DiagnosticHUD";
import SettingsHUD from "@/features/hud/SettingsHUD";
import ResonanceHUD from "@/features/hud/ResonanceHUD";
import NeuralIntercept from "@/features/hud/NeuralIntercept";
import MissionLabHUD from "@/features/hud/MissionLabHUD";
import ForesightHUD from "@/features/hud/ForesightHUD";
import NetworkPresence from "@/features/hud/NetworkPresence";
import PerceptionHUD from "@/features/hud/PerceptionHUD";
import PersonalityHUD from "@/features/hud/PersonalityHUD";
import NotificationCenter from "@/features/hud/NotificationCenter";
import LeftSidebar from "@/features/hud/LeftSidebar";
import CommandFeed from "@/features/hud/CommandFeed";
import NewsTicker from "@/features/hud/NewsTicker";
import AuraHUD from "@/features/hud/SystemCoherenceHUD";

import HUDLayer from "@/layout/HUDLayer";
import SpatialLayer, { SovereignCanvas } from "@/layout/SpatialLayer";
import { useAppState } from "@/core/contexts";

// 🚀 HEAVY_MODULE_LAZY_LOADING
const ZenithPortal = React.lazy(() => import("@/features/simulations/ZenithPortal"));
const FaceScanner = React.lazy(() => import("@/features/scanners/FaceScanner"));

export default function MainLayout() {
  const {
    mode,
    status,
    logs,
    isInitialized,
    biometrics,
    iotState,
    isScanning,
    showStartup,
    zenithFocus,
    visionInsight,
    newsData,
    taskData,
    diagnosticData,
    showFlash,
    showSettings,
    themeColor,
    showDiagnostic,
    settings,
    hudMode,
    showArmory,
    systemPulse,
    isIgniting,
    assemblyStep,
    activeForgeId,
    forgeLogs,
    proposedForge,
    showDominion,
    showResonance,
    showMissionSpire,
    foresightData,
    interimText,
    mouseX,
    mouseY,
    systemCoherence,
    initializeSystem,
    addLog,
    handleVerify,
    processLocalIntent,
    handleOSControl,
    handleOptimize,
    handleDominionControl,
    startVoice,
    handleLogoComplete,
    handleAssemblyComplete,
    setActiveForgeId,
    setForgeLogs,
    setProposedForge,
    setShowSettings,
    setShowDiagnostic,
    setSettings,
    setShowDominion,
    setShowResonance,
    setHudMode,
    setShowMissionSpire
  } = useAppState();

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
      <SpatialLayer />

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

      {!isInitialized ? (
        <div className="fixed inset-0 z-5 flex flex-col items-center justify-center bg-black overflow-hidden">
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
                      className="w-125 h-125 flex items-center justify-center cursor-pointer pointer-events-auto"
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
        <div className="fixed inset-0 z-5 bg-[#000508] overflow-hidden">
          <main className="h-screen w-screen relative z-10 overflow-hidden pointer-events-none flex flex-col items-center justify-center">
            
            <HUDLayer />

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
                className="relative z-200 pointer-events-auto cursor-pointer flex items-center justify-center w-125 h-125"
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
                  <motion.div initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} className="fixed bottom-12 mx-auto w-150 z-300 pointer-events-auto">
                    <NeuralIntercept status={status} mode={mode} focusValue={zenithFocus} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-150 flex flex-col items-center gap-4 pointer-events-none z-400">
              <div className="pointer-events-auto w-full px-8"><ManualChatInput onSubmit={processLocalIntent} /></div>
              <div className="pointer-events-auto w-full px-8"><NewsTicker news={newsData} /></div>
              <div className="pointer-events-auto"><NetworkPresence active={isInitialized} /></div>
            </div>

            <CommandFeed logs={logs} status={status} />
            <ForesightHUD predictions={foresightData} onAction={processLocalIntent} />

            <AnimatePresence>
              {showDiagnostic && <DiagnosticHUD data={diagnosticData} onComplete={() => setShowDiagnostic(false)} />}
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
        </div>
      )}

      <SovereignCanvas eventSource={containerRef} />
      <LeftSidebar onOpenSettings={() => setShowSettings(true)} />
      <AnimatePresence>
        {showSettings && <SettingsHUD settings={settings} onUpdate={setSettings} onClose={() => setShowSettings(false)} onOSControl={handleOSControl} />}
      </AnimatePresence>
    </div>
    {cursorLayer}
    </>
  );
}
