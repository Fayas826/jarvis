import React from "react";
import { motion } from "framer-motion";

const seededValue = (index, seed = 43) => {
  const value = Math.sin(index * 59.23 + seed) * 10000;
  return value - Math.floor(value);
};

export default function SpotifyWidget({ status, onCommand }) {
  const isPlaying = status === 'speaking' || status === 'listening';

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="stark-widget p-0 overflow-hidden relative group pointer-events-auto w-full shadow-[0_0_30px_rgba(0,180,255,0.15)]"
      style={{ 
        background: 'rgba(0, 10, 15, 0.6)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(var(--stark-glow-rgb), 0.15)',
        borderRadius: '2px'
      }}
    >
      {/* 🛡️ SCANNING_LASER_EFFECT */}
      <motion.div 
         animate={{ top: ["-10%", "110%"] }}
         transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
         className="absolute inset-x-0 h-[1px] bg-cyan-400/30 z-10 drop-shadow-[0_0_5px_rgba(0,240,255,0.6)]"
      />

      <div className="p-3 flex flex-col gap-2">
          <div className="flex justify-between items-center border-b border-cyan-500/20 pb-1">
             <span className="text-[6px] text-cyan-500/60 font-mono tracking-[0.4em] uppercase shadow-cyan-400">Ambiance_Control_v4</span>
             <div className="flex gap-1">
                 <div className="w-1 h-1 bg-cyan-400 shadow-[0_0_5px_cyan] rounded-full animate-pulse" />
                 <div className="w-1 h-1 bg-cyan-400/20 rounded-full" />
             </div>
          </div>

          <div className="flex items-center gap-3">
              <div className="w-10 h-10 relative flex items-center justify-center border border-cyan-500/20 rounded-sm overflow-hidden bg-cyan-900/10 group-hover:bg-cyan-900/30 transition-colors">
                  <motion.div 
                      animate={{ rotate: isPlaying ? [0, 360] : 0 }}
                      transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
                      className="absolute inset-1.5 border-[0.5px] border-dashed border-cyan-400/50 rounded-full"
                  />
                  <div className="relative z-10 text-cyan-400 shadow-cyan-400 drop-shadow-[0_0_5px_rgba(0,255,255,0.8)]">
                      <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                          <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                      </svg>
                  </div>
              </div>

              <div className="flex flex-col flex-1 relative">
                  <div className="absolute -left-2 top-0 bottom-0 w-[1px] bg-gradient-to-b from-cyan-500/40 to-transparent" />
                  
                  <span className="text-[8px] font-black text-cyan-300 tracking-[0.2em] uppercase drop-shadow-[0_0_5px_rgba(0,255,255,0.4)]">Deep_Space_Resonance</span>
                  <span className="text-[5px] text-cyan-600/80 font-mono italic mt-0.5 tracking-widest">SYST_LINK_OK: 42.0ms</span>
                  
                  <div className="flex gap-0.5 h-3 items-end mt-1 opacity-80">
                      {Array.from({ length: 18 }).map((_, i) => (
                          <motion.div 
                              key={i}
                              animate={{ height: isPlaying ? [2, seededValue(i, 5) * 10 + 2, 2] : 2 }}
                              transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.05 }}
                              className="w-[1.5px] bg-cyan-400 rounded-t-[1px]"
                          />
                      ))}
                  </div>
              </div>

              <div className="flex gap-2 items-center text-cyan-500/60 pl-2 border-l border-cyan-500/20">
                  <motion.button whileHover={{ scale: 1.1, color: "#00f0ff", filter: "drop-shadow(0 0 5px #00f0ff)" }} onClick={() => onCommand('play')} className="p-1 transition-all">
                      <svg className="w-3 h-3 fill-current" viewBox="0 0 20 20"><path d="M4 5h3v10H4V5zm9 0h3v10h-3V5z"/></svg>
                  </motion.button>
              </div>
          </div>
      </div>
    </motion.div>
  );
}
