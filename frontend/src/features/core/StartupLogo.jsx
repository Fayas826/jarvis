import React, { useState, useEffect, useMemo, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useFrame } from "@react-three/fiber";
import { View } from "@react-three/drei";
import * as THREE from "three";

const seededValue = (index, seed = 23) => {
    const value = Math.sin(index * 43.13 + seed) * 10000;
    return value - Math.floor(value);
};

// 🌀 O.M.E.G.A. XVIII: QUANTUM_VORTEX (WebGL Engine)
const QuantumField = ({ progress }) => {
    const pointsRef = useRef();
    const count = 2000;
    
    const positions = useMemo(() => {
        const p = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            p[i * 3] = (seededValue(i, 3) - 0.5) * 10;
            p[i * 3 + 1] = (seededValue(i, 7) - 0.5) * 10;
            p[i * 3 + 2] = (seededValue(i, 11) - 0.5) * 10;
        }
        return p;
    }, []);

    useFrame(() => {
        if (!pointsRef.current) return;
        
        const t = performance.now() / 1000;
        pointsRef.current.rotation.y = t * 0.1;
        pointsRef.current.rotation.z = t * 0.05;
        const scale = 1 + (progress / 100) * 0.5;
        pointsRef.current.scale.set(scale, scale, scale);
    });

    return (
        <points ref={pointsRef}>
            <bufferGeometry>
                <bufferAttribute
                    attach="attributes-position"
                    count={count}
                    array={positions}
                    itemSize={3}
                />
            </bufferGeometry>
            <pointsMaterial 
                size={0.05} 
                color="#00f0ff" 
                transparent 
                opacity={0.4} 
                blending={THREE.AdditiveBlending}
                sizeAttenuation={true}
            />
        </points>
    );
};

export default function StartupLogo({ onComplete }) {
  const [ignited, setIgnited] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const [renderCanvas, setRenderCanvas] = useState(true);

  useEffect(() => {
    // 🧬 O.M.E.G.A. XVIII: TRANSCENDENCE IGNITION TIMING
    const ignitionTimer = setTimeout(() => setIgnited(true), 800);
    const completeTimer = setTimeout(() => onComplete(), 5500); // 5.5s for Cinematic Pacing
    let canvasCleanupTimer;
    
    // 📊 PROGRESS_FLUX
    const progressInterval = setInterval(() => {
        setProgress(prev => {
            if (prev >= 100) {
                // 🛡️ O.M.E.G.A. STABILITY: Early cleanup for imminent context switch
                if (!canvasCleanupTimer) {
                    canvasCleanupTimer = setTimeout(() => setRenderCanvas(false), 200);
                }
                return 100;
            }
            const increment = Math.random() * 4; // Smoother, cinematic ramp
            return Math.min(prev + increment, 100);
        });
    }, 100);

    // 📜 KERNEL_LOG_DRIP
    const logPool = [
        "INITIALIZING_O.M.E.G.A_CORE...",
        "DECRYPTING_NEURAL_NODES...",
        "UPLINKING_SATELLITE_ARRAYS...",
        "MOORING_USER_SIGNATURE...",
        "STABILIZING_QUANTUM_LATTICE...",
        "IGNITING_AURA_PROTOCOLS...",
        "TRANSCENDENCE_READY."
    ];
    let logIdx = 0;
    const logInterval = setInterval(() => {
        if (logIdx < logPool.length) {
            setLogs(prev => [...prev, `> ${logPool[logIdx]}`]);
            logIdx++;
        }
    }, 700);

    return () => {
        clearTimeout(ignitionTimer);
        clearTimeout(completeTimer);
        clearTimeout(canvasCleanupTimer);
        clearInterval(progressInterval);
        clearInterval(logInterval);
    };
  }, [onComplete]);

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 1.2, filter: 'brightness(2) blur(20px)' }}
      className="fixed inset-0 z-[1000] bg-black flex flex-col items-center justify-center overflow-hidden"
    >
      {/* 🌌 O.M.E.G.A. XVIII: ULTIMATE_QUANTUM_FIELD */}
      <div className="absolute inset-0 z-0">
          {renderCanvas && (
               <View className="absolute inset-0 z-0">
                   <color attach="background" args={["#000"]} />
                   <QuantumField progress={progress} />
               </View>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black opacity-60" />
      </div>

      {/* 🚀 O.M.E.G.A. XVIII: SPATIOTEMPORAL SHOCKWAVES */}
      {ignited && (
          <div className="absolute inset-0 flex items-center justify-center">
              {Array.from({ length: 4 }).map((_, i) => (
                    <motion.div 
                        key={i}
                        initial={{ scale: 0, opacity: 0.6 }}
                        animate={{ scale: 6, opacity: 0 }}
                        transition={{ duration: 2.5, delay: i * 0.6, repeat: Infinity }}
                        className="absolute w-[300px] h-[300px] border border-amber-500/20 rounded-full blur-[4px]"
                    />
              ))}
          </div>
      )}

      {/* 🚀 Logo & Loading Flux */}
      <div className="relative z-10 flex flex-col items-center gap-14">
        <motion.div
            animate={{ 
                scale: [1, 1.02, 1],
                filter: ignited ? ["hue-rotate(0deg)", "hue-rotate(10deg)", "hue-rotate(0deg)"] : "none"
            }}
            transition={{ duration: 3, repeat: Infinity }}
            className="flex flex-col items-center"
        >
            <motion.svg 
                initial={{ scale: 0.8, opacity: 0, filter: 'blur(20px)' }}
                animate={{ 
                    scale: ignited ? 1 : 0.8, 
                    opacity: ignited ? 1 : 0,
                    filter: ignited ? 'blur(0.01px)' : 'blur(20px)'
                }}
                transition={{ duration: 1.2, ease: "easeOut" }}
                viewBox="0 0 400 100" 
                className="w-[500px] h-auto drop-shadow-[0_0_80px_rgba(255,185,0,0.5)]"
            >
                <defs>
                    <linearGradient id="zenith-ignite" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style={{ stopColor: '#00f0ff', stopOpacity: 1 }} />
                        <stop offset="50%" style={{ stopColor: '#ffb900', stopOpacity: 1 }} />
                        <stop offset="100%" style={{ stopColor: '#ff0000', stopOpacity: 1 }} />
                    </linearGradient>
                </defs>

                <motion.path 
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 4, ease: "easeInOut", delay: 1 }}
                    d="M20 70 L50 20 L80 70 M50 20 L50 70 M100 20 L100 70 L130 70 M150 70 L180 20 L210 70 M180 20 L180 70 M230 20 L230 70 L260 70 L260 45 L245 45 M280 20 L310 70 L340 20"
                    fill="none" 
                    stroke="url(#zenith-ignite)" 
                    strokeWidth="4"
                    strokeLinecap="round"
                    className="drop-shadow-[0_0_30px_cyan]"
                />
                
                <motion.text 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 4 }}
                    x="110" y="90" fontSize="12" fontWeight="900" fill="#ffb900" 
                    className="font-mono tracking-[1.4em] font-black drop-shadow-[0_0_20px_orange]"
                >
                    INDUSTRIES
                </motion.text>
            </motion.svg>
        </motion.div>

        {/* 🛠️ Loading Infrastructure */}
        <div className="w-[350px] flex flex-col gap-4">
             <div className="flex justify-between items-end">
                <div className="flex flex-col gap-1">
                    <span className="text-[7px] font-black font-mono text-cyan-400 uppercase tracking-widest">Aura_Ignition_Protocol</span>
                    <span className="text-[10px] font-mono text-white/40 tracking-[0.4em] uppercase">TRANSCENDENCE</span>
                </div>
                <span className="text-[16px] font-mono text-amber-500 font-bold">{Math.floor(progress)}%</span>
             </div>
             <div className="w-full h-[2px] bg-white/5 relative overflow-hidden">
                <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    className="h-full bg-gradient-to-r from-cyan-400 via-amber-400 to-red-600 shadow-[0_0_15px_rgba(255,185,0,0.8)]"
                />
                {/* ⚡ High-speed scan flash */}
                <motion.div 
                    animate={{ x: ["-100%", "200%"] }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-0 w-1/2 bg-gradient-to-r from-transparent via-white/40 to-transparent"
                />
             </div>
        </div>
      </div>

      {/* 📜 O.M.E.G.A. XVIII: TACTICAL_BOOT_INTERIM */}
      <div className="absolute left-10 bottom-10 flex flex-col gap-1">
          {logs.slice(-4).map((log, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: (i + 1) / 4, x: 0 }}
                className="font-mono text-[8px] text-cyan-500 tracking-widest uppercase"
              >
                  {log}
              </motion.div>
          ))}
      </div>

      {/* 📐 Stark Industries HUD Anchors */}
      <div className="absolute top-12 left-12 flex flex-col gap-2 font-mono text-[8px] text-white/20 tracking-[0.6em] uppercase">
         <div>NODE: ZENITH_PRIME</div>
         <div>REGION: {new Intl.DateTimeFormat('en-US', { month: 'short', day: '2-digit' }).format(new Date())}_SECTOR</div>
      </div>

      <div className="absolute bottom-12 right-12 flex items-center gap-4">
          <div className="flex flex-col items-end gap-1">
              <span className="text-[7px] font-mono text-white/40 tracking-widest uppercase">System_State</span>
              <span className="text-[9px] font-black font-mono text-amber-500 uppercase tracking-[0.4em]">Absolute_Transcendence</span>
          </div>
          <div className="w-8 h-8 border border-white/10 flex items-center justify-center p-1">
              <div className="w-full h-full bg-amber-500/20 animate-pulse" />
          </div>
      </div>
    </motion.div>
  );
}
