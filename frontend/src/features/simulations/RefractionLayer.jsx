import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function RefractionLayer({ active, stress = 0 }) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  if (!active) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-[1000] overflow-hidden mix-blend-overlay opacity-30">
      <svg width="100%" height="100%">
        <filter id="cortex-refraction">
          <feTurbulence 
            type="fractalNoise" 
            baseFrequency={0.01 + (stress * 0.05)} 
            numOctaves="3" 
            result="noise" 
          />
          <feDisplacementMap 
            in="SourceGraphic" 
            in2="noise" 
            scale={20 + (stress * 50)} 
          />
        </filter>

        {/* 🌌 Optical Displacement Pulse */}
        <motion.circle
          cx={mousePos.x}
          cy={mousePos.y}
          r={150 + (stress * 200)}
          fill="none"
          stroke="url(#refraction-grad)"
          strokeWidth="2"
          filter="url(#cortex-refraction)"
          animate={{
            r: [140, 160, 140],
            opacity: [0.1, 0.4, 0.1]
          }}
          transition={{ duration: 4, repeat: Infinity }}
        />

        <defs>
          <radialGradient id="refraction-grad">
            <stop offset="0%" stopColor="rgba(0, 240, 255, 0.4)" />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
        </defs>
      </svg>

      {/* 🔮 Crystalline Lattice Overlay */}
      <div 
        className="absolute inset-0 opacity-5"
        style={{ 
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0l30 30-30 30-30-30z' fill-opacity='0.1' fill='%2300f0ff' fill-rule='evenodd'/%3E%3C/svg%3E")`,
            backgroundSize: '60px 60px'
        }}
      />
    </div>
  );
}
