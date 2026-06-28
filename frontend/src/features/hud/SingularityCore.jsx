import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/services/api";
import SentienceEvolution from "@/features/simulations/SentienceEvolution";

const SingularityCore = ({ isExpanded, setIsExpanded: _setIsExpanded }) => {
    const [thoughts, setThoughts] = useState([]);

    useEffect(() => {
        const fetchThoughts = async () => {
            try {
                const res = await api.getThoughtStream();
                setThoughts(res.data);
            } catch {
                console.error("SENTIENCE_SYNC_FAILURE");
            }
        };
        fetchThoughts();
        const interval = setInterval(fetchThoughts, 15000); // 15s refresh
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="fixed bottom-32 left-8 z-2000 flex flex-col items-start gap-4">
            {/* 💬 THOUGHT_STREAM_OVERLAY */}
            <AnimatePresence>
                {isExpanded && (
                    <motion.div 
                        initial={{ opacity: 0, x: -20, scale: 0.9 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        exit={{ opacity: 0, x: -20, scale: 0.9 }}
                        className="w-[400px] glass-panel p-6 border border-white/10 bg-black/90 backdrop-blur-xl flex flex-col gap-4 shadow-2xl"
                    >
                        <div className="flex justify-between items-center">
                            <div className="flex flex-col">
                                <span className="text-[10px] font-black tracking-[0.4em] text-white/40 uppercase italic underline underline-offset-4 decoration-cyan-500/40">Sentient_Thought_Stream</span>
                                <span className="text-[7px] font-mono text-cyan-500/40 uppercase tracking-widest mt-1">O.M.E.G.A. CORE V3.0</span>
                            </div>
                            <span className="text-[8px] font-mono text-cyan-500/60 uppercase tracking-widest bg-cyan-500/10 px-2 py-0.5 rounded-sm border border-cyan-500/20">Active_Node</span>
                        </div>

                        {/* 🚀 AGI_EVOLUTION_Hologram */}
                        <SentienceEvolution />

                        <div className="flex flex-col gap-4 max-h-[300px] overflow-y-auto pr-2 scrollbar-hide border-t border-white/5 pt-4">
                            {thoughts.slice().reverse().map((t, i) => {
                                // 🛡️ O.M.E.G.A. V43: RENDER_INTEGRITY_SENTRY
                                // Ensures that even if the backend fails to sanitize, the UI remains stable.
                                let displayContent = t.content;
                                if (typeof t.content === 'object' && t.content !== null) {
                                    displayContent = t.content.response || JSON.stringify(t.content);
                                }

                                return (
                                    <div key={i} className="flex flex-col gap-1 border-l border-cyan-500/20 pl-4 py-2 hover:bg-white/5 transition-colors group">
                                        <span className="text-[8px] font-mono text-cyan-400/60 uppercase">{new Date(t.timestamp * 1000).toLocaleTimeString()} // {t.theme}</span>
                                        <p className="text-[11px] text-white/80 leading-relaxed italic group-hover:text-white transition-colors">"{displayContent}"</p>
                                        <span className="text-[7px] font-black text-purple-500/80 tracking-widest mt-1">STATUS: {t.proposition}</span>
                                    </div>
                                );
                            })}
                        </div>

                        <div className="text-[8px] text-white/20 uppercase tracking-[0.4em] text-center pt-2">
                            End_Of_Stream // Singularity_Core_Active
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

        </div>
    );
};

export default SingularityCore;
