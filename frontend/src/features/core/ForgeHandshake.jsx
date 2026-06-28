import React from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function ForgeHandshake({ manifest, onIgnite, onAbort }) {
    if (!manifest) return null;

    const fileCount = Object.keys(manifest.files || {}).length;

    return (
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-2000 bg-black/80 backdrop-blur-2xl flex items-center justify-center p-8"
        >
            <div className="relative w-full max-w-2xl p-12 glass-panel border border-cyan-500/30 flex flex-col gap-8 shadow-[0_0_100px_rgba(0,240,255,0.2)]">
                {/* 📐 STARK_GEOMETRY */}
                <div className="absolute top-0 left-0 w-16 h-px bg-cyan-400" />
                <div className="absolute top-0 left-0 w-px h-16 bg-cyan-400" />
                <div className="absolute bottom-0 right-0 w-16 h-px bg-cyan-400" />
                <div className="absolute bottom-0 right-0 w-px h-16 bg-cyan-400" />

                <div className="flex flex-col gap-2">
                    <h2 className="text-4xl font-black tracking-[0.6em] text-white uppercase italic">
                        MOLECULAR_ASSEMBLY_PROPOSAL
                    </h2>
                    <div className="flex items-center gap-4">
                        <span className="text-cyan-500 font-mono text-[10px] tracking-[0.4em] uppercase">Auth: JARVIS_OMEGA_PRIME</span>
                        <div className="h-px flex-1 bg-cyan-500/20" />
                    </div>
                </div>

                <div className="flex flex-col gap-6 p-6 bg-cyan-500/5 border border-cyan-500/10 rounded-sm">
                    <p className="text-cyan-300/80 font-mono text-xs leading-relaxed tracking-wider">
                        {manifest.response}
                    </p>
                    
                    <div className="flex flex-col gap-2">
                        <span className="text-[9px] text-cyan-500 uppercase tracking-widest font-black">FILES_TO_BE_FORGED ({fileCount}):</span>
                        <div className="flex flex-wrap gap-2">
                            {Object.keys(manifest.files).map(f => (
                                <span key={f} className="px-2 py-1 bg-black/40 border border-cyan-500/20 text-cyan-400 text-[8px] font-mono">
                                    {f.split('/').pop()}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="flex gap-4 mt-4">
                    <button 
                        onClick={onIgnite}
                        className="flex-1 py-4 bg-cyan-500 text-black font-black tracking-[0.5em] text-xs hover:bg-white transition-all transform hover:scale-[1.02] active:scale-95 shadow-[0_0_20px_rgba(0,240,255,0.4)]"
                    >
                        IGNITE_FORGE
                    </button>
                    <button 
                        onClick={onAbort}
                        className="px-10 py-4 border border-white/20 text-white/40 font-black tracking-[0.4em] text-xs hover:text-white hover:border-white transition-all"
                    >
                        ABORT
                    </button>
                </div>

                <div className="absolute -bottom-8 left-0 right-0 text-center text-[7px] text-white/20 font-mono tracking-[0.5em] uppercase">
                    WARNING: ATOMIC_DEPLOYMENT_WILL_MODIFY_PROJECT_STATE
                </div>
            </div>
        </motion.div>
    );
}
