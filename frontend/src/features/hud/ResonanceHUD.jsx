import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/services/api";

const ResonanceHUD = ({ onClose, onOptimize }) => {
    const [vitals, setVitals] = useState(null);
    const [history, setHistory] = useState({ cpu: [], ram: [] });

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const res = await api.getResonanceVitals();
                const data = res.data || {};
                setVitals(data);
                
                // 🛡️ O.M.E.G.A. TIER_4: SANITIZE_RESONANCE_DATA
                const sanitize = (val) => {
                    if (typeof val === 'number') return val;
                    if (typeof val === 'string') {
                        const parsed = parseFloat(val.replace(/[^\d.-]/g, ''));
                        return isNaN(parsed) ? 0 : parsed;
                    }
                    return 0;
                };

                const cpu = sanitize(data.cpu_load);
                const ram = sanitize(data.ram_load);
                
                setHistory(prev => ({
                    cpu: [...prev.cpu, cpu].slice(-30),
                    ram: [...prev.ram, ram].slice(-30)
                }));
            } catch (e) {
                console.error("RESONANCE_SCAN_FAILURE:", e.message);
            }
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    const renderGraph = (data, color) => {
        if (data.length < 2) return null;
        const width = 300;
        const height = 60;
        const points = data.map((v, i) => `${(i / (data.length - 1)) * width},${height - (v / 100) * height}`).join(" ");

        return (
            <svg width={width} height={height} className="overflow-visible">
                <motion.polyline
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                    points={points}
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    className="drop-shadow-[0_0_8px_rgba(0,240,255,0.5)]"
                />
            </svg>
        );
    };

    return (
        <motion.div 
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className="fixed right-8 top-1/2 -translate-y-1/2 z-1000 w-[400px] flex flex-col gap-6"
        >
            <div className="glass-panel p-8 border border-cyan-500/20 bg-black/80 backdrop-blur-2xl relative">
                {/* 📐 STARK_GEOMETRY */}
                <div className="absolute top-0 right-0 w-8 h-px bg-cyan-500" />
                <div className="absolute top-0 right-0 w-px h-8 bg-cyan-500" />
                
                <div className="flex flex-col gap-1 mb-8">
                    <h2 className="text-2xl font-black tracking-[0.4em] text-white uppercase italic">System_Resonance</h2>
                    <span className="text-[8px] font-mono text-cyan-500/50 uppercase tracking-[0.6em]">Tier_4 // Primary_PC_Nexus</span>
                </div>

                <div className="flex flex-col gap-8">
                    {/* CPU SECTOR */}
                    <div className="flex flex-col gap-2">
                        <div className="flex justify-between items-end">
                            <span className="text-[10px] text-cyan-400 font-black tracking-widest uppercase">CPU_CORE_LOAD</span>
                            <span className="text-xl font-mono text-white">{vitals?.cpu_load || "0%"}</span>
                        </div>
                        <div className="h-16 bg-cyan-500/5 border border-cyan-500/10 flex items-center justify-center">
                            {renderGraph(history.cpu, "#00f0ff")}
                        </div>
                    </div>

                    {/* RAM SECTOR */}
                    <div className="flex flex-col gap-2">
                        <div className="flex justify-between items-end">
                            <span className="text-[10px] text-purple-400 font-black tracking-widest uppercase">MEM_PRESSURE</span>
                            <span className="text-xl font-mono text-white">{vitals?.ram_load || "0%"}</span>
                        </div>
                        <div className="h-16 bg-purple-500/5 border border-purple-500/10 flex items-center justify-center">
                            {renderGraph(history.ram, "#a855f7")}
                        </div>
                    </div>

                    {/* PROCESS TACTICAL MAP */}
                    <div className="flex flex-col gap-4">
                        <span className="text-[9px] text-cyan-500/60 uppercase tracking-[0.3em] font-black">Top_Active_Threads:</span>
                        <div className="flex flex-col gap-2">
                            {vitals?.tasks?.map((t, i) => (
                                <div key={i} className="flex items-center justify-between text-[10px] font-mono p-2 bg-white/5 border border-white/5 group hover:border-cyan-500/30 transition-all">
                                    <span className="truncate w-32">{t.name}</span>
                                    <span className="text-cyan-400">{t.cpu}</span>
                                    <span className="text-white/40">{t.ram}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* OPTIMIZATION_NODE */}
                    <button 
                        onClick={onOptimize}
                        className="w-full py-4 mt-4 border border-cyan-500/40 bg-cyan-500/10 text-cyan-400 font-black tracking-[0.3em] text-[9px] uppercase hover:bg-cyan-500 hover:text-black transition-all shadow-[0_0_15px_rgba(0,240,255,0.1)]"
                    >
                        Auto_Optimize_Environment
                    </button>
                    
                    <button 
                        onClick={onClose}
                        className="w-full py-2 text-[8px] text-white/20 uppercase tracking-[0.5em] hover:text-white/40 transition-colors"
                    >
                        Minimize_Dashboard
                    </button>
                </div>

                {/* Network Telemetry */}
                <div className="absolute -bottom-8 left-0 right-0 flex justify-between px-4 text-[8px] font-mono text-cyan-500/40 uppercase">
                    <span>NET_SENT: {vitals?.network?.sent || "0MB"}</span>
                    <span>NET_RECV: {vitals?.network?.recv || "0MB"}</span>
                </div>
            </div>
        </motion.div>
    );
};

export default ResonanceHUD;
