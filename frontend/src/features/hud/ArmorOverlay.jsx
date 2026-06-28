import React from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function ArmorOverlay({ active, mode }) {
  if (!active && mode !== "combat") return null;

  return (
    <AnimatePresence>
      {(active || mode === "combat") && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 pointer-events-none z-[100] overflow-hidden"
        >
          {/* 🛡️ Peripheral Scanning HUD (Red Alert) */}
          <div className="absolute inset-0 border-[20px] border-red-500/10 blur-[2px]" />
          <div className="absolute inset-0 border-[2px] border-red-500/5 shadow-[inset_0_0_100px_rgba(255,0,0,0.1)]" />

          {/* 📐 Tactical Grid Lines */}
          <div 
            className="absolute inset-0 opacity-10"
            style={{ 
                backgroundImage: `linear-gradient(rgba(255, 0, 0, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 0, 0, 0.3) 1px, transparent 1px)`,
                backgroundSize: '40px 40px'
            }}
          />

          {/* 📡 Peripheral Status Indicators */}
          <motion.div 
            animate={{ x: [0, 10, 0], opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute top-1/4 left-10 text-[10px] text-red-500 font-mono space-y-2"
          >
            <div>ARMOR_INTEGRITY: 100%</div>
            <div>STARK_OS_V_XI: ACTIVE</div>
            <div>TACTICAL_SYNC: HIGH</div>
          </motion.div>

          <motion.div 
            animate={{ x: [0, -10, 0], opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 2, repeat: Infinity, delay: 1 }}
            className="absolute bottom-1/4 right-10 text-[10px] text-red-500 font-mono text-right space-y-2"
          >
            <div>THREAT_LEVEL: ELEVATED</div>
            <div>SECTOR_SCAN: IND_04</div>
            <div>WEAPON_SYSTEMS: STANDBY</div>
          </motion.div>

          {/* 🎯 Targeting Reticles (Dynamic) */}
          <motion.div 
            animate={{ rotate: 360, scale: [1, 1.1, 1] }}
            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-red-500/5 rounded-full"
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
