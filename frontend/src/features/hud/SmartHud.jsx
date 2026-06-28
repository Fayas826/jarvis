import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaCloudSun, FaYoutube, FaTasks, FaMicrochip } from "react-icons/fa";

export default function SmartHud({ context, status: _status }) {
  // context can be: 'default', 'weather', 'youtube', 'tasks'
  
  const variants = {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 }
  };

  return (
    <div className="fixed top-40 right-10 z-[115] w-[220px] flex flex-col gap-4">
      <AnimatePresence mode="wait">
        {context === 'weather' ? (
          <motion.div key="weather" {...variants} className="zenith-glass p-4 rounded-xl border border-blue-400/20 shadow-[0_0_30px_rgba(0,180,255,0.1)]">
             <div className="flex justify-between items-start mb-3">
                <FaCloudSun className="text-yellow-400 text-xl" />
                <span className="text-[9px] font-mono text-blue-400 font-black">24°C // NYC</span>
             </div>
             <div className="space-y-1.5 opacity-60 text-[8px] uppercase tracking-widest font-mono">
                <div>HUMIDITY: 45%</div>
                <div>WIND: 12KM/H</div>
             </div>
          </motion.div>
        ) : context === 'youtube' ? (
          <motion.div key="youtube" {...variants} className="zenith-glass p-4 rounded-xl border border-red-500/20 shadow-[0_0_30px_rgba(255,0,0,0.1)]">
             <FaYoutube className="text-red-500 text-xl mb-3" />
             <div className="space-y-2">
                {[1, 2].map(i => (
                  <div key={i} className="group cursor-pointer">
                    <div className="w-full h-12 bg-black/40 rounded-lg mb-1 relative overflow-hidden">
                       <div className="absolute inset-0 bg-red-500/10 group-hover:bg-red-500/20 transition-all"></div>
                    </div>
                    <div className="text-[7px] uppercase tracking-widest text-gray-400 line-clamp-1">STRM_{i}</div>
                  </div>
                ))}
             </div>
          </motion.div>
        ) : context === 'tasks' ? (
            <motion.div key="tasks" {...variants} className="zenith-glass p-4 rounded-xl border border-green-500/20 shadow-[0_0_30px_rgba(0,255,0,0.1)]">
               <FaTasks className="text-green-500 text-xl mb-3" />
               <div className="space-y-1.5 font-mono text-[8px] uppercase tracking-widest text-gray-400">
                  <div className="flex items-center gap-2"><div className="w-1 h-1 bg-green-500 rounded-full"></div> KERNEL_SYNC</div>
                  <div className="flex items-center gap-2"><div className="w-1 h-1 bg-gray-500 rounded-full opacity-50"></div> ETHICS_PATCH</div>
               </div>
            </motion.div>
        ) : (
          <motion.div key="default" {...variants} className="zenith-glass p-4 rounded-xl border border-cyan-500/10 opacity-60">
             <div className="flex justify-between items-center mb-3">
                <FaMicrochip className="text-cyan-400 text-xl animate-pulse" />
                <span className="text-[7px] text-cyan-500/40 font-mono tracking-widest uppercase">Buffer_Active</span>
             </div>
             <div className="h-[1.5px] w-full bg-cyan-900/20 rounded-full overflow-hidden mb-2">
                <motion.div initial={{ x: '-100%' }} animate={{ x: '100%' }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} className="w-1/2 h-full bg-cyan-500/40"></motion.div>
             </div>
             <div className="text-[6px] tracking-[0.4em] text-cyan-500/30 uppercase font-mono">System_Auth_OK</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
