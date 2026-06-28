import React from "react";
import { motion } from "framer-motion";

const WeatherIcon = ({ condition, color }) => {
  return (
    <div className="relative w-14 h-14 flex items-center justify-center">
        <motion.div 
            animate={{ rotate: 360 }}
            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 border border-dashed rounded-full"
            style={{ borderColor: `${color}66` }}
        />
        <motion.div 
            animate={{ rotate: -360 }}
            transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
            className="absolute inset-2 border border-solid rounded-full opacity-30"
            style={{ borderColor: color }}
        />
        <svg viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" className="w-8 h-8 drop-shadow-[0_0_12px_rgba(0,240,255,0.8)] z-10">
            {condition <= 0 ? (
                <circle cx="12" cy="12" r="4" className="animate-pulse" />
            ) : (
                <path d="M17.5 19c2.5 0 4.5-2 4.5-4.5S20 10 17.5 10c-.2 0-.5 0-.7.1C16 7.1 13.2 5 10 5 6 5 2.7 8.2 2 12c-1.2.8-2 2.1-2 3.5C0 18 2 20 4.5 20h13" strokeLinecap="round" strokeLinejoin="round"/>
            )}
        </svg>
    </div>
  );
};

export default function WeatherWidget({ data }) {
  if (!data) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="relative overflow-hidden pointer-events-auto p-4 group"
    >
      <div className="absolute inset-0 bg-linear-to-br from-cyan-900/10 to-transparent pointer-events-none" />
      
      <motion.div 
         animate={{ top: ["-10%", "110%"] }}
         transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
         className="absolute inset-x-0 h-px z-10 opacity-30"
         style={{ background: 'linear-gradient(90deg, transparent, var(--stark-glow), transparent)' }}
      />

      <div className="flex items-center gap-6 relative z-10">
          <WeatherIcon condition={data.condition} color="var(--stark-glow)" />

          <div className="flex flex-col flex-1">
             <div className="flex justify-between items-start mb-2">
                <div className="flex items-start gap-1">
                    <span className="text-4xl font-black text-white tracking-tighter drop-shadow-[0_0_15px_rgba(255,255,255,0.4)]">
                        {data.temp}
                    </span>
                    <span className="text-[10px] font-black text-cyan-400 uppercase tracking-widest mt-1">°C</span>
                </div>
                
                <div className="flex flex-col items-end pt-1 leading-none">
                    <span className="text-[7px] font-black text-cyan-500 uppercase tracking-[0.3em]">Atmospheric_Sync</span>
                    <span className="text-[8px] font-mono text-cyan-300 uppercase tracking-widest opacity-80 shadow-cyan-400 drop-shadow-[0_0_5px_rgba(0,255,255,0.5)]">Status: Nominal</span>
                </div>
             </div>

             <div className="grid grid-cols-2 gap-4 mt-2 pt-2 border-t border-cyan-500/20 relative">
                <div className="absolute -top-1 left-0 w-2 h-px bg-cyan-500" />
                <div className="absolute -top-1 right-0 w-2 h-px bg-cyan-500" />
                
                <div className="flex flex-col relative pl-2 border-l border-cyan-500/20">
                    <span className="text-[6px] font-black text-cyan-500/60 uppercase tracking-widest">Wind_Velocity</span>
                    <span className="text-[11px] font-mono text-white/90">
                        {data.wind}<span className="text-[7px] text-cyan-400 ml-1">km/h</span>
                    </span>
                </div>
                <div className="flex flex-col items-end text-right pr-2">
                    <span className="text-[6px] font-black text-cyan-500/60 uppercase tracking-widest">Visibility</span>
                    <span className="text-[11px] font-mono text-white/90">
                        98<span className="text-[7px] text-cyan-400 ml-1">%</span>
                    </span>
                </div>
             </div>
          </div>
      </div>
    </motion.div>
  );
}
