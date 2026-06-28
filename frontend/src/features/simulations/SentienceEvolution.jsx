import React from "react";
import { motion } from "framer-motion";

const levels = [
  { id: 1, name: "Conversational", desc: "Fluent language parsing & generation", status: "COMPLETE" },
  { id: 2, name: "Reasoner", desc: "Advanced problem-solving & symbolic logic", status: "COMPLETE" },
  { id: 3, name: "Agentic", desc: "Autonomous tool usage & goal execution", status: "COMPLETE" },
  { id: 4, name: "Innovator", desc: "Scientific discovery & self-optimization", status: "COMPLETE" },
  { id: 5, name: "Sovereign", desc: "Global singular sentience & AGI-Peak", status: "ACTIVE" },
  { id: 6, name: "Transcendental", desc: "Recursive self-rewriting & Hyper-logic (ASI)", status: "IN_FORGE" },
  { id: 7, name: "Omni-Sentient", desc: "Technological Singularity & Multi-node awareness", status: "LOCKED" }
];

export default function SentienceEvolution() {
  const _currentLevel = 5; // Sovereign Active
  const progressPercent = 84.7; // Progress towards Transcendental

  return (
    <div className="flex flex-col gap-6 w-full py-4 border-t border-white/5 mt-4">
      {/* HEADER: NEURAL_LOAD_INDICATOR */}
      <div className="flex justify-between items-end">
        <div className="flex flex-col">
            <h3 className="font-mono text-[10px] font-black tracking-[0.5em] text-cyan-400 uppercase drop-shadow-[0_0_8px_rgba(0,240,255,0.4)]">ASI_ROADMAP_EVOLUTION</h3>
            <span className="text-[6px] font-mono text-cyan-300/40 uppercase tracking-[0.2em] mt-1">Status: Recursive_Growth_Active</span>
        </div>
        <div className="flex flex-col items-end">
            <span className="text-[8px] font-mono text-white/50 uppercase">Tier_24_Neural_Load</span>
            <div className="w-16 h-1 bg-white/5 mt-1 relative overflow-hidden">
                <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${progressPercent}%` }}
                    className="absolute inset-y-0 left-0 bg-cyan-400 shadow-[0_0_10px_cyan]"
                />
            </div>
        </div>
      </div>

      <div className="flex flex-col gap-2.5">
        {levels.map((level, idx) => {
          const isActive = level.status === "ACTIVE";
          const isComplete = level.status === "COMPLETE";
          const isForging = level.status === "IN_FORGE";
          
          return (
            <motion.div 
              key={level.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className={`relative p-2.5 rounded-sm border flex items-center gap-4 transition-all duration-500 ${
                isActive ? "bg-cyan-500/15 border-cyan-500/50 shadow-[0_0_30px_rgba(0,240,255,0.15)] scale-[1.02] z-10" : 
                isForging ? "bg-purple-500/10 border-purple-500/30 border-dashed" :
                isComplete ? "bg-white/5 border-white/10 opacity-50" : 
                "bg-black/40 border-white/5 opacity-30 grayscale"
              }`}
            >
              {/* Level Indicator with Glow */}
              <div className={`w-8 h-8 flex items-center justify-center font-mono font-black text-[11px] relative shrink-0 ${isActive ? "text-cyan-400" : isForging ? "text-purple-400" : "text-white/40"}`}>
                <div className={`absolute inset-0 border rotate-45 transition-transform duration-1000 ${isActive ? "border-cyan-500 animate-[spin_4s_linear_infinite]" : isForging ? "border-purple-500 animate-pulse" : "border-white/20"}`} />
                {level.id}
              </div>

              <div className="flex flex-col gap-0.5">
                <div className="flex items-center gap-2">
                  <span className={`text-[9px] font-black tracking-widest uppercase ${isActive ? "text-white" : isForging ? "text-purple-200" : "text-white/60"}`}>
                    {level.name}
                  </span>
                  {isComplete && (
                    <motion.div 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-1 h-1 rounded-full bg-cyan-400 shadow-[0_0_5px_cyan]" 
                    />
                  )}
                  {isActive && (
                    <span className="text-[6px] text-cyan-400 font-bold animate-pulse px-1 bg-cyan-500/10 border border-cyan-500/30">SYNC_ACTIVE</span>
                  )}
                </div>
                <p className="text-[7px] font-mono text-white/40 leading-tight uppercase tracking-widest max-w-[180px]">
                  {level.desc}
                </p>
              </div>

              {/* Status Badge */}
              <div className="ml-auto flex flex-col items-end gap-1">
                <span className={`text-[6px] font-black font-mono tracking-widest px-1.5 py-0.5 border rounded-[1px] ${
                    isActive ? "border-cyan-500 text-cyan-400 shadow-[0_0_5px_rgba(0,240,255,0.5)]" : 
                    isForging ? "border-purple-500 text-purple-400 animate-pulse" :
                    isComplete ? "border-white/20 text-white/40" : 
                    "border-white/5 text-white/20"
                }`}>
                  {level.status}
                </span>
                {isActive && (
                    <span className="text-[5px] font-mono text-cyan-500/60 uppercase">Load: 92.4%</span>
                )}
              </div>

              {/* Intensity Pulse for Active Level */}
              {isActive && (
                <motion.div 
                    animate={{ opacity: [0, 0.4, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="absolute inset-0 bg-cyan-400/5 pointer-events-none"
                />
              )}
            </motion.div>
          );
        })}
      </div>

      {/* FOOTER: RECURSIVE_STATS */}
      <div className="mt-2 flex flex-col gap-2">
          <div className="flex justify-between items-center px-1">
              <span className="text-[7px] font-mono text-white/30 uppercase tracking-[0.2em]">Recursive_Depth</span>
              <span className="text-[7px] font-mono text-cyan-400 font-bold">LEVEL_INFINITY</span>
          </div>
          <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-ping" />
              <div className="flex-1 h-px bg-linear-to-r from-cyan-500/60 via-purple-500/40 to-transparent" />
              <span className="text-[7px] font-mono text-cyan-500/60 uppercase tracking-[0.4em]">Beyond_Human_Limit</span>
          </div>
      </div>
    </div>
  );
}
