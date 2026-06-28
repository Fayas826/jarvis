import React, { useState, useEffect, useRef, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useFrame } from "@react-three/fiber";
import { View, Points, PointMaterial } from "@react-three/drei";
import * as THREE from "three";
import suits from "@/features/simulations/suitData.json";
const Globe = React.lazy(() => import("../../features/simulations/Globe"));

const seededValue = (index, seed = 31) => {
  const value = Math.sin(index * 67.17 + seed) * 10000;
  return value - Math.floor(value);
};

const circleCanvas = document.createElement("canvas");
circleCanvas.width = 32;
circleCanvas.height = 32;
const circleCtx = circleCanvas.getContext("2d");
const circleGradient = circleCtx.createRadialGradient(16, 16, 0, 16, 16, 16);
circleGradient.addColorStop(0, "rgba(255,255,255,1)");
circleGradient.addColorStop(1, "rgba(255,255,255,0)");
circleCtx.fillStyle = circleGradient;
circleCtx.beginPath();
circleCtx.arc(16, 16, 16, 0, 2 * Math.PI);
circleCtx.fill();
const globalCircleTexture = new THREE.CanvasTexture(circleCanvas);

// 🌀 3D NANO-SWARM (MK_LXXXV EXCLUSIVE)
const NanoSwarm = ({ activeColor }) => {
  const pointsRef = useRef();

  const [positions] = useMemo(() => {
    const count = 800;
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
       const r = 2.0;
       const theta = 2 * Math.PI * seededValue(i, 5);
       const phi = Math.acos(2 * seededValue(i, 9) - 1);
       pos[i*3] = r * Math.sin(phi) * Math.cos(theta);
       pos[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
       pos[i*3+2] = r * Math.cos(phi);
    }
    return [pos];
  }, []);

  useFrame(() => {
    if (!pointsRef.current) return;
    
    const t = performance.now() / 1000;
    pointsRef.current.rotation.y = t * 1.5;
    pointsRef.current.rotation.x = Math.sin(t * 2) * 0.5;
    // Pulsate Nano Cloud
    const pulse = 1 + Math.sin(t * 8) * 0.1;
    pointsRef.current.scale.set(pulse, pulse, pulse);
  });

  return (
    <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial transparent color={activeColor} size={0.08} depthWrite={false} blending={THREE.AdditiveBlending} map={globalCircleTexture} />
    </Points>
  );
};

// 🧊 3D HOLOGRAPHIC SUIT PROJECTIONS
const SuitHologram = ({ suitId, isEvolving, activeColor }) => {
    const meshRef = useRef();
    
    useFrame(() => {
        if (!meshRef.current) return;
        
        const t = performance.now() / 1000;
        meshRef.current.rotation.y += 0.03;
        meshRef.current.rotation.x = Math.sin(t) * 0.1;
        
        // Evolving Glitch Effect
        if (isEvolving) {
            meshRef.current.scale.setScalar(1 + (Math.random() * 0.2));
            meshRef.current.rotation.z += (Math.random() - 0.5) * 0.1;
        } else {
            meshRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1);
        }
    });

    const matProps = {
        color: activeColor,
        wireframe: true,
        transparent: true,
        opacity: isEvolving ? 0.1 : 0.8,
        blending: THREE.AdditiveBlending
    };

    switch(suitId) {
        case "MK_LXXXV":
            return (
                <group ref={meshRef}>
                    <mesh>
                        <icosahedronGeometry args={[1.5, 1]} />
                        <meshBasicMaterial {...matProps} />
                    </mesh>
                    <mesh>
                        <icosahedronGeometry args={[0.8, 0]} />
                        <meshBasicMaterial {...matProps} opacity={0.5} />
                    </mesh>
                    <NanoSwarm activeColor={activeColor} />
                </group>
            );
        case "MK_III":
             return <mesh ref={meshRef}><cylinderGeometry args={[0.8, 1.2, 2.5, 6]} /><meshBasicMaterial {...matProps} /></mesh>;
        case "MK_VII":
             return <mesh ref={meshRef}><octahedronGeometry args={[1.5, 0]} /><meshBasicMaterial {...matProps} /></mesh>;
        case "MK_XLII":
             return <mesh ref={meshRef}><torusKnotGeometry args={[0.9, 0.2, 64, 8]} /><meshBasicMaterial {...matProps} /></mesh>;
        case "MK_I":
             return <mesh ref={meshRef}><boxGeometry args={[1.6, 2.2, 1.6]} /><meshBasicMaterial {...matProps} color="#888" /></mesh>;
        default:
             return <mesh ref={meshRef}><sphereGeometry args={[1, 16, 16]} /><meshBasicMaterial {...matProps} /></mesh>;
    }
};

export default function Armory({ status, systemPulse, themeColor, vitals, onDiagnostic, isExpanded, onToggleSentience }) {
  const [index, setIndex] = useState(0);
  const [isEvolving, setIsEvolving] = useState(false);
  const suit = suits[index];
  
  // 🌈 Neural Color Sync Integration
  const activeColor = status === "thinking" || status === "speaking" ? "#ffb900" : themeColor;

  useEffect(() => {
    const startTimer = setTimeout(() => setIsEvolving(true), 0);
    const stopTimer = setTimeout(() => setIsEvolving(false), 600);
    return () => {
      clearTimeout(startTimer);
      clearTimeout(stopTimer);
    };
  }, [index]);

  const next = () => setIndex((index + 1) % suits.length);
  const prev = () => setIndex((index - 1 + suits.length) % suits.length);

  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="armory-panel w-full p-2 border border-cyan-500/30 bg-black/60 shadow-[0_0_30px_rgba(0,240,255,0.1)] backdrop-blur-xl rounded-sm font-mono uppercase overflow-hidden"
    >
      {/* HEADER */}
      <div className="flex justify-between items-center mb-2 border-b border-cyan-500/40 pb-1">
        <span className="text-[10px] text-cyan-300 font-black tracking-[0.5em] drop-shadow-[0_0_5px_cyan]">DIGITAL_ARMORY_v9.0</span>
        <div className="flex gap-4">
            <button 
                onClick={() => onDiagnostic && onDiagnostic()} 
                className="text-[8px] text-cyan-400 bg-cyan-500/10 hover:bg-cyan-500/30 transition-colors pointer-events-auto border border-cyan-500/40 px-2 py-0.5 rounded-sm"
            >
                DIAGNOSTIC
            </button>
            <div className="flex gap-2">
                <button onClick={prev} className="hover:text-white text-cyan-500 transition-colors pointer-events-auto text-[12px] font-bold">{"<"}</button>
                <button onClick={next} className="hover:text-white text-cyan-500 transition-colors pointer-events-auto text-[12px] font-bold">{">"}</button>
            </div>
        </div>
      </div>

      {/* 🔮 3D ZENITH PROJECTION STAGE */}
      <div className="relative h-[150px] w-full flex items-center justify-center overflow-hidden mx-auto border border-cyan-500/20 bg-[rgba(var(--stark-glow-rgb),0.02)] rounded-[2px] shadow-[inset_0_0_40px_rgba(0,0,0,0.8)]">
         
         {/* LAYER 0: BASE GLOBE */}
         <div className="absolute inset-0 z-0 pointer-events-none flex items-center justify-center opacity-40">
             <React.Suspense fallback={<div className="text-[10px] text-cyan-500 font-mono">LOADING NAV...</div>}>
                 <Globe isOnline={true} status={status} systemPulse={systemPulse} themeColor={themeColor} vitals={vitals} minimal={true} />
             </React.Suspense>
         </div>

         {/* LAYER 1: WEBGL CANVAS */}
         <div className="absolute inset-0 z-10 pointer-events-none">
             <View className="w-full h-full">
                 <SuitHologram suitId={suit.id} isEvolving={isEvolving} activeColor={activeColor} />
             </View>
         </div>

         {/* LAYER 2: ZENITH NAV ACTIVE RINGS */}
         <div className="absolute z-20 pointer-events-none flex items-center justify-center top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
             <motion.div 
                 animate={{ rotateZ: -360 }}
                 transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                 className="relative border border-solid rounded-full flex items-center justify-center"
                 style={{ width: '120px', height: '120px', borderColor: activeColor, boxShadow: `0 0 15px ${activeColor}30` }}
             >
                 {/* ZENITH NAV LABEL */}
                 <div className="absolute top-[-4px] left-1/2 -translate-x-1/2 bg-black px-2 py-px text-[6px] text-white font-black tracking-[0.4em] whitespace-nowrap drop-shadow-[0_0_5px_cyan]">
                     ZENITH_NAV_ACTIVE
                 </div>
                 <div className="absolute bottom-[-4px] left-1/2 -translate-x-1/2 bg-black px-2 py-px text-[6px] font-bold tracking-[0.2em] whitespace-nowrap" style={{ color: activeColor }}>
                     LINK_SECURE
                 </div>
                 
                 {/* Outer Tech Ring */}
                 <motion.div 
                     animate={{ rotate: 360 }}
                     transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                     className="absolute w-[140px] h-[140px] border-t-2 border-r-2 border-transparent rounded-full"
                     style={{ borderTopColor: activeColor }}
                 />
                 
                 {/* Inner Pulse Ring */}
                 <motion.div 
                    animate={{ scale: [1, 1.1, 1], opacity: [0.3, 0.8, 0.3] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="w-[100px] h-[100px] border rounded-full backdrop-blur-[2px]"
                    style={{ borderColor: activeColor }}
                 />
             </motion.div>
         </div>

         {/* SWEEP BAR */}
         <AnimatePresence>
            {isEvolving && (
               <motion.div 
                  initial={{ top: "-10%" }}
                  animate={{ top: "110%" }}
                  transition={{ duration: 0.6, ease: "linear" }}
                  className="absolute left-0 right-0 h-2 z-30 bg-white shadow-[0_0_20px_rgba(255,255,255,1)] opacity-90"
               />
            )}
         </AnimatePresence>
      </div>

      {/* METRICS */}
      <div className="mt-4 flex flex-col gap-2">
         <div className="flex justify-between items-center px-2 bg-[rgba(var(--stark-glow-rgb),0.1)] py-1 border border-cyan-500/20" style={{ borderColor: activeColor, backgroundColor: `${activeColor}1A` }}>
            <span className="text-[14px] font-black text-white tracking-[0.3em] drop-shadow-[0_0_5px_cyan]">{suit.name}</span>
            <span className="text-[9px] font-bold text-cyan-400 tracking-[0.2em] bg-black px-2 py-0.5 border" style={{ color: activeColor, borderColor: `${activeColor}80` }}>PROT_ID: {suit.id}</span>
         </div>
         
         <p className="text-[8px] leading-relaxed tracking-widest h-12 overflow-hidden px-1 border-l-2 mt-1 pl-2 text-white/70" style={{ borderLeftColor: activeColor }}>
            {suit.description}
         </p>

         {/* 🎯 ULTIMATE ZENITH METRICS BLOCK (ZENITH_FINAL_EVOLUTION) */}
         <div className="flex gap-4 mt-3 px-2 relative items-center">
             
             {/* 🧿 THE_INTEGRITY_HUB (ZENITH_FINAL_EVOLUTION) */}
             <div 
                 className="relative w-16 h-16 flex items-center justify-center cursor-pointer group pointer-events-auto"
                 onClick={onToggleSentience}
             >
                 {/* 🌌 VOLUMETRIC_DEPTH_GLOW */}
                 <div className="absolute inset-0 bg-cyan-500/5 rounded-full blur-xl group-hover:bg-cyan-500/10 transition-colors" />
                 
                 {/* 🌀 OUTER_TACTICAL_RINGS */}
                 <motion.div 
                     animate={{ rotate: 360 }}
                     transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                     className="absolute inset-[-4px] border border-cyan-500/20 rounded-full border-dashed"
                     style={{ borderColor: `${activeColor}40` }}
                 />
                 
                 {/* 🛡️ REINFORCED_CONTAINMENT_FIELD */}
                 <div className="absolute inset-0 border border-white/5 bg-black/40 backdrop-blur-md rounded-full shadow-[inset_0_0_20px_rgba(255,255,255,0.05)]" />
                 
                 {/* 🩸 RESONANCE_CORE */}
                 <motion.div 
                     animate={{ 
                         scale: isExpanded ? [1, 1.15, 1] : [1, 1.05, 1],
                         opacity: isExpanded ? 1 : 0.8
                     }}
                     transition={{ duration: isExpanded ? 1 : 4, repeat: Infinity }}
                     className="absolute inset-1.5 rounded-full flex items-center justify-center overflow-hidden"
                     style={{ 
                         background: isExpanded 
                           ? `radial-gradient(circle, ${activeColor} 0%, #9333ea 70%, #000 100%)` 
                           : `radial-gradient(circle, ${activeColor} 0%, #4338ca 70%, #000 100%)` 
                     }}
                 >
                     <div className="absolute inset-0 bg-white/10 mix-blend-overlay animate-pulse" />
                     <span className="text-white font-black text-[12px] tracking-tighter drop-shadow-[0_0_5px_white]">
                         {suit.specs.integrity || "100%"}
                     </span>
                 </motion.div>
                 
                 {/* 🟢 SENTIENT_GATE_STATUS */}
                 <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-black transition-all duration-500 ${isExpanded ? 'bg-purple-500 shadow-[0_0_10px_#9333ea]' : 'bg-green-500 shadow-[0_0_10px_#22c55e]'}`} />
                 
                 <span className="absolute -bottom-5 text-[6px] text-white/40 font-black tracking-[0.3em] uppercase whitespace-nowrap group-hover:text-white transition-colors">INTEGRITY_HUB</span>
             </div>

             {/* Right side stats box */}
             <div className="flex-1 flex flex-col gap-2 bg-black/80 border border-cyan-500/20 p-2.5 relative shadow-[0_4px_20px_rgba(0,0,0,0.5),inset_0_0_15px_rgba(255,255,255,0.05)] backdrop-blur-md pointer-events-auto min-h-[50px] justify-between" style={{ borderColor: `${activeColor}40` }}>
                  {/* Subtle inner top glow for the box */}
                  <div className="absolute top-0 left-1/4 right-1/4 h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent" />
                  
                  <div className="text-[12px] font-mono tracking-tight z-10 relative flex flex-col items-start leading-[1.1]">
                      <span className="text-white/50 text-[7px] font-black uppercase tracking-[0.4em] drop-shadow-[0_0_5px_rgba(255,255,255,0.2)]">REFLECTING</span> 
                      <div className="flex items-center gap-2">
                          <span className="text-white/40 text-[7px] font-bold italic">ON:</span>
                          <span className="text-white font-black tracking-[0.25em] drop-shadow-[0_0_12px_rgba(255,255,255,0.9)] text-[10px]">NEURAL_REASONING</span>
                      </div>
                  </div>
                  <div className="flex justify-between items-end relative z-10 pt-1">
                      <div className="flex flex-col">
                          <span className="text-[13px] text-white font-black font-mono drop-shadow-[0_0_8px_cyan]">{suit.specs.power || "100%"}</span>
                      </div>
                      <div className="flex flex-col text-right">
                          <span className="text-[11px] text-white font-bold tracking-widest uppercase drop-shadow-[0_0_4px_cyan]">{suit.specs.weapons || "NANO_FORGE"}</span>
                      </div>
                  </div>
             </div>
         </div>
         <div className="h-4" /> {/* Bot padding */}
      </div>
    </motion.div>
  );
}
