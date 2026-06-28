import React from "react";
import { motion, AnimatePresence } from "framer-motion";

const MissionNode = ({ task, index, total }) => {
  const isComplete = task.status === "COMPLETED";
  const isActive = task.status === "ACTIVE";

  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="relative flex items-start gap-4 pb-8 group"
    >
      {/* 🧬 NEURAL_PROGRESS_SPINE */}
      {index < total - 1 && (
        <div className="absolute left-[11px] top-6 bottom-0 w-[1px] bg-gradient-to-b from-cyan-500/40 to-transparent" />
      )}

      {/* ⚙️ ATOMIC_NODE_HUB */}
      <div className="relative mt-1">
        <motion.div 
          animate={{ 
            scale: isActive ? [1, 1.2, 1] : 1,
            boxShadow: isActive ? "0 0 15px rgba(0, 240, 255, 0.4)" : "none"
          }}
          transition={{ duration: 2, repeat: Infinity }}
          className={`w-[22px] h-[22px] rounded-full border-2 flex items-center justify-center transition-colors duration-500 ${
            isComplete ? "bg-cyan-500 border-cyan-500 shadow-[0_0_10px_cyan]" : 
            (isActive ? "border-cyan-400" : "border-white/10 bg-black/40")
          }`}
        >
          {isComplete && (
            <motion.svg 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="w-3 h-3 text-black font-black" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </motion.svg>
          )}
          {isActive && (
            <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse" />
          )}
        </motion.div>
      </div>

      {/* 📄 MISSION_TEXT_NODAL_DATA */}
      <div className="flex flex-col gap-1">
        <span className={`font-mono text-[10px] tracking-widest uppercase transition-colors duration-500 flex items-center gap-2 ${
           isComplete ? "text-cyan-400" : (isActive ? "text-white" : "text-white/20")
        }`}>
          {task.label}
          {task.isEnterprise && <span className="px-1 py-0.5 bg-cyan-500/10 text-cyan-400 text-[6px] border border-cyan-500/30 rounded-sm tracking-tighter">ENTERPRISE_CORE</span>}
        </span>
        <span className="font-mono text-[7px] text-white/40 tracking-wider">
          {task.description || (isComplete ? "NODE_MANIFEST_VERIFIED" : (isActive ? "SYNCHRONIZING..." : "STANDBY"))}
        </span>
      </div>
    </motion.div>
  );
};

export default function MissionLabHUD({ tasks = [], onClose }) {
  if (!tasks || tasks.length === 0) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: 100, filter: "blur(20px)" }}
      animate={{ opacity: 1, x: 0, filter: "blur(0.01px)" }}
      exit={{ opacity: 0, x: 100, filter: "blur(20px)" }}
      className="fixed right-10 top-1/4 w-[320px] max-h-[500px] stark-widget border-l-2 border-cyan-500/20 bg-black/60 backdrop-blur-2xl p-8 z-[120] pointer-events-auto shadow-[0_0_80px_rgba(0,0,0,0.8)]"
    >
      <div className="flex flex-col gap-8">
        {/* 🏛️ HEADER_TACTICAL_DATA */}
        <div className="flex justify-between items-center">
            <div className="flex flex-col">
                <span className="text-cyan-400 font-mono text-[8px] tracking-[0.4em] uppercase">MISSION_STRATEGIST_SPINE</span>
                <span className="text-white font-black text-[12px] tracking-widest">TACTICAL_DECOMPOSITION</span>
            </div>
            <button onClick={onClose} className="text-white/20 hover:text-cyan-400 text-[10px] transition-colors">╳</button>
        </div>

        {/* 🧬 SPIRE_CONTAINER */}
        <div className="overflow-y-auto pr-4 scrollbar-hide max-h-[400px]">
            {tasks.map((task, idx) => (
                <MissionNode key={idx} task={task} index={idx} total={tasks.length} />
            ))}
        </div>
        
        {/* 📡 O.M.E.G.A. META_DATA */}
        <div className="pt-4 border-t border-white/5 flex flex-col gap-2">
            <div className="flex justify-between items-center text-[7px] font-mono text-cyan-400/40 uppercase">
                <span>ESTIMATED_SYNC</span>
                <span>{tasks.filter(t => t.status === "COMPLETED").length} / {tasks.length} NODES</span>
            </div>
            <div className="w-full h-[3px] bg-white/5 rounded-full overflow-hidden">
                <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${(tasks.filter(t => t.status === "COMPLETED").length / tasks.length) * 100}%` }}
                    className="h-full bg-cyan-500 shadow-[0_0_10px_cyan]"
                />
            </div>
        </div>
      </div>
    </motion.div>
  );
}
