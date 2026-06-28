import React, { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";

const seededValue = (index, seed = 47) => {
  const value = Math.sin(index * 73.51 + seed) * 10000;
  return value - Math.floor(value);
};

export default function DiagnosticHUD({ data, onComplete }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [complete, setComplete] = useState(false);
  const matrixColumns = useMemo(() => {
    return Array.from({ length: 48 }, (_, i) => ({
      duration: 3 + seededValue(i, 5) * 4,
      rows: Array.from({ length: 40 }, (_, j) =>
        seededValue(i * 40 + j, 11).toString(16).slice(2, 10).toUpperCase()
      ),
    }));
  }, []);
  const sessionId = useMemo(
    () => seededValue((data?.length ?? 0) + 1, 17).toString(36).slice(2, 9).toUpperCase(),
    [data]
  );

  useEffect(() => {
    if (!data) return;
    
    let completeTimeout;
    let onCompleteTimeout;

    // Scan through nodes one by one
    const interval = setInterval(() => {
      setCurrentIndex(prev => {
        if (prev >= data.length - 1) {
          clearInterval(interval);
          completeTimeout = setTimeout(() => {
            setComplete(true);
            onCompleteTimeout = setTimeout(onComplete, 2500);
          }, 1000);
          return prev;
        }
        return prev + 1;
      });
    }, 400);

    return () => {
      clearInterval(interval);
      clearTimeout(completeTimeout);
      clearTimeout(onCompleteTimeout);
    };
  }, [data, onComplete]);

  if (!data) return null;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-1000 bg-black/60 backdrop-blur-[60px] flex flex-col items-center justify-center p-20 overflow-hidden"
    >
      {/* 🧬 ZENITH_SCANNING_MATRIX (PRISM-SHIFT) */}
      <div className="absolute inset-0 opacity-[0.15] pointer-events-none font-mono text-[9px] text-cyan-400 grid grid-cols-12 gap-1 overflow-hidden">
          {matrixColumns.map((column, i) => (
              <motion.div 
                  key={i}
                  animate={{ y: [-500, 1000] }}
                  transition={{ duration: column.duration, repeat: Infinity, ease: "linear" }}
                  className="whitespace-nowrap flex flex-col gap-1 border-l border-cyan-500/10 pl-2"
              >
                  {column.rows.map((row, j) => (
                      <span key={j}>{row}</span>
                  ))}
              </motion.div>
          ))}
      </div>

      {/* 💠 ZENITH_DIAGNOSTIC_CORE */}
      <div className="relative z-10 flex flex-col items-center gap-16 w-full max-w-5xl">
        <div className="flex flex-col items-center gap-8 text-center">
            <div className="relative">
                <motion.div 
                    animate={{ rotate: 360 }}
                    transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                    className="w-24 h-24 rounded-full border border-cyan-500/20 flex items-center justify-center"
                >
                    <div className="w-20 h-20 rounded-full border-2 border-cyan-400/40 border-t-cyan-400 animate-spin" />
                </motion.div>
                <div className="absolute inset-0 bg-cyan-400/5 blur-2xl animate-pulse" />
            </div>
            
            <div className="flex flex-col gap-2">
                <h2 className="text-5xl font-black tracking-[0.8em] text-cyan-400 uppercase">ZENITH_PROTOCOL</h2>
                <p className="text-[10px] text-cyan-500/60 font-mono tracking-[0.5em] uppercase">Hyper_Neural_Diagnostic_v4.2</p>
            </div>
        </div>

        {/* Node Verification Grid */}
        <div className="grid grid-cols-2 gap-x-24 gap-y-8 w-full px-20">
            {data.map((item, i) => (
                <div key={i} className={`flex flex-col gap-2 transition-all duration-500 ${i <= currentIndex ? 'opacity-100 scale-100' : 'opacity-10 scale-95'}`}>
                    <div className="flex justify-between items-center">
                        <span className="text-[11px] font-mono text-cyan-500 font-black tracking-widest uppercase">{item.module}</span>
                        <div className="flex items-center gap-3">
                            <span className={`text-[8px] font-black tracking-widest ${i <= currentIndex ? 'text-cyan-400' : 'text-white/20'}`}>
                                {i < currentIndex ? "NOMINAL" : (i === currentIndex ? "SYNCING..." : "QUEUED")}
                            </span>
                            <div className={`w-2 h-2 rounded-full ${i < currentIndex ? 'bg-cyan-400 shadow-[0_0_10px_cyan]' : (i === currentIndex ? 'bg-amber-500 animate-pulse shadow-[0_0_10px_amber]' : 'bg-white/5')}`} />
                        </div>
                    </div>
                    {item.details && i <= currentIndex && (
                        <motion.span 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-[7px] text-cyan-300/40 font-mono tracking-widest uppercase mb-1"
                        >
                            {item.details}
                        </motion.span>
                    )}
                    <div className="h-px w-full bg-cyan-500/10 relative overflow-hidden">
                        {i === currentIndex && (
                            <motion.div 
                                initial={{ x: "-100%" }}
                                animate={{ x: "200%" }}
                                transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
                                className="absolute inset-0 bg-linear-to-r from-transparent via-cyan-400 to-transparent w-1/2"
                            />
                        )}
                    </div>
                </div>
            ))}
        </div>

        {/* Final Nominal Signature */}
        <AnimatePresence>
            {complete && (
                <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center gap-8 mt-4"
                >
                    <div className="w-96 h-[2px] bg-linear-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_30px_cyan]" />
                    <div className="flex flex-col items-center gap-2">
                        <span className="text-5xl font-black tracking-[1em] text-cyan-400 animate-pulse">SYSTEM_ZENITH</span>
                        <span className="text-[8px] text-cyan-600/60 font-mono tracking-[0.5em] uppercase px-4 py-1 border border-cyan-500/20 bg-cyan-500/5">NO_ANOMALIES_DETECTED // OMEGA_LEVEL_SECURE</span>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
      </div>

      {/* Cinematic HUD Side Data */}
      <div className="absolute bottom-12 left-12 flex flex-col gap-3 font-mono text-[9px] text-cyan-600/40 uppercase tracking-[0.4em]">
         <div className="flex items-center gap-3">
            <div className="w-1 h-8 bg-cyan-500/20" />
            <div className="flex flex-col">
                <span>Diag_Type: HYPER_OS_SCAN</span>
                <span>Session: ZENITH_{sessionId}</span>
            </div>
         </div>
      </div>
    </motion.div>
  );
}
