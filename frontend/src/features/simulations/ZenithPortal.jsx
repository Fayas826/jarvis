import React, { Suspense } from "react";
import { View } from "@react-three/drei";
import { motion } from "framer-motion";
import { ARButton, Interactive, createXRStore } from "@react-three/xr";
import { OrbitControls, Float } from "@react-three/drei";

import MemoryLattice from "@/features/simulations/MemoryLattice";
import HolographicUplink from "@/features/simulations/HolographicUplink";
import SuitLab3D from "@/features/simulations/SuitLab3D";
import ASICore from "@/features/simulations/ASICore";
import Tesseract4D, { DimensionOverlay } from "@/features/simulations/Tesseract4D";
import useSystemMetrics from "@/hooks/useSystemMetrics";

import { 
    InnerSingularity, 
    NeuralMist, 
    AdvancedStarkRings, 
    NeuralConstellation, 
    SpectralSurface 
} from "./PortalMeshes";
import { KineticCamera, ParallaxController } from "./PortalControllers";

// 🚀 O.M.E.G.A. TIER_15: XR_STORE_SINGLETON (v6 API)
const store = createXRStore();

export default function ZenithPortal({ status, mode, themeColor, onClick, focusValue, vitals, iotState, showArmory = false }) {
    const { cpuLoad, ramLoad, isLive } = useSystemMetrics();

    return (
        <div className="relative aspect-square w-full max-w-[90vh] flex items-center justify-center cursor-pointer select-none" onClick={onClick}>
            <div className="absolute inset-0 z-10">
                <View className="absolute inset-0">
                    <HolographicUplink vitals={vitals} iotState={iotState} />
                    {showArmory && (
                        <group position={[0, 0, 0]} scale={[1.5, 1.5, 1.5]}>
                            <SuitLab3D themeColor={themeColor} vitals={vitals} />
                        </group>
                    )}
                    <ambientLight intensity={0.5} />
                    <KineticCamera />
                    <ParallaxController />
                    <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.2}>
                        <group name="ParallaxLayer">
                            <NeuralConstellation focusValue={focusValue} />
                            {/* <SpectralSurface themeColor={themeColor} focusValue={focusValue} /> */}
                            <Tesseract4D themeColor={themeColor} cpuLoad={cpuLoad} ramLoad={ramLoad} />
                            <ASICore themeColor={themeColor} />
                            <AdvancedStarkRings themeColor={themeColor} focusValue={focusValue} />
                            <NeuralMist />
                            <MemoryLattice status={status} mode={mode} />
                        </group>
                    </Float>
                    <OrbitControls enableZoom={false} enablePan={false} makeDefault />
                    
                    {/* 🔘 O.M.E.G.A. TIER_14: XR_AR_ENTRY_NODE */}
                    <Float speed={1} rotationIntensity={0} floatIntensity={0}>
                        <Interactive onSelect={() => console.log("XR_SESSION_START")}>
                            <mesh position={[3, 2, -2]} onClick={() => console.log("FORCE_AR")}>
                                <planeGeometry args={[1, 0.4]} />
                                <meshBasicMaterial color="#00f0ff" transparent opacity={0.1} />
                            </mesh>
                        </Interactive>
                    </Float>
                </View>
            </div>

            <div className="absolute top-10 right-10 z-200 pointer-events-auto">
                <ARButton store={store} className="holographic-btn" />
            </div>

            <div className="absolute inset-0 flex items-center justify-center z-50 pointer-events-none">
                <motion.div 
                    animate={{ scale: 0.85 + focusValue * 0.1 }}
                    className="flex flex-col items-center justify-center"
                >
                    <span className="font-mono text-[14px] font-black tracking-[1.2em] text-white/95 drop-shadow-[0_0_20px_rgba(255,255,255,0.6)]">
                        JARVIS
                        {focusValue > 0.5 && <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ duration: 0.2, repeat: Infinity }} className="absolute -right-6 top-0 text-[10px] text-cyan-400 font-bold">!!</motion.span>}
                    </span>
                    
                    <div className="flex gap-2 items-center mt-2 opacity-50">
                        <div className="w-10 h-px bg-white shadow-[0_0_5px_white]" />
                        <div className="w-4 h-px bg-cyan-400 shadow-[0_0_5px_cyan]" />
                        <div className="w-10 h-px bg-white shadow-[0_0_5px_white]" />
                    </div>

                    {/* 5D status indicator */}
                    <div className="mt-3 flex items-center gap-2">
                        <div className={`w-1.5 h-1.5 rounded-full ${isLive ? 'bg-green-400 shadow-[0_0_5px_lime]' : 'bg-yellow-400 shadow-[0_0_5px_yellow]'}`} />
                        <span className="font-mono text-[8px] text-white/30 tracking-widest">
                            {isLive ? 'LIVE·5D' : 'SIM·5D'}
                        </span>
                    </div>
                </motion.div>
            </div>

            <DimensionOverlay cpuLoad={cpuLoad} ramLoad={ramLoad} />
        </div>
    );
}
