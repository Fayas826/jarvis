import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaGlobeAmericas, FaChevronRight } from "react-icons/fa";
import CalendarWidget from "@/features/hud/CalendarWidget";

export default function Sidebar({ _onManifestChange, _isProjecting = false, children }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      initial={{ width: 60 }}
      animate={{ width: isHovered ? 480 : 60 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className={`h-screen flex flex-col z-200 transition-all overflow-hidden relative border-r border-cyan-500/20 ${isHovered ? 'zenith-glass' : ''}`}
      style={{ 
        background: isHovered ? "rgba(0, 8, 15, 0.6)" : "rgba(0, 5, 10, 0.3)",
        backdropFilter: "blur(25px) saturate(200%)"
      }}
    >
      <div className="flex h-full">
        {/* 🚀 NAVIGATION CHANNEL */}
        <nav className="w-[60px] flex flex-col items-center justify-center gap-8 shrink-0">
            <div className="w-px h-32 bg-linear-to-b from-transparent via-cyan-500/40 to-transparent"></div>
            <div className="text-[9px] font-mono text-cyan-500/40 vertical-text tracking-[0.5em] rotate-180 uppercase">
               ZENITH_SIDEBAR_V4.0
            </div>
            <div className="w-px h-32 bg-linear-to-b from-transparent via-cyan-500/40 to-transparent"></div>

            {/* MANIFEST BUTTON */}
            <div className="w-10 h-10 rounded-full flex items-center justify-center bg-cyan-500/5 border border-cyan-500/10">
                <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_10px_cyan]" />
            </div>
        </nav>

        {/* 🧬 NEURAL DIAGNOSTICS: QUAD-STACK (FLOATING DATA) */}
        <AnimatePresence mode="wait">
            {isHovered && (
                <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="flex-1 flex flex-col gap-6 pl-10 pr-6 py-8 overflow-y-auto custom-scrollbar overflow-x-hidden"
                >
                    <div className="flex flex-col gap-2 shrink-0">
                        <div className="flex items-center gap-3">
                            <span className="text-[10px] font-black tracking-[0.6em] text-cyan-400 uppercase">NEURAL_ZENITH_STACK</span>
                            <div className="px-1.5 py-0.5 rounded-[2px] bg-cyan-500/10 border border-cyan-500/20 text-[6px] text-cyan-400 font-mono">NODE_LIVE</div>
                        </div>
                        <p className="text-[7px] text-cyan-500/30 font-mono tracking-widest uppercase mb-2">Synthetic Synapse Monitoring & Hardware Resonance</p>
                        <div className="w-full h-px bg-linear-to-r from-cyan-500/40 to-transparent" />
                    </div>

                    {/* NEURAL STACK AREA: Vitals, Heatmap, and NEW Calendar */}
                    <div className="flex flex-col gap-12 pb-12">
                        {children}
                        
                        <div className="mt-4 pt-8 border-t border-cyan-500/10">
                            <CalendarWidget />
                        </div>
                    </div>

                    <div className="mt-auto border-t border-white/5 pt-8 shrink-0">
                         <div className="flex flex-col gap-4">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(0,240,255,0.15)]">
                                   <span className="text-xs text-cyan-400 font-bold uppercase">FA</span>
                                </div>
                                <div className="flex flex-col whitespace-nowrap">
                                   <span className="text-[11px] text-white font-black tracking-widest uppercase">Admin: Fayas</span>
                                   <span className="text-[8px] text-green-500 font-mono tracking-tighter animate-pulse uppercase">Neural_Link_Connected_ZENITH</span>
                                </div>
                            </div>
                         </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
      </div>

      {!isHovered && (
          <div className="absolute top-1/2 right-2 -translate-y-1/2 text-cyan-500/40">
             <FaChevronRight size={12} className="animate-pulse" />
          </div>
      )}
    </motion.div>
  );
}
