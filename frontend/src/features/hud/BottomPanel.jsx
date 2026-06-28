import React from "react";
import { motion } from "framer-motion";

export default function BottomPanel() {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="panel-bottom"
    >
      <div className="flex flex-col gap-2">
        <p className="system-log">CORE_THERMAL_DEPTH — 33.17°C</p>
        
        <div className="bar w-64 h-[2px] bg-cyan-500/10 overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: "60%" }}
            transition={{ duration: 2, ease: "easeOut" }}
            className="h-full bg-cyan-400 shadow-[0_0_10px_rgba(0,255,255,0.5)]"
          />
        </div>

        <p className="text-[10px] opacity-40 tracking-[0.3em] mt-1">AMBIENCE_CONTROL</p>
      </div>
    </motion.div>
  );
}
