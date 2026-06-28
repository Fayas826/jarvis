import React from "react";
import { motion } from "framer-motion";

export default function SingularityCanvas({ highPerf = false, mode = "initializing" }) {
  // 🚀 O.M.E.G.A. XIV: SMOOTHNESS PROTOCOL (LOD SYSTEM)
  const layers = highPerf ? [1, 2, 3] : [1];
  const gridOpacity = mode === "initializing" ? 0.03 : 0.015;

  return (
    <div className="fixed inset-0 pointer-events-none z-[-1] overflow-hidden bg-[#020202]">
      {/* 🌌 Deep Space Nebula (Subtle) */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
            background: 'radial-gradient(circle at 50% 50%, rgba(0, 240, 255, 0.05) 0%, transparent 70%)'
        }}
      />

      {/* 🚀 Infinite Parallax Grid Layers (GPU OPTIMIZED) */}
      {layers.map((layer) => (
        <motion.div
          key={layer}
          animate={{ 
            scale: [1, 1.1, 1],
            rotate: [layer * 10, layer * 10 + 2, layer * 10]
          }}
          transition={{ 
            duration: 20 + (layer * 10), 
            repeat: Infinity, 
            ease: "linear" 
          }}
          className="absolute inset-[-50%]"
          style={{ 
              opacity: gridOpacity,
              backgroundImage: `linear-gradient(rgba(0, 240, 255, 0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 240, 255, 0.2) 1px, transparent 1px)`,
              backgroundSize: `${100 * layer}px ${100 * layer}px`,
              transform: `perspective(1000px) rotateX(60deg) translateZ(${layer * -100}px)`,
              willChange: 'transform', // 🖖 GPU RASTERIZATION BOOST
              backfaceVisibility: 'hidden'
          }}
        />
      ))}

      {/* 💎 Singularity Core Glow - GPU OPTIMIZED */}
      <motion.div 
        animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.05, 0.1, 0.05]
        }}
        transition={{ duration: 15, repeat: Infinity }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-500/5 rounded-full blur-[150px]"
        style={{ willChange: 'opacity, scale' }}
      />
    </div>
  );
}
