import React from "react";
import { motion } from "framer-motion";
import AICore from "@/features/hud/AICore";
import VitalsMonitor from "@/features/hud/VitalsMonitor";

export default function MiniHud({ thermalData, status, mode, systemPulse }) {
  return (
    <div className="fixed inset-0 bg-black flex flex-col items-center justify-center p-6 font-mono text-cyan-400 select-none overflow-hidden">
       {/* 🧩 PORTABLE_TELEMETRY_ENGINE */}
       <div className="absolute top-4 left-4 border-l-2 border-cyan-500/40 pl-4 py-2">
          <span className="text-[10px] font-black tracking-[0.4em]">PORTABLE_HUD_v1.0</span>
       </div>

       <motion.div 
         animate={{ scale: systemPulse ? 1.02 : 1 }}
         className="w-48 h-48 mb-8"
       >
          <AICore isOnline={true} mode={mode} status={status} systemPulse={systemPulse} />
       </motion.div>

       <div className="w-full max-w-[250px] flex flex-col gap-4">
          <VitalsMonitor status={status} hideLabels={true} threatLevel="NOMINAL" />
          
          <div className="grid grid-cols-2 gap-4 border-t border-cyan-500/10 pt-4">
             <div className="flex flex-col gap-1">
                <span className="text-[8px] opacity-40">CPU_LOAD</span>
                <span className="text-xs font-bold">{thermalData.cpu_load}</span>
             </div>
             <div className="flex flex-col gap-1 items-end">
                <span className="text-[8px] opacity-40">GPU_TEMP</span>
                <span className="text-xs font-bold text-orange-400">{thermalData.gpu}°C</span>
             </div>
          </div>
       </div>

       <div className="absolute bottom-4 right-4 text-[7px] opacity-20 tracking-[0.6em]">
          O.M.E.G.A. ZENITH // LITE_ARRAY
       </div>
    </div>
  );
}
