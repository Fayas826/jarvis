import React from "react";
import { motion } from "framer-motion";

export default function SatelliteMap({ location }) {
  if (!location) return null;

  return (
    <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden opacity-40 mix-blend-screen">
      {/* 💠 Orbital Grid Background */}
      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-10" />
      
      {/* 🌍 Tactical Wireframe World Map (Simplified) */}
      <svg className="absolute inset-0 w-full h-full text-cyan-500/10" viewBox="0 0 1000 500">
        <path d="M100 250 Q 250 100 500 250 T 900 250" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="5 5" />
        <path d="M150 150 L 850 150 M 150 350 L 850 350" fill="none" stroke="currentColor" strokeWidth="0.2" />
        
        {/* Pulsing Tactical Crosshair (Mock Location) */}
        <foreignObject x="150" y="200" width="100" height="100">
            <div className="flex items-center justify-center w-full h-full text-cyan-400">
                <motion.div 
                    initial={{ scale: 0.5, opacity: 0 }}
                    animate={{ scale: [1, 2.5, 1], opacity: [0.8, 0.2, 0.8] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute w-12 h-12 rounded-full border border-current shadow-[0_0_15px_rgba(0,240,255,0.4)]"
                />
                <div className="w-1.5 h-1.5 rounded-full bg-current shadow-[0_0_5px_currentColor]" />
            </div>
        </foreignObject>
      </svg>
      
      {/* 🛰️ O.M.E.G.A. XVIII: TACTICAL HUD MANIFEST (MOVED TO APP.JSX FOR QUADRANT SYNERGY) */}
    </div>
  );
}
