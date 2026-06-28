import React from "react";
import { motion } from "framer-motion";

export default function GlobalScanner({ status: _status }) {
  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="stark-widget p-0 overflow-hidden relative group pointer-events-auto"
      style={{ 
        background: 'rgba(0, 10, 20, 0.4)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(var(--stark-glow-rgb), 0.1)',
        borderRadius: '2px'
      }}
    >
      {/* 🛡️ SCANNING_LASER_EFFECT */}
      <motion.div 
         animate={{ top: ["-10%", "110%"] }}
         transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
         className="absolute inset-x-0 h-[1px] bg-cyan-400/20 z-10"
      />

      <div className="p-4 flex flex-col gap-3">
          <div className="flex justify-between items-center border-b border-cyan-500/10 pb-2">
             <span className="text-[7px] text-cyan-400/50 font-mono tracking-[0.4em] uppercase">Sector_Analysis</span>
             <span className="text-[8px] font-mono text-cyan-400 animate-pulse uppercase">Link: [STABLE]</span>
          </div>

          <div className="flex items-center gap-6">
              <div className="w-12 h-12 relative flex items-center justify-center">
                  <motion.div 
                      animate={{ rotateY: 360 }}
                      transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                      style={{ transformStyle: "preserve-3d" }}
                      className="w-full h-full relative"
                  >
                      {[0, 45, 90].map((deg) => (
                          <div 
                              key={`lat-${deg}`}
                              style={{ transform: `rotateX(${deg}deg)` }}
                              className="absolute inset-0 rounded-full border border-cyan-500/20"
                          />
                      ))}
                      {[0, 45, 90].map((deg) => (
                          <div 
                              key={`long-${deg}`}
                              style={{ transform: `rotateY(${deg}deg)` }}
                              className="absolute inset-0 rounded-full border border-cyan-500/20"
                          />
                      ))}
                  </motion.div>
                  {/* CENTRAL_CORE_PULSE */}
                  <div className="absolute w-1 h-1 bg-cyan-400 rounded-full animate-ping" />
              </div>

              <div className="flex flex-col gap-1 flex-1">
                 <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                    <div className="flex flex-col">
                        <span className="text-[5px] font-black text-cyan-400/40 tracking-widest uppercase">LATITUDE</span>
                        <span className="text-[8px] font-mono text-white/80 tracking-tighter">28.6142° N</span>
                    </div>
                    <div className="flex flex-col text-right">
                        <span className="text-[5px] font-black text-cyan-400/40 tracking-widest uppercase">LONGITUDE</span>
                        <span className="text-[8px] font-mono text-white/80 tracking-tighter">77.2088° W</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-[5px] font-black text-cyan-400/40 tracking-widest uppercase">ALTITUDE</span>
                        <span className="text-[8px] font-mono text-white/80 tracking-tighter">12.4K MSL</span>
                    </div>
                    <div className="flex flex-col text-right">
                        <span className="text-[5px] font-black text-cyan-400/40 tracking-widest uppercase">VELOCITY</span>
                        <span className="text-[8px] font-mono text-white/80 tracking-tighter">0.00 M/S</span>
                    </div>
                 </div>
              </div>
          </div>
      </div>
    </motion.div>
  );
}
