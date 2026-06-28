import React from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function HardwareHeatMap({ data, status }) {
  if (!data || !data.cores) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.8, filter: "blur(12px)" }}
      animate={{ 
          opacity: 1, 
          scale: 1,
          filter: "blur(0.01px)",
          translateX: status === 'speaking' ? [0, 1.2, -1.2, 0] : 0,
          translateY: status === 'speaking' ? [0, -1.2, 1.2, 0] : 0
      }}
      transition={{ 
          translateX: { duration: 0.1, repeat: status === 'speaking' ? Infinity : 0 },
          translateY: { duration: 0.12, repeat: status === 'speaking' ? Infinity : 0 },
          default: { duration: 1.5, ease: "easeOut", type: "tween" }
      }}
      className="stark-widget flex flex-col gap-5 p-6 overflow-visible shadow-[0_0_50px_rgba(0,0,0,0.6)]"
      style={{ transformStyle: "preserve-3d" }}
    >
      <div className="flex flex-col gap-2 shrink-0">
          <div className="flex items-center gap-3">
              <span className="text-[10px] font-black tracking-[0.6em] text-cyan-400 uppercase">NEURAL_ZENITH_STACK</span>
              <div className="px-1.5 py-0.5 rounded-[2px] bg-cyan-500/10 border border-cyan-500/20 text-[6px] text-cyan-400 font-mono">NODE_LIVE</div>
          </div>
          <p className="text-[7px] text-cyan-500/30 font-mono tracking-widest uppercase mb-2">Synthetic Synapse Monitoring & Hardware Resonance</p>
          <div className="w-full h-[1px] bg-gradient-to-r from-cyan-500/40 to-transparent" />
      </div>

      {/* 🧬 VOLUMETRIC NEURAL STACK */}
      <div className="grid grid-cols-4 gap-6 px-2 py-4" style={{ transform: "perspective(500px) rotateX(10deg)" }}>
         {data.cores.map((load, i) => {
            const isHot = load > 75;
            const isOverheated = load > 92;
            const nodeColor = isOverheated ? "#ff0000" : (isHot ? "#ffb900" : "#00f0ff");
            
            return (
               <div key={i} className="relative group flex flex-col items-center">
                  {/* 🕯️ VOLUMETRIC GLOW CORE */}
                  <motion.div 
                     animate={{ 
                        height: [20, 20 + (load / 2), 20],
                        backgroundColor: nodeColor,
                        boxShadow: `0 0 30px ${nodeColor}44`,
                        opacity: [0.6, 1, 0.6]
                     }}
                     transition={{ duration: 2, repeat: Infinity, delay: i * 0.15 }}
                     className="w-4 rounded-t-sm relative transition-colors duration-1000"
                     style={{ 
                         transformOrigin: "bottom",
                         background: `linear-gradient(to top, ${nodeColor}22, ${nodeColor})`
                     }}
                  >
                     {/* Top Cap for 3D effect */}
                     <div className="absolute -top-1 left-0 w-full h-2 rounded-full blur-[2px]" style={{ backgroundColor: nodeColor }} />
                  </motion.div>
                  <span className="text-[5px] text-white/20 font-black font-mono mt-3">SYN_0{i+1}</span>
               </div>
            );
         })}
      </div>
      
      <div className="mt-4 flex flex-col gap-3 pt-3 border-t border-white/5 overflow-visible">
         <div className="flex justify-between items-center px-1">
            <span 
                className="text-[8px] font-black uppercase tracking-[0.4em] transition-colors duration-1000"
                style={{ color: 'rgba(var(--stark-glow-rgb), 0.7)' }}
            >
                Integrated_GPU
            </span>
            <span 
                className={`text-[10px] font-black font-mono transition-all duration-300`}
                style={{ color: data.gpu > 80 ? '#fbbf24' : 'var(--stark-glow)', opacity: data.gpu > 80 ? 1 : 0.7 }}
            >
               {Math.round(data.gpu)}%_SATURATION
            </span>
         </div>
         <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden relative shadow-[inset_0_0_5px_black]">
             <motion.div 
                 animate={{ 
                     width: `${data.gpu}%`, 
                     backgroundColor: data.gpu > 80 ? "#fbbf24" : "var(--stark-glow)",
                     boxShadow: `0 0 15px ${data.gpu > 80 ? '#fbbf24' : 'var(--stark-glow)'}`
                 }}
                 className="h-full rounded-full transition-colors duration-1000"
             />
         </div>
      </div>
    </motion.div>
  );
}
