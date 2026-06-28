import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/services/api";

const NexusHUD = ({ onClose }) => {
    const [intel, setIntel] = useState(null);

    useEffect(() => {
        const fetchIntel = async () => {
            try {
                const res = await api.getNexusIntel();
                setIntel(res.data);
            } catch {
                console.error("NEXUS_SYNC_FAILURE");
            }
        };
        fetchIntel();
        const interval = setInterval(fetchIntel, 30000); // 30s refresh
        return () => clearInterval(interval);
    }, []);

    const syncCode = ((intel?.news?.length ?? 0) * 157 + (intel?.nexus_insights?.length ?? 0) * 23 + 256)
        .toString(16)
        .toUpperCase();

    return (
        <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-0 z-1500 flex items-center justify-center bg-black/80 backdrop-blur-2xl p-20"
        >
            <div className="relative w-full max-w-6xl h-full glass-panel border border-cyan-500/20 p-12 flex flex-col gap-12 overflow-hidden shadow-[0_0_100px_rgba(0,240,255,0.1)]">
                {/* 📐 STARK_GEOMETRY */}
                <div className="absolute top-0 left-0 w-32 h-px bg-cyan-500/50" />
                <div className="absolute top-0 left-0 w-px h-32 bg-cyan-500/50" />
                
                {/* 🏹 HEADER_TACTICAL */}
                <div className="flex justify-between items-start">
                    <div className="flex flex-col gap-2">
                        <h2 className="text-5xl font-black tracking-[0.5em] text-white uppercase italic">Nexus_Command</h2>
                        <div className="flex items-center gap-4">
                            <span className="text-cyan-500 font-mono text-[10px] tracking-[0.6em] uppercase underline decoration-cyan-500/30 underline-offset-8">Global_Intel_Nexus // Tier_9</span>
                            <div className="h-px w-32 bg-cyan-500/20" />
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-xs font-mono text-cyan-500/60 mb-1">GLOBAL_THREAT_LEVEL</div>
                        <div className={`text-2xl font-black tracking-widest ${intel?.threat_level === 'NOMINAL' ? 'text-green-500' : 'text-red-500'} uppercase italic`}>
                            {intel?.threat_level || "SCANNING..."}
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-3 gap-12 flex-1 min-h-0">
                    {/* NEWS_COLLECTIVE */}
                    <div className="col-span-2 flex flex-col gap-6 overflow-hidden">
                        <span className="text-[10px] font-black tracking-[0.4em] text-white/40 uppercase">Broadcast_Nodes // Global_Stream</span>
                        <div className="flex flex-col gap-4 overflow-y-auto pr-4 scrollbar-hide">
                            {intel?.news?.map((n, i) => (
                                <a 
                                    key={i} 
                                    href={n.link} 
                                    target="_blank" 
                                    rel="noreferrer"
                                    className="p-6 bg-white/5 border border-white/5 hover:border-cyan-500/40 hover:bg-cyan-500/5 transition-all group flex flex-col gap-2"
                                >
                                    <div className="flex justify-between items-center text-[8px] font-mono text-cyan-500/60 uppercase tracking-widest">
                                        <span>Node: {n.source}</span>
                                        <span className="opacity-0 group-hover:opacity-100 transition-opacity">Launch_Link ↗</span>
                                    </div>
                                    <p className="text-lg font-black tracking-wide leading-tight text-white group-hover:text-cyan-400 transition-colors">{n.title}</p>
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* MARKET_RESONANCE */}
                    <div className="flex flex-col gap-8">
                        <div className="flex flex-col gap-4">
                            <span className="text-[10px] font-black tracking-[0.4em] text-white/40 uppercase">Market_Resonance</span>
                            <div className="p-8 bg-cyan-500/10 border border-cyan-500/20 rounded-sm flex flex-col gap-6">
                                <div className="flex justify-between items-end">
                                    <span className="text-[9px] font-mono text-cyan-400 uppercase">Sentiment</span>
                                    <span className={`text-2xl font-black italic tracking-widest ${intel?.markets?.sentiment === 'BULLISH' ? 'text-green-400' : 'text-red-400'}`}>
                                        {intel?.markets?.sentiment || "SYNCING"}
                                    </span>
                                </div>
                                <div className="h-px bg-cyan-500/20" />
                                <div className="grid grid-cols-2 gap-4">
                                    {intel?.markets?.prices && Object.entries(intel.markets.prices).map(([key, val]) => (
                                        <div key={key} className="flex flex-col">
                                            <span className="text-[10px] font-mono text-white/40">{key}/USD</span>
                                            <span className="text-lg font-black tracking-widest text-white">{val}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* 🌌 TIER_9: NEXUS_RESONANCE_DATA */}
                        <div className="flex flex-col gap-4 flex-1">
                            <span className="text-[10px] font-black tracking-[0.4em] text-white/40 uppercase">Nexus_Global_Insights</span>
                            <div className="flex-1 flex flex-col gap-4 overflow-y-auto pr-2 scrollbar-hide">
                                {intel?.nexus_insights?.map((insight, idx) => (
                                    <motion.div 
                                        key={idx}
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className="p-4 border-l-2 border-cyan-500/40 bg-cyan-500/5 flex flex-col gap-1"
                                    >
                                        <div className="flex justify-between items-center">
                                            <span className="text-[8px] font-mono text-cyan-400 tracking-widest">{insight.label}</span>
                                            <span className={`text-[7px] font-mono ${insight.vector === 'POSITIVE' ? 'text-green-400' : 'text-amber-400'}`}>{insight.vector}</span>
                                        </div>
                                        <p className="text-[10px] font-mono text-white/80 leading-relaxed uppercase">{insight.details}</p>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex justify-between items-center mt-auto pt-8 border-t border-white/5">
                    <div className="flex gap-12">
                        <div className="flex flex-col">
                            <span className="text-[10px] font-mono text-white/20 uppercase tracking-widest">Uplink_Status</span>
                            <span className="text-sm font-black text-cyan-500 tracking-widest uppercase italic">OMNICORE_SECURE</span>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-[10px] font-mono text-white/20 uppercase tracking-widest">Neural_Efficiency</span>
                            <span className="text-sm font-black text-white tracking-widest uppercase italic">99.8%_DEEP_SYNC</span>
                        </div>
                    </div>
                    <button 
                        onClick={onClose}
                        className="stark-button px-12 py-4 bg-white/5 border border-white/10 hover:bg-cyan-500 hover:text-black transition-all font-black tracking-[0.4em] uppercase italic text-sm"
                    >
                        Close_Nexus_Link
                    </button>
                </div>

                {/* 🛡️ LIVE_INTELLIGENCE_TICKER */}
                <div className="absolute bottom-0 left-0 right-0 h-16 bg-cyan-500/10 border-t border-cyan-500/20 flex items-center overflow-hidden">
                    <div className="w-24 h-full bg-cyan-600/20 flex items-center justify-center border-r border-cyan-500/30 z-10 backdrop-blur-xl">
                        <span className="text-[9px] font-black tracking-widest text-white italic">LIVE_FEED</span>
                    </div>
                    <div className="flex-1 overflow-hidden whitespace-nowrap relative">
                        <motion.div 
                            animate={{ x: ["100%", "-200%"] }}
                            transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
                            className="flex gap-16 items-center"
                        >
                            {intel?.news?.map((n, i) => (
                                <div key={i} className="flex gap-4 items-center">
                                    <span className="text-cyan-400 font-mono text-[9px] font-black">[{n.source}]</span>
                                    <span className="text-white font-mono text-[10px] tracking-wide uppercase">{n.title}</span>
                                    <span className="text-white/20">///</span>
                                </div>
                            ))}
                            {/* Duplicate for seamless loop if content is short */}
                            {intel?.news?.map((n, i) => (
                                <div key={`loop-${i}`} className="flex gap-4 items-center">
                                    <span className="text-cyan-400 font-mono text-[9px] font-black">[{n.source}]</span>
                                    <span className="text-white font-mono text-[10px] tracking-wide uppercase">{n.title}</span>
                                    <span className="text-white/20">///</span>
                                </div>
                            ))}
                        </motion.div>
                    </div>
                    <div className="px-8 h-full flex items-center bg-cyan-600/10 font-mono text-[8px] text-cyan-500/60 uppercase tracking-widest">
                        RES_SYNC: 0x{syncCode}
                    </div>
                </div>

                <button 
                    onClick={onClose}
                    className="absolute top-12 right-12 w-10 h-10 border border-white/10 flex items-center justify-center hover:bg-red-500/20 hover:border-red-500/40 transition-all text-white/40 hover:text-red-500"
                >
                    ✕
                </button>
            </div>
        </motion.div>
    );
};

export default NexusHUD;
