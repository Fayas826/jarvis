import React from "react";
import { motion, AnimatePresence } from "framer-motion";

const ForesightNode = ({ node, onClick }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.05, backgroundColor: "rgba(0, 240, 255, 0.1)" }}
      whileTap={{ scale: 0.95 }}
      onClick={() => onClick(node.intent)}
      className="stark-glass px-4 py-2 flex items-center gap-3 border border-cyan-500/10 hover:border-cyan-400 group transition-all duration-300 pointer-events-auto"
    >
      {/* 🔮 CORE_RESONANCE_SCANNER */}
      <div className="relative w-2 h-2">
         <div className="absolute inset-0 bg-cyan-400/20 rounded-full animate-ping" />
         <div className="absolute inset-0 bg-cyan-500 rounded-full shadow-[0_0_8px_cyan]" />
      </div>

      <div className="flex flex-col items-start translate-y-[-1px]">
        <span className="text-[7px] font-mono text-cyan-400/40 tracking-[0.3em] font-black group-hover:text-cyan-400">FORESIGHT_NODE</span>
        <span className="text-[9px] font-mono text-white/60 tracking-widest uppercase group-hover:text-white transition-colors">{node.label}</span>
      </div>
    </motion.button>
  );
};

export default function ForesightHUD({ predictions = [], onAction }) {
  if (!predictions || predictions.length === 0) return null;

  return (
    <div className="fixed left-1/2 -translate-x-1/2 top-[120px] flex gap-4 z-[300] pointer-events-none">
      <AnimatePresence mode="popLayout">
        {predictions.map((node, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: -20, filter: "blur(10px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0.01px)" }}
            exit={{ opacity: 0, scale: 0.8, filter: "blur(20px)" }}
            transition={{ duration: 0.8, delay: idx * 0.2 }}
          >
            <ForesightNode node={node} onClick={onAction} />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
