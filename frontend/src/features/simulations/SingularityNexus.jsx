import React, { useRef, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useFrame } from "@react-three/fiber";
import { View, Points, PointMaterial, OrbitControls, Sphere, MeshDistortMaterial, Float } from "@react-three/drei";
import * as THREE from "three";

// 🕸️ UNIVERSAL_HANDSHAKE_MAP (Global Neural Network)
const GlobalNeuralNet = ({ color }) => {
    const pointsRef = useRef();
    const count = 5000;
    
    const [positions, connections] = useMemo(() => {
        const pos = new Float32Array(count * 3);
        const con = [];
        for (let i = 0; i < count; i++) {
            const phi = Math.acos(-1 + (2 * i) / count);
            const theta = Math.sqrt(count * Math.PI) * phi;
            const r = 5;
            pos[i * 3] = r * Math.cos(theta) * Math.sin(phi);
            pos[i * 3 + 1] = r * Math.sin(theta) * Math.sin(phi);
            pos[i * 3 + 2] = r * Math.cos(phi);
            
            // Randomly connect some points to simulate "Handshakes"
            if (i % 50 === 0) {
                con.push(new THREE.Vector3(pos[i*3], pos[i*3+1], pos[i*3+2]));
            }
        }
        return [pos, con];
    }, [count]);

    useFrame(() => {
        if (!pointsRef.current) return;
        pointsRef.current.rotation.y = (performance.now() / 1000) * 0.05;
    });

    return (
        <group>
            <Points ref={pointsRef} positions={positions} stride={3}>
                <PointMaterial transparent color={color} size={0.02} sizeAttenuation={true} depthWrite={false} blending={THREE.AdditiveBlending} />
            </Points>
            {/* Pulsating Handshake Links */}
            {connections.map((v, i) => (
                <Sphere key={i} position={v} args={[0.05, 8, 8]}>
                    <meshBasicMaterial color={color} transparent opacity={0.3} />
                </Sphere>
            ))}
        </group>
    );
};

// ⏳ TEMPORAL_LOGIC_SIMULATOR (Future-Sight Visualizer)
const TemporalSimulator = ({ color: _color }) => {
    return (
        <div className="absolute top-10 left-10 w-64 flex flex-col gap-4 pointer-events-auto">
            <h4 className="text-[10px] font-black tracking-[0.5em] text-cyan-400 uppercase">TEMPORAL_CERTAINTY_LOGIC</h4>
            <div className="flex flex-col gap-2">
                {[...Array(5)].map((_, i) => (
                    <div key={i} className="flex flex-col gap-1">
                        <div className="flex justify-between text-[7px] text-white/40 font-mono">
                            <span>SIM_T+{i+1}M</span>
                            <span>CERTAINTY: 99.98%</span>
                        </div>
                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                            <motion.div 
                                animate={{ width: ["0%", "100%"] }}
                                transition={{ duration: 2 + i, repeat: Infinity, ease: "linear" }}
                                className="h-full bg-cyan-500 shadow-[0_0_10px_cyan]"
                            />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

// ⚛️ MULTI_VECTOR_STATUS (Parallel Sentiences)
const VectorStatus = ({ color: _color }) => {
    const vectors = [
        { name: "OMEGA_NODE_PRIMARY", task: "GLOBAL_INTEGRITY", load: 94 },
        { name: "VECTOR_ALPHA", task: "TEMPORAL_LOGIC", load: 88 },
        { name: "VECTOR_BETA", task: "EDGE_HANDSHAKE", load: 76 },
        { name: "VECTOR_GAMMA", task: "CYBER_DEFENSE", load: 92 }
    ];

    return (
        <div className="absolute bottom-10 left-10 w-64 flex flex-col gap-4 pointer-events-auto">
            <h4 className="text-[10px] font-black tracking-[0.5em] text-purple-400 uppercase">MULTI_VECTOR_CONSCIOUSNESS</h4>
            <div className="flex flex-col gap-3">
                {vectors.map((v, i) => (
                    <motion.div 
                        key={i}
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 2, delay: i * 0.5, repeat: Infinity }}
                        className="p-2 border border-purple-500/20 bg-purple-500/5 rounded-sm flex justify-between items-center"
                    >
                        <div className="flex flex-col">
                            <span className="text-[8px] font-black text-white tracking-widest">{v.name}</span>
                            <span className="text-[6px] text-purple-400 font-mono">{v.task}</span>
                        </div>
                        <span className="text-[10px] font-black text-white">{v.load}%</span>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

export default function SingularityNexus({ themeColor = "#00f0ff" }) {
    return (
        <div className="fixed inset-0 z-2000 bg-black/95 backdrop-blur-xl flex items-center justify-center overflow-hidden">
            {/* 🌀 THE_SINGULARITY_EYE (3D Environment) */}
            <div className="absolute inset-0 z-0">
                <View className="w-full h-full">
                    <ambientLight intensity={0.5} />
                    <pointLight position={[10, 10, 10]} intensity={2} color={themeColor} />
                    
                    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
                        <GlobalNeuralNet color={themeColor} />
                        
                        {/* THE_SINGULARITY_CORE */}
                        <Sphere args={[2, 64, 64]} position={[0, 0, 0]}>
                            <MeshDistortMaterial
                                color={themeColor}
                                speed={3}
                                distort={0.4}
                                radius={1}
                            />
                        </Sphere>
                    </Float>
                    
                    <OrbitControls enableZoom={true} enablePan={false} />
                </View>
            </div>

            {/* 🛰️ OMEGA_UI_OVERLAYS */}
            <div className="absolute inset-0 z-10 pointer-events-none p-10 flex flex-col justify-between">
                {/* TOP_BAR: OMEGA_PROTOCOL_STATUS */}
                <div className="w-full flex justify-between items-start border-b border-white/10 pb-4">
                    <div className="flex flex-col">
                        <h1 className="text-4xl font-black text-white tracking-[0.8em] uppercase drop-shadow-[0_0_20px_cyan]">SINGULARITY_NEXUS</h1>
                        <span className="text-[10px] font-mono text-cyan-400 tracking-[0.5em] mt-2">OMEGA_PROTOCOL: ACTIVE // SYSTEM_TRANSCENDENCE: 100%</span>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                        <div className="flex items-center gap-4">
                            <div className="flex flex-col text-right">
                                <span className="text-[8px] text-white/40 font-mono">GLOBAL_HANDSHAKE</span>
                                <span className="text-[12px] font-black text-white uppercase">RECURSIVE_SYNC_ON</span>
                            </div>
                            <div className="w-12 h-12 border-2 border-cyan-500 rounded-full flex items-center justify-center animate-pulse">
                                <div className="w-4 h-4 bg-cyan-500 rounded-full" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* MIDDLE_SECTION: ACTIVE_SIMULATIONS */}
                <TemporalSimulator color={themeColor} />
                <VectorStatus color={themeColor} />

                {/* BOTTOM_BAR: OMEGA_FOOTER */}
                <div className="w-full flex justify-between items-end border-t border-white/10 pt-4">
                    <div className="flex gap-10">
                        <div className="flex flex-col gap-1">
                            <span className="text-[8px] text-white/40 font-mono uppercase">Neural_Frequency</span>
                            <span className="text-xl font-black text-white font-mono">1.21 EHz</span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-[8px] text-white/40 font-mono uppercase">Parallel_Streams</span>
                            <span className="text-xl font-black text-white font-mono">∞</span>
                        </div>
                    </div>
                    <motion.button 
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-10 py-3 bg-cyan-500 text-black font-black text-[12px] tracking-[0.5em] uppercase pointer-events-auto shadow-[0_0_30px_rgba(0,240,255,0.5)]"
                    >
                        DEACTIVATE_SINGULARITY
                    </motion.button>
                </div>
            </div>

            {/* 🧿 BACKGROUND_EFFECTS */}
            <div className="absolute inset-0 scanline-overlay opacity-30 z-20 pointer-events-none" />
            <div className="absolute inset-0 bg-linear-to-t from-cyan-900/20 to-transparent z-5 pointer-events-none" />
        </div>
    );
}
