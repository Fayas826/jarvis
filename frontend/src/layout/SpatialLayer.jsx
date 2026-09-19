import React, { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { View, Preload } from "@react-three/drei";
import { AnimatePresence, motion } from "framer-motion";
import { useAppState } from "@/core/contexts";
import ErrorBoundary from "@/features/core/ErrorBoundary";

import StarField from "@/features/simulations/Stars";
import ParallaxField from "@/features/simulations/ParallaxField";

// 🚀 HEAVY_MODULE_LAZY_LOADING
const SingularityNexus = React.lazy(() => import("@/features/simulations/SingularityNexus"));
const SingularityCanvas = React.lazy(() => import("@/features/simulations/SingularityCanvas"));
const SatelliteMap = React.lazy(() => import("@/features/simulations/SatelliteMap"));

// 🧊 STABLE_GL_CONFIG: Prevent renderer re-initialization on state changes
const GL_CONFIG = { 
  antialias: true, 
  alpha: true, 
  powerPreference: "high-performance",
  preserveDrawingBuffer: true 
};

// 🛡️ MEMOIZED_CANVAS: The Singleton WebGL Engine
export const SovereignCanvas = React.memo(({ eventSource }) => (
  <div className="fixed inset-0 z-10 pointer-events-none">
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

export default function SpatialLayer() {
  const {
    isSuitActive,
    isInitialized,
    mouseX,
    mouseY,
    showNexus,
    themeColor,
    isVisionActive,
    geoData,
    showStartup,
    isScanning
  } = useAppState();

  return (
    <>
      <StarField active={isSuitActive} />
      <AnimatePresence>
        {isInitialized && <ParallaxField mouseX={mouseX} mouseY={mouseY} />}
      </AnimatePresence>
      <div className="absolute inset-0 scanline-overlay z-501 pointer-events-none opacity-50" />
      <div className="absolute inset-0 tactical-grid opacity-25 pointer-events-none z-0" />

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
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-200 h-200 bg-cyan-500/5 rounded-full blur-[120px] animate-pulse z-2000">
              <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-cyan-400" />
              <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-cyan-400" />
              <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-cyan-400" />
              <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-cyan-400" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {!isInitialized && (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <Suspense fallback={null}>
            <ErrorBoundary>
              <SingularityCanvas highPerf={true} mode="initializing" />
            </ErrorBoundary>
          </Suspense>
        </div>
      )}

      {isInitialized && (
        <>
          <Suspense fallback={null}>
            <ErrorBoundary>
              <SingularityCanvas highPerf={true} mode="stable" />
            </ErrorBoundary>
          </Suspense>
          <SatelliteMap location={geoData} />
        </>
      )}
    </>
  );
}
