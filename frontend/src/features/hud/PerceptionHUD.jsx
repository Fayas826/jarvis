import React from 'react';
import { motion } from 'framer-motion';

/**
 * 🧿 O.M.E.G.A. TIER_4: PERCEPTION_HUD
 * Visualizing the autonomous visual cortex insights.
 */
const PerceptionHUD = ({ insight }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      className="fixed top-24 right-8 w-80 z-[301] pointer-events-none"
    >
      <div className="relative p-4 bg-black/60 border-l-4 border-cyan-500/50 backdrop-blur-md rounded-r-lg">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="text-[10px] font-mono text-cyan-400 tracking-[0.2em] uppercase">Autonomous_Perception</span>
        </div>
        
        <p className="text-[11px] font-mono text-white/80 leading-relaxed italic">
          "{insight}"
        </p>

        {/* 📉 SCAN_LINE_DECORATION */}
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-cyan-500 to-transparent opacity-20" />
        <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-cyan-500 to-transparent opacity-20" />
        
        {/* 🧬 DATA_STREAM_PARTICLES */}
        <div className="mt-3 flex gap-1">
          {[1,2,3,4,5].map(i => (
            <div key={i} className="w-1 h-1 bg-cyan-400/20" />
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default PerceptionHUD;
