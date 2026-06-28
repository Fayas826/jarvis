import React from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function TaskManagerHUD({ tasks, onKill }) {
  if (!tasks || tasks.length === 0) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: -30 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex flex-col gap-4 pointer-events-auto w-64 glass-panel p-4"
    >
      <div className="flex flex-col gap-1">
         <div className="flex justify-between items-center">
            <span className="text-[9px] text-cyan-500 font-mono tracking-[0.4em] uppercase font-black">Active_Threads</span>
            <div className="w-8 h-[1px] bg-amber-500/40" />
         </div>
         <div className="text-[6px] opacity-30 font-mono">S.I._TASK_LOAD_V4 // OMEGA</div>
      </div>

      <div className="flex flex-col gap-2 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
         <AnimatePresence>
            {tasks.map((task, i) => (
               <motion.div 
                  key={`${task.name}-${i}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ delay: i * 0.05 }}
                  className={`p-3 rounded-sm border transition-all ${
                      task.mem > 1000 ? 'border-amber-500/20 bg-amber-500/5' : 'border-cyan-500/10 bg-cyan-500/5'
                  } hover:bg-white/5 group`}
               >
                  <div className="flex justify-between items-center mb-2">
                     <span className={`text-[10px] font-bold truncate w-32 uppercase tracking-wide ${
                         task.mem > 1000 ? 'text-amber-400' : 'text-cyan-400'
                     }`}>
                        {task.name}
                     </span>
                     <span className="text-[9px] text-cyan-500/50 font-mono">
                        {task.mem} MB
                     </span>
                  </div>

                  <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden relative">
                     <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min((task.mem / 2000) * 100, 100)}%` }}
                        className={`absolute inset-y-0 ${task.mem > 1000 ? 'bg-amber-500' : 'bg-cyan-500/60'}`}
                     />
                  </div>

                  <div className="flex justify-end mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                     <button 
                        onClick={() => onKill(task.name)}
                        className="text-[8px] text-red-500/60 hover:text-red-500 uppercase font-black font-mono tracking-widest border border-red-500/20 px-2 py-1 rounded"
                     >
                        Terminate
                     </button>
                  </div>
               </motion.div>
            ))}
         </AnimatePresence>
      </div>
      <div className="absolute top-1 right-2 w-1 h-1 rounded-full bg-amber-500 shadow-[0_0_5px_amber] animate-pulse" />
    </motion.div>
  );
}
