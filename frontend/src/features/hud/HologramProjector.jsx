import React, { useMemo } from "react";
import { motion } from "framer-motion";

const seededValue = (index, seed = 71) => {
  const value = Math.sin(index * 101.59 + seed) * 10000;
  return value - Math.floor(value);
};

export default function HologramProjector({ active = false, mood = 'STARK', isStabilized = false }) {
  const accentColor = mood === 'ENERGETIC' ? 'rgba(255, 185, 0, 0.8)' : 'rgba(255, 120, 0, 0.6)';
  const auraDust = useMemo(() => {
    return Array.from({ length: 30 }, (_, i) => ({
      id: i,
      duration: 4 + seededValue(i, 3) * 6,
      delay: seededValue(i, 7) * 5,
      left: `${seededValue(i, 11) * 100}%`,
      top: `${seededValue(i, 13) * 100}%`,
    }));
  }, []);

  if (!active) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-[50] pointer-events-none perspective-[2000px]">
      
      {/* 🔮 O.M.E.G.A. ZENITH: THE HOLOGRAPHIC CORE */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ 
            opacity: 1, 
            scale: isStabilized ? 1.05 : 1,
            filter: isStabilized ? 'brightness(1.4) contrast(1.1)' : 'brightness(1)'
        }}
        exit={{ opacity: 0, scale: 1.5 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
        className="relative w-[600px] h-[600px] flex items-center justify-center transform-style-3d"
      >
        {/* 🚀 Central Zenith Singularity */}
        <motion.div 
            animate={{ 
                rotateY: 360,
                scale: [1, 1.1, 1]
            }}
            transition={{ 
                rotateY: { duration: 20, repeat: Infinity, ease: "linear" },
                scale: { duration: 4, repeat: Infinity, ease: "easeInOut" }
            }}
            className="absolute w-32 h-32 rounded-full border border-cyan-400 shadow-[0_0_100px_rgba(0,240,255,0.4)]"
            style={{ 
                background: `radial-gradient(circle, ${accentColor} 0%, transparent 70%)`,
                backdropFilter: 'blur(20px)' 
            }}
        />

        {/* 🚀 Volumetric Light Beams (Prism-Shift) */}
        {[0, 45, 90, 135].map((deg) => (
            <motion.div
                key={deg}
                animate={{ 
                    rotateZ: deg + 360,
                    opacity: [0.1, 0.3, 0.1]
                }}
                transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
                className="absolute w-[800px] h-[1px] bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent"
                style={{ transform: `rotateZ(${deg}deg)` }}
            />
        ))}

        {/* 🚀 Rotating Zenith Shells */}
        {[1, 2, 3].map((i) => (
            <motion.div
                key={i}
                animate={{ 
                    rotateY: i % 2 === 0 ? 360 : -360,
                    rotateX: [10, 30, 10]
                }}
                transition={{ 
                    rotateY: { duration: 20 + i * 10, repeat: Infinity, ease: "linear" },
                    rotateX: { duration: 5, repeat: Infinity, ease: "easeInOut" }
                }}
                className={`absolute rounded-full border border-cyan-500/10 shadow-[0_0_30px_rgba(0,240,255,0.05)]`}
                style={{
                    width: `${300 + i * 100}px`,
                    height: `${300 + i * 100}px`,
                    backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(0,240,255,0.02) 0%, transparent 80%)',
                    transformStyle: 'preserve-3d'
                }}
            />
        ))}

        {/* ✨ Digital Aura Dust */}
        {auraDust.map((particle) => (
            <motion.div
                key={particle.id}
                animate={{
                    y: [0, -100, 0],
                    opacity: [0, 0.6, 0]
                }}
                transition={{
                    duration: particle.duration,
                    repeat: Infinity,
                    delay: particle.delay
                }}
                className="absolute w-0.5 h-0.5 bg-cyan-400 rounded-full blur-[0.5px]"
                style={{
                    left: particle.left,
                    top: particle.top
                }}
            />
        ))}

        {/* ⚠️ Kinetic Flicker */}
        <div className="absolute inset-0 bg-cyan-500/5 animate-flicker pointer-events-none mix-blend-overlay opacity-20" />
      </motion.div>
    </div>
  );
}
