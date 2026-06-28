import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/services/api";

const TacticalSight = ({ onClose }) => {
    const [analysis, setAnalysis] = useState("INITIALIZING_TACTICAL_SCAN...");
    const [isScanning, setIsScanning] = useState(true);

    useEffect(() => {
        const performScan = async () => {
            try {
                // Trigger backend to capture and analyze screen
                const res = await api.postVisionFocalPlane();
                setAnalysis(res.data.response);
                setIsScanning(false);
            } catch {
                setAnalysis("NEURAL_LINK_FAILURE: Could not establish visual focal plane.");
                setIsScanning(false);
            }
        };

        const timer = setTimeout(performScan, 2000); // Wait for the scan animation
        return () => clearTimeout(timer);
    }, []);

    return (
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-2000 bg-cyan-500/5 backdrop-blur-[2px] pointer-events-none"
        >
            {/* 📏 SCAN_LINE */}
            {isScanning && (
                <motion.div 
                    initial={{ top: "0%" }}
                    animate={{ top: "100%" }}
                    transition={{ duration: 2, ease: "linear", repeat: Infinity }}
                    className="absolute left-0 right-0 h-[2px] bg-cyan-400 shadow-[0_0_20px_#00f0ff] z-10"
                />
            )}

            {/* 🎯 FOCAL_POINTS */}
            <div className="absolute top-1/4 left-1/4 w-12 h-12 border border-cyan-500/40 rounded-full animate-ping" />
            <div className="absolute top-2/3 left-1/2 w-16 h-16 border border-cyan-500/40 rounded-full animate-pulse" />
            <div className="absolute top-1/3 left-3/4 w-8 h-8 border border-cyan-500/40 rounded-full animate-ping" />

            {/* 📟 TACTICAL_TERMINAL */}
            <motion.div 
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="absolute bottom-12 left-1/2 -translate-x-1/2 w-[600px] glass-panel p-8 border border-cyan-500/30 bg-black/90 pointer-events-auto"
            >
                <div className="flex flex-col gap-4">
                    <div className="flex justify-between items-center">
                        <span className="text-[10px] font-black tracking-[0.4em] text-cyan-400 uppercase">Neural_Sight // Focal_Plane_Analysis</span>
                        <div className="flex gap-1">
                            <div className="w-1 h-1 bg-cyan-500 animate-pulse" />
                            <div className="w-1 h-1 bg-cyan-500 animate-pulse delay-75" />
                            <div className="w-1 h-1 bg-cyan-500 animate-pulse delay-150" />
                        </div>
                    </div>
                    
                    <div className="h-px bg-cyan-500/20" />
                    
                    <p className="text-white font-mono text-xs leading-relaxed tracking-wider italic">
                        {analysis}
                    </p>

                    <button 
                        onClick={onClose}
                        className="mt-4 py-2 border border-white/10 hover:border-cyan-500/50 text-[8px] text-white/40 uppercase tracking-[0.6em] transition-all"
                    >
                        DISENGAGE_TACTICAL_SIGHT
                    </button>
                </div>
            </motion.div>

            {/* Grid Overlay */}
            <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#00f0ff 0.5px, transparent 0.5px)', backgroundSize: '20px 20px' }} />
        </motion.div>
    );
};

export default TacticalSight;
