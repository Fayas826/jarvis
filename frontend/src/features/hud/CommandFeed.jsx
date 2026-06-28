import React, { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function CommandFeed({ logs, status: _status = "idle", threatLevel: _threatLevel = "NOMINAL" }) {
  const scrollRef = useRef();
  const [jitter, setJitter] = useState({ x: 0, y: 0 });
  const [isImpact, setIsImpact] = useState(false);

  // 🧠 NEURAL TWITCH: MICROSCOPIC JITTER ON LOG INTAKE (SENTIENCE 10/10)
  useEffect(() => {
    if (logs.length > 0) {
      // 1. NEURAL TWITCH (±0.4px - SUBTLE & PHYSICAL)
      const effectSeed = Math.sin(logs.length * 91.37) * 10000;
      const normalized = effectSeed - Math.floor(effectSeed);
      const kickoffTimer = setTimeout(() => {
        setJitter({ x: (normalized - 0.5) * 0.8, y: ((1 - normalized) - 0.5) * 0.8 });
        setIsImpact(true);
      }, 0);
      const impactTimer = setTimeout(() => setIsImpact(false), 30); 
      
      const jitterTimer = setTimeout(() => setJitter({ x: 0, y: 0 }), 200); 
      return () => {
        clearTimeout(kickoffTimer);
        clearTimeout(impactTimer);
        clearTimeout(jitterTimer);
      };
    }
  }, [logs.length]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  // 🚨 TACTICAL COLOR MAPPING (THE SIGNATURE PROTOCOL - XXXIX PARITY)
  const getLogStyle = (text) => {
    const isCritical = /CRITICAL|FAILURE|THREAT|COMBAT/i.test(text);
    const isWarning = /WARNING|OVERLOAD|SYNC|ALERT/i.test(text);
    
    if (isCritical) return "text-red-500 border-red-500/30 bg-red-500/10 shadow-[0_0_30px_rgba(255,0,0,0.3)]";
    if (isWarning) return "text-amber-400 border-amber-500/30 bg-amber-500/10 shadow-[0_0_20px_rgba(255,185,0,0.2)]";
    return "text-cyan-400 border-cyan-500/20 bg-cyan-500/5 shadow-[inset_0_0_10px_rgba(0,240,255,0.02)]";
  };

  return (
    <motion.div 
      animate={{ 
          x: jitter.x, y: jitter.y,
          // ⚖️ O.M.E.G.A. XXIV: TACTICAL WEIGHT SPIKE (1.01 SCALE POP)
          scale: isImpact ? 1.01 : 1, 
          filter: isImpact ? "brightness(1.6) contrast(1.2) drop-shadow(0 0 15px rgba(0,240,255,0.4))" : "brightness(1) contrast(1)"
      }}
      className="absolute top-[-140px] w-full flex justify-center pointer-events-none transition-all duration-75"
    >
      <div 
        ref={scrollRef}
        style={{ maskImage: "linear-gradient(to top, black 80%, transparent 100%)" }}
        className="max-h-24 overflow-y-hidden flex flex-col items-center gap-2 opacity-65 hover:opacity-100 transition-opacity duration-1000"
      >
        <AnimatePresence initial={false}>
          {logs.slice(-3).map((log, i) => (
            <motion.div
              key={i + log}
              initial={{ opacity: 0, y: 15, filter: "blur(5px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0.01px)" }}
              exit={{ opacity: 0, y: -15, filter: "blur(5px)" }}
              transition={{ 
                opacity: { duration: 0.2 },
                y: { type: "spring", damping: 40, stiffness: 500 },
                filter: { type: "tween", duration: 0.3 }
              }}
              className={`text-[9px] font-mono tracking-[0.4em] uppercase px-6 py-2 rounded-sm border backdrop-blur-md whitespace-nowrap transition-all duration-200 ${getLogStyle(log)}`}
            >
              <span className="opacity-30 mr-4">[{new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}]</span>
              <span className="opacity-50 mr-2">{">"}</span>
              {log}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
