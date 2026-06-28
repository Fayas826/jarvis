import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaCheckCircle, FaSpinner } from "react-icons/fa";

export default function CommandExecutionPanel({ actions }) {
  if (!actions || actions.length === 0) {
    return (
      <div className="relative group p-[1px] rounded-xl overflow-hidden glow">
         <div className="absolute inset-0 bg-blue-500/20 backdrop-blur-md rounded-xl"></div>
         <div className="relative p-4 rounded-xl bg-black/50 border border-white/5 h-32 flex flex-col items-center justify-center text-center">
            <span className="text-gray-500 font-mono text-sm tracking-widest">COMMAND ENGINE</span>
            <span className="text-gray-600 font-mono text-xs mt-2 uppercase">Awaiting Action sequence...</span>
         </div>
      </div>
    );
  }

  // Reverse to show latest first
  const displayActions = [...actions].reverse().slice(0, 5);

  return (
    <div className="glass-panel p-4 rounded-sm shadow-[0_0_50px_rgba(0,0,0,0.8)] h-48 flex flex-col relative">
      {/* 🛠️ Micro-Detailing Layer */}
      <div className="absolute top-1 left-2 text-[6px] text-cyan-500/20 font-black tracking-[0.2em]">S.I._COMMAND_EXEC_V4 // OMEGA</div>
      <div className="absolute bottom-1 right-2 w-8 h-[1px] bg-amber-500/30" />

      <h3 className="text-[10px] font-black text-amber-500/80 tracking-[0.4em] uppercase mb-4 border-b border-white/5 pb-2 flex justify-between items-center">
         <span>Command_Log</span>
         <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_5px_cyan] animate-pulse" />
      </h3>
      
      <div className="flex-1 overflow-y-auto space-y-3 font-mono text-[9px] pr-1 custom-scrollbar">
        <AnimatePresence>
          {displayActions.map((log, i) => (
            <motion.div
              key={actions.length - i}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className={`flex items-center gap-3 p-2 rounded-sm border transition-all ${
                  i === 0 ? 'bg-amber-500/5 border-amber-500/20' : 'bg-white/5 border-white/5 opacity-60'
              }`}
            >
              {i === 0 ? (
                 <FaSpinner className="text-amber-400 animate-spin flex-shrink-0" />
              ) : (
                 <FaCheckCircle className="text-cyan-400 flex-shrink-0" />
              )}
              
              <div className="flex flex-col">
                <span className={`font-black tracking-widest ${i === 0 ? 'text-amber-400' : 'text-cyan-400/80'}`}>
                  [{log.action.toUpperCase()}]
                </span>
                <span className="text-white/40 uppercase tracking-tighter">Target: {log.target}</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
