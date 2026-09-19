import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { View, Float, MeshDistortMaterial, Sphere } from "@react-three/drei";
import * as THREE from "three";

// 🌀 3D_KINETIC_CORE: AMBIENT ENERGY FIELD (NO BLOB)
const KineticCanvas = () => {
    return (
        <div className="absolute inset-0 z-0 pointer-events-none opacity-20">
            <View className="w-full h-full">
                <ambientLight intensity={0.3} color="#00f0ff" />
                <pointLight position={[0, 5, 5]} intensity={2} color="#00f0ff" />
                <pointLight position={[-5, -5, -5]} intensity={0.5} color="#0055ff" />
            </View>
        </div>
    );
};

export default function CinematicOverlay({ children, active = true }) {
  const containerRef = useRef(null);
  const [logs, setLogs] = useState([]);

  // 📝 PROTOCOL_LOG_GENERATOR (SIMULATED AUTHENTICATION)
  useEffect(() => {
    const protocols = [
        "ESTABLISHING_ENCRYPTED_QUANTUM_TUNNEL...",
        "VERIFYING_OMEGA_NEURAL_CERT...",
        "BYPASSING_LEGACY_FIREWALL_V6.2...",
        "RETRIEVING_BIOMETRIC_NEURAL_SIGNATURE...",
        "IDENTITY_CONFIRMED: MASTER_FAYAS",
        "ACCESS_GRANTED: LEVEL_OMEGA",
        "INITIALIZING_ZENITH_NEURAL_CORE..."
    ];
    let i = 0;
    const interval = setInterval(() => {
        if (i < protocols.length) {
            setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${protocols[i]}`].slice(-10));
            i++;
        }
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div ref={containerRef} className="absolute inset-0 overflow-hidden pointer-events-auto z-10 bg-black">
      {/* 🔮 WEBGL_LAYER */}
      {active && <KineticCanvas />}

      {/* 🎞️ FILM_GRAIN_TEXTURE */}
      <div className="absolute inset-0 opacity-[0.05] pointer-events-none mix-blend-overlay animate-grain bg-[url('/assets/images/noise.svg')]" />
      
      {/* 🌫️ CINEMATIC_VIGNETTE */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_transparent_0%,_rgba(0,0,0,0.6)_100%)]" />
      
      {/* 💡 AMBIENT_ENERGY_LEAKS */}
      <motion.div 
        animate={{ opacity: [0.1, 0.3, 0.1], scale: [1, 1.2, 1] }}
        transition={{ duration: 8, repeat: Infinity }}
        className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-600/10 blur-[150px] rounded-full"
      />

      {/* 📋 TERMINAL_PROTOCOL_LOGS (LEFT_ALIGNED) */}
      <div className="absolute top-1/2 -translate-y-1/2 left-12 flex flex-col gap-2 z-20 pointer-events-none">
          {logs.map((log, i) => (
              <motion.div 
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1 - (logs.length - i) * 0.1, x: 0 }}
                  className="font-mono text-[7px] text-cyan-400/60 tracking-widest uppercase"
              >
                  {log}
              </motion.div>
          ))}
      </div>

      {/* 💎 LUXURY_HEADER: O.M.E.G.A. AUTH — pushed below the sidebar toggle */}
      <div className="absolute top-20 left-12 flex flex-col gap-1 pointer-events-none z-30">
        <div className="flex items-center gap-3">
          <div className="w-8 h-[1px] bg-cyan-400/40" />
          <span className="font-mono text-[10px] text-cyan-400/60 tracking-[0.6em] uppercase">QUANTUM_AUTH_v20.0</span>
        </div>
        <motion.h1 
            initial={{ letterSpacing: "1em", opacity: 0 }}
            animate={{ letterSpacing: "0.3em", opacity: 1 }}
            transition={{ duration: 1.5 }}
            className="font-mono text-[18px] text-white font-black uppercase drop-shadow-[0_0_20px_rgba(0,240,255,0.5)]"
        >
          O.M.E.G.A. NEURAL CORE
        </motion.h1>
        <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="font-mono text-[9px] text-cyan-400/50 uppercase tracking-[0.4em] mt-0.5"
        >
          Omniscient Multi-Engine General Architecture
        </motion.p>
        <div className="flex justify-between items-center mt-2 px-1">
           <span className="text-[8px] text-cyan-500/40 uppercase tracking-[0.4em]">Neural ID: Master_Fayas // OMEGA_TIER</span>
           <div className="flex gap-1.5">
              {[1,2,3,4].map(i => (
                <motion.div 
                    key={i}
                    animate={{ opacity: [0.2, 1, 0.2], scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                    className="w-1.5 h-1.5 bg-cyan-400 shadow-[0_0_10px_cyan] rounded-full" 
                />
              ))}
           </div>
        </div>
      </div>

      {children}
    </div>
  );
}
