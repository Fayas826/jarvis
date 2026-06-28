import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

export default function HoloMetadata({ status: _status, className = "" }) {
  const [data, setData] = useState({
    load: 12.4,
    temp: 32,
    latency: 7
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setData({
        load: (10 + Math.random() * 5).toFixed(1),
        temp: (30 + Math.random() * 4).toFixed(0),
        latency: (5 + Math.random() * 4).toFixed(0)
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`z-[100] flex flex-col items-center gap-2 pointer-events-none ${className}`}
    >
      <div className="flex items-center gap-4 px-6 py-1.5 zenith-glass border border-cyan-500/20 shadow-[0_0_30px_rgba(0,180,255,0.1)] rounded-full text-cyan-400">
         <div className="flex flex-col items-end">
            <span className="text-[6px] text-cyan-500/40 font-mono tracking-[0.2em] uppercase">System_Load</span>
            <span className="text-[9px] font-black font-mono">{data.load}%</span>
         </div>
         
         <div className="w-[1px] h-6 bg-cyan-500/20" />
         
         <div className="flex flex-col items-center min-w-[120px]">
            <span className="text-[7px] font-black tracking-[0.5em] uppercase">O.M.E.G.A_ZENITH</span>
            <motion.div 
               animate={{ width: ["0%", "100%", "0%"] }}
               transition={{ duration: 4, repeat: Infinity }}
               className="h-[1px] bg-cyan-400/40 mt-0.5"
            />
         </div>
         
         <div className="w-[1px] h-6 bg-cyan-500/20" />
         
         <div className="flex flex-col items-start pr-1">
            <span className="text-[6px] text-cyan-500/40 font-mono tracking-[0.2em] uppercase">Core_Temp</span>
            <span className="text-[9px] font-black font-mono">{data.temp}°C</span>
         </div>
      </div>
    </motion.div>
  );
}
