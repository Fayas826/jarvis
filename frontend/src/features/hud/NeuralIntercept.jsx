import React, { useState, useEffect, useMemo, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

const INTENT_FRAGMENTS = [
    "NEURAL_HANDSHAKE_0x7F",
    "DECRYPTING_THOUGHT_VECTOR",
    "SYNAPTIC_FLUX_LOCKED",
    "INTENT_ANALYSIS: 98.4%",
    "GATEWAY_RESONANCE_STABLE",
    "BUFFER_LATENCY: 0.12ms",
    "DEEP_CORE_SCAN_ACTIVE",
    "RESONANCE_FEEDBACK_NULL",
    "PROTOCOL_XC_AUTHORIZED",
    "MANIFEST_TIER_10_AGI",
    "HEARTBEAT_SYNC_LOCKED",
    "UPLINK_INTEGRITY_100%",
    "DECODING_VOCAL_SIGNATURE",
    "FOCAL_PLANE_ANCHOR: SECURE",
    "RECURSIVE_RESIDUAL_NULL",
    "ZENITH_AUTH_VERIFIED",
    "INTERCEPT_VECTOR_ALPHA_9",
    "QUANTUM_ENCRYPTION_ACTIVE",
    "OMEGA_CORE_HANDSHAKE_READY"
];

const seededValue = (index, seed = 61) => {
    const value = Math.sin(index * 89.41 + seed) * 10000;
    return value - Math.floor(value);
};

export default function NeuralIntercept({ status, mode, focusValue }) {
    const [lines, setLines] = useState([]);
    const lineCounterRef = useRef(0);
    const sideStreams = useMemo(() => {
        return Array.from({ length: 30 }, (_, i) => ({
            id: i,
            text: seededValue(i, 5).toString(16).slice(2, 10).toUpperCase(),
        }));
    }, []);
    
    useEffect(() => {
        const interval = setInterval(() => {
            const newLine = {
                id: `${Date.now()}-${lineCounterRef.current++}`,
                text: INTENT_FRAGMENTS[Math.floor(seededValue(Date.now(), 7) * INTENT_FRAGMENTS.length)],
                timestamp: new Date().toLocaleTimeString('en-US', { hour12: false, fractionalSecondDigits: 2 })
            };
            setLines(prev => [newLine, ...prev].slice(0, 5));
        }, focusValue > 0.5 ? 200 : 800);
        return () => clearInterval(interval);
    }, [focusValue]);

    const isIntercepted = mode === "offline"; 
    const color = isIntercepted ? "text-red-500" : (status === "listening" ? "text-amber-400" : "text-cyan-400");

    return (
        <div className="relative w-full h-44 flex flex-col items-center justify-start overflow-hidden pointer-events-none border-y border-white/5 bg-black/20 backdrop-blur-sm">
            {/* 📺 SCANLINE_OVERLAY */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.03),rgba(0,255,0,0.01),rgba(0,0,255,0.03))] z-10 bg-[length:100%_2px,3px_100%] pointer-events-none opacity-20" />
            
            {/* ⏹️ HEX_BITSTREAM_LEFT */}
            <div className="absolute left-4 top-0 bottom-0 w-16 flex flex-col gap-0.5 opacity-20 pointer-events-none overflow-hidden pt-2">
                {sideStreams.map((stream, i) => (
                    <motion.span 
                        key={stream.id} 
                        animate={{ opacity: focusValue > 0.5 ? [0.4, 1, 0.4] : [0.1, 0.4, 0.1] }}
                        transition={{ duration: focusValue > 0.5 ? 0.3 : 2, repeat: Infinity, delay: i * 0.05 }}
                        className="font-mono text-[7px] text-white/50"
                    >
                        {stream.text}
                    </motion.span>
                ))}
            </div>

            {/* ⏹️ HEX_BITSTREAM_RIGHT */}
            <div className="absolute right-4 top-0 bottom-0 w-16 flex flex-col gap-0.5 opacity-20 pointer-events-none text-right overflow-hidden pt-2">
                {sideStreams.map((stream, i) => (
                    <motion.span 
                        key={`right-${stream.id}`} 
                        animate={{ opacity: focusValue > 0.5 ? [0.4, 1, 0.4] : [0.1, 0.4, 0.1] }}
                        transition={{ duration: focusValue > 0.5 ? 0.3 : 2, repeat: Infinity, delay: i * 0.05 }}
                        className="font-mono text-[7px] text-white/50"
                    >
                        {stream.text}
                    </motion.span>
                ))}
            </div>

            {/* 🧬 WAVEFORM_VISUALIZER */}
            <div className="absolute inset-x-0 bottom-0 h-10 flex items-end justify-center gap-[3px] px-2 opacity-50 z-0">
                {Array.from({ length: 50 }).map((_, i) => (
                    <motion.div
                        key={i}
                        animate={{ 
                            height: status === "speaking" || focusValue > 0.5 ? [4, 40, 4] : [2, 15, 2],
                            opacity: status === "speaking" || focusValue > 0.5 ? 1.0 : 0.4,
                            backgroundColor: focusValue > 0.5 ? "#ffffff" : "#22d3ee"
                        }}
                        transition={{ 
                            duration: focusValue > 0.5 ? 0.2 : 0.6, 
                            repeat: Infinity, 
                            delay: i * 0.02,
                            ease: "easeInOut"
                        }}
                        className={`w-[2px] rounded-full`}
                    />
                ))}
            </div>

            {/* 🛑 TACTICAL_LABEL */}
            <motion.div 
                animate={{ 
                    opacity: isIntercepted ? [0.8, 1, 0.8] : (focusValue > 0.5 ? 1.0 : 0.7),
                    scale: focusValue > 0.5 ? 1.05 : 1.0,
                    backgroundColor: isIntercepted ? "rgba(239, 68, 68, 0.2)" : "rgba(34, 211, 238, 0.1)"
                }}
                transition={{ duration: 0.15, repeat: Infinity }}
                className={`mt-4 px-6 py-1 border ${isIntercepted ? 'border-red-500 shadow-[0_0_20px_rgba(255,0,0,0.5)]' : 'border-cyan-500/30 shadow-[0_0_15px_rgba(0,240,255,0.15)]'} rounded-sm z-20 backdrop-blur-md`}
            >
                <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full animate-ping ${isIntercepted ? 'bg-red-500' : 'bg-cyan-500'}`} />
                    <span className={`font-mono text-[11px] font-black tracking-[0.5em] uppercase ${color} ${focusValue > 0.5 ? 'brightness-200' : ''}`}>
                        {isIntercepted ? "NEURAL_SIGNAL_INTERCEPTED" : "OMEGA_NEURAL_UPLINK"}
                    </span>
                </div>
            </motion.div>

            {/* 🧬 DATA_STREAM */}
            <div className="flex flex-col gap-1 items-center w-full mt-3 z-20">
                <AnimatePresence mode="popLayout">
                    {lines.map((line, i) => (
                        <motion.div
                            key={line.id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ 
                                opacity: Math.max(0, 1 - (i * 0.2)) + (focusValue * 0.5), 
                                x: 0,
                                scale: (1 - (i * 0.05)) + (focusValue * 0.1),
                                filter: i > 2 && focusValue < 0.5 ? "blur(1px)" : "blur(0px)"
                            }}
                            exit={{ opacity: 0, x: 20 }}
                            transition={{ duration: 0.2 }}
                            className={`flex gap-4 font-mono text-[8px] font-bold tracking-[0.25em] uppercase ${color}`}
                        >
                            <span className="opacity-40 tabular-nums">[{line.timestamp}]</span>
                            <span className={i === 0 || focusValue > 0.5 ? "brightness-150 text-white" : "opacity-80"}>{line.text}</span>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* 🏮 KINETIC_SCANNER */}
            <div className="absolute top-0 left-0 w-full h-[2px] overflow-hidden opacity-30">
                <motion.div 
                    animate={{ x: ["-100%", "100%"] }}
                    transition={{ duration: focusValue > 0.5 ? 0.8 : 2, repeat: Infinity, ease: "linear" }}
                    className={`w-1/2 h-full bg-gradient-to-r from-transparent via-cyan-400 to-transparent`}
                />
            </div>
        </div>
    );
}
