import React from "react";
import { motion } from "framer-motion";

export default function NewsTicker({ news }) {
  if (!news || news.length === 0) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-0 left-0 right-0 z-[100] h-10 bg-black/60 backdrop-blur-xl border-t flex items-center overflow-hidden transition-colors duration-1000"
      style={{ borderColor: 'rgba(var(--stark-glow-rgb), 0.2)' }}
    >
      {/* Breaking Signal Label */}
      <div 
        className="h-full flex items-center px-6 border-r gap-3 transition-colors duration-1000"
        style={{ backgroundColor: 'rgba(var(--stark-glow-rgb), 0.1)', borderColor: 'rgba(var(--stark-glow-rgb), 0.2)' }}
      >
         <div 
            className="w-2 h-2 rounded-full animate-pulse shadow-[0_0_5px_var(--stark-glow)] transition-colors duration-1000" 
            style={{ backgroundColor: 'var(--stark-glow)' }}
         />
         <span 
            className="text-[10px] font-black tracking-[0.3em] uppercase whitespace-nowrap transition-colors duration-1000"
            style={{ color: 'var(--stark-glow)' }}
         >
            Signal_Intercepted
         </span>
      </div>

      {/* The Scrolling Feed */}
      <div className="flex-1 relative h-full flex items-center overflow-hidden">
        <motion.div 
          animate={{ x: [0, -2000] }}
          transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
          className="flex gap-24 items-center whitespace-nowrap"
        >
          {news.map((item, i) => (
            <div key={i} className="flex items-center gap-4">
              <span className="text-[8px] text-cyan-600/60 font-mono tracking-tighter uppercase whitespace-nowrap">
                Source_BBC_Tech_INTEL:
              </span>
              <a 
                href={item.link} 
                target="_blank" 
                rel="noreferrer"
                className="text-[11px] font-bold text-cyan-200/80 hover:text-cyan-400 uppercase tracking-widest transition-colors"
              >
                {item.title}
              </a>
              <div className="w-1 h-1 bg-cyan-500/30 rounded-full" />
            </div>
          ))}
          {/* Duplicate for seamless loop */}
          {news.map((item, i) => (
            <div key={`dup-${i}`} className="flex items-center gap-4">
              <span className="text-[8px] text-cyan-600/60 font-mono tracking-tighter uppercase whitespace-nowrap">
                Source_BBC_Tech_INTEL:
              </span>
              <span className="text-[11px] font-bold text-cyan-200/80 uppercase tracking-widest">
                {item.title}
              </span>
              <div className="w-1 h-1 bg-cyan-500/30 rounded-full" />
            </div>
          ))}
        </motion.div>
      </div>

      {/* Satellite Sync Info */}
      <div className="bg-black/40 h-full flex items-center px-6 border-l border-cyan-500/10 gap-3 font-mono text-[8px] text-cyan-600/60 uppercase tracking-[0.2em]">
         <span className="animate-pulse">Link_Stable</span>
         <span>|</span>
         <span>{new Date().toLocaleTimeString()}</span>
      </div>
    </motion.div>
  );
}
