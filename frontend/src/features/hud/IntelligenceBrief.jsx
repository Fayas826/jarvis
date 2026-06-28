import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/services/api";

export default function IntelligenceBrief({ active }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.getMissionLogs();
        setLogs(res.data.reverse()); // Latest first
      } catch {
        console.error("Neural link interrupted.");
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!active) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="w-full flex flex-col gap-3 p-3 rounded-[2px] border border-cyan-500/30 bg-gradient-to-br from-[#000a12]/90 to-[#001726]/90 backdrop-blur-xl shadow-[0_0_20px_rgba(0,0,0,0.8)]"
    >
      <div className="flex justify-between items-center mb-1">
         <span className="text-[10px] text-cyan-400 font-black tracking-[0.2em] uppercase drop-shadow-[0_0_8px_cyan]">INTELLIGENCE_BRIEF</span>
         <div className="flex gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 shadow-[0_0_10px_cyan]" />
            <div className="w-1.5 h-1.5 rounded-full bg-cyan-500/40" />
         </div>
      </div>
      
      <div className="flex flex-col gap-3 max-h-[100px] overflow-y-auto pr-2 scrollbar-hide">
         <AnimatePresence mode='popLayout'>
            {logs.length > 0 ? (
                logs.map((log, i) => (
                    <motion.div 
                        key={log.timestamp + i}
                        initial={{ opacity: 0, scale: 0.95, filter: "blur(5px)" }}
                        animate={{ opacity: 1, scale: 1, filter: "blur(0.01px)" }}
                        transition={{ duration: 0.4, type: "tween" }}
                        className={`flex flex-col gap-1 pl-3 py-1 relative border-l ${log.tag === 'ARCHITECT_SUCCESS' ? 'border-cyan-400 bg-cyan-400/5' : 'border-cyan-500/0'}`}
                    >
                        {/* Static sharp line from the image */}
                        <div className="absolute left-[-2px] inset-y-0 w-[3px] bg-cyan-400 shadow-[0_0_10px_cyan]" />
                        
                        <div className="flex justify-between items-center">
                            <span className={`text-[8px] font-black tracking-widest uppercase ${log.tag === 'ARCHITECT_SUCCESS' ? 'text-white' : 'text-white'}`}>{log.tag}</span>
                            <span className="text-[6px] text-cyan-500/80 font-mono tracking-widest pl-2">
                                {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                        <p className="text-[7px] text-cyan-200/50 leading-tight font-mono lowercase">
                            {log.details}
                        </p>
                    </motion.div>
                ))
            ) : (
                <div className="text-center py-4 opacity-20 text-[7px] uppercase tracking-widest">
                   No Mission Data Recorded
                </div>
            )}
         </AnimatePresence>
      </div>

      {/* 📊 MISSION_EFFICIENCY_METRIC */}
      <div className="mt-1 pt-1.5 border-t border-cyan-500/20 flex flex-col gap-1">
         <div className="flex justify-between text-[6px] text-white/50 uppercase tracking-tighter">
            <span>COGNITIVE_LOAD</span>
            <span>{logs.length > 5 ? "88%" : "12%"}</span>
         </div>
         <div className="h-[2px] w-full bg-white/5 overflow-hidden">
            <motion.div 
                initial={{ width: 0 }}
                animate={{ width: logs.length > 5 ? "88%" : "12%" }}
                className="h-full bg-cyan-500/60"
            />
         </div>
      </div>
    </motion.div>
  );
}
