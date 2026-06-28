import React from "react";
import { motion } from "framer-motion";

const ThreatBar = ({ label, percentage }) => (
    <div className="flex flex-col gap-0.5 w-full">
        <div className="flex justify-between items-end opacity-70">
            <span className="text-[7px] font-black uppercase tracking-[0.2em]">{label}</span>
            <span className="text-[8px] font-mono text-red-400">{percentage}%</span>
        </div>
        <div className="h-[2px] w-full bg-white/5 relative overflow-hidden rounded-full">
            <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${percentage}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className="h-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)] rounded-full"
            />
            {/* PING_RESONANCE */}
            <motion.div 
                animate={{ left: ["-100%", "200%"] }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                className="absolute inset-y-0 w-12 bg-gradient-to-r from-transparent via-white/40 to-transparent"
            />
        </div>
    </div>
);

export default function TacticalThreatScanner({ active }) {
  if (!active) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="stark-widget p-0 overflow-hidden relative group pointer-events-auto shadow-[0_0_30px_rgba(239,68,68,0.2)]"
      style={{ 
        background: 'rgba(15, 0, 0, 0.6)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(239, 68, 68, 0.15)',
        borderRadius: '2px'
      }}
    >
      {/* 🛡️ SCANNING_LASER_EFFECT */}
      <motion.div 
         animate={{ top: ["-10%", "110%"] }}
         transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }}
         className="absolute inset-x-0 h-[1px] bg-red-500/40 z-10 drop-shadow-[0_0_5px_rgba(255,0,0,0.8)]"
      />

      <div className="p-3 flex flex-col gap-3">
          <div className="flex justify-between items-center pb-1 border-b border-red-500/20 shadow-[0_1px_10px_rgba(255,0,0,0.1)]">
             <div className="flex items-center gap-2">
                 <div className="w-1 h-1 bg-red-500 shadow-[0_0_5px_red] animate-ping" />
                 <span className="text-[9px] font-black text-red-500 tracking-[0.3em] uppercase drop-shadow-[0_0_5px_rgba(255,0,0,0.4)]">Threat_Scanner</span>
             </div>
             <span className="text-[6px] font-mono text-white/30 uppercase tracking-widest">v3.0.42</span>
          </div>

          <div className="flex flex-col gap-2">
              <ThreatBar label="Thermal_Signature" percentage={94} />
              <ThreatBar label="EM_Disturbance" percentage={22} />
              <ThreatBar label="Neural_Oscillation" percentage={45} />
          </div>

          <div className="mt-1 p-2 bg-red-500/5 border border-red-500/20 rounded-sm relative overflow-hidden group-hover:bg-red-500/10 transition-colors">
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-red-500 to-transparent" />
              <div className="flex flex-col gap-0.5 relative z-10 pl-2">
                  <span className="text-[6px] font-black text-red-500/80 uppercase tracking-widest">Predicted_Focal_Lock</span>
                  <span className="text-[9px] font-mono text-white/90 uppercase tracking-tighter">STARK_IND_PROT_0X</span>
              </div>
              {/* CROSSHAIR_SIMULATION */}
              <div className="absolute right-1 top-1/2 -translate-y-1/2 w-6 h-6 opacity-30">
                  <div className="absolute inset-0 border-[0.5px] border-dashed border-red-500 rounded-full animate-spin" style={{ animationDuration: '6s' }} />
                  <div className="absolute top-1/2 left-0 w-full h-[0.5px] bg-red-500" />
                  <div className="absolute left-1/2 top-0 h-full w-[0.5px] bg-red-500" />
              </div>
          </div>
      </div>
    </motion.div>
  );
}
