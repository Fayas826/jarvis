import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const DominionHUD = ({ onClose, onControl }) => {
    const [nodes] = useState([
        { id: 'living_room_lights', label: 'Living Room Core', status: 'ONLINE', depth: 0, angle: 0 },
        { id: 'lab_hologram', label: 'Sanctuary Projection', status: 'ONLINE', depth: 100, angle: 120 },
        { id: 'smart_plug', label: 'Primary Power Cell', status: 'OFFLINE', depth: -100, angle: 240 }
    ]);

    const routines = [
        { id: 'GHOST_PROTOCOL', label: 'GHOST_PROTOCOL', icon: '👻' },
        { id: 'STARK_SECURITY', label: 'STARK_SECURITY', icon: '🛡️' },
        { id: 'NIGHT_WATCH', label: 'NIGHT_WATCH', icon: '🌙' }
    ];

    const handleAction = (id, action) => {
        onControl(id, action);
    };

    const handleRoutine = (id) => {
        onControl(id, 'routine');
    };

    return (
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-1500 flex items-center justify-center bg-black/80 backdrop-blur-3xl overflow-hidden"
        >
            {/* 🌌 PEAK_DEPTH_LAYERING */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,240,255,0.05)_0%,transparent_70%)]" />
                <div className="absolute inset-0 tactical-grid opacity-10" />
            </div>

            <div className="relative w-full h-full flex flex-col items-center justify-center">
                
                {/* 🏹 HEADER_TACTICAL */}
                <div className="absolute top-12 flex flex-col items-center gap-2">
                    <span className="font-mono text-cyan-400 text-xs tracking-[1em] uppercase">Molecular_Dominion_Lattice</span>
                    <div className="w-64 h-px bg-linear-to-r from-transparent via-cyan-500/50 to-transparent" />
                </div>

                {/* 🧪 ROUTINE_SECTOR */}
                <div className="absolute left-12 top-1/2 -translate-y-1/2 flex flex-col gap-4 z-20">
                    <span className="text-[8px] font-black tracking-[0.5em] text-cyan-500/50 uppercase italic mb-2">Physical_Macros</span>
                    {routines.map(r => (
                        <button 
                            key={r.id}
                            onClick={() => handleRoutine(r.id)}
                            className="w-48 p-4 bg-cyan-950/20 border border-cyan-500/10 hover:border-cyan-400 group flex items-center gap-4 transition-all relative overflow-hidden"
                        >
                            <div className="absolute inset-0 bg-cyan-400/0 group-hover:bg-cyan-400/5 transition-colors" />
                            <span className="text-xl opacity-50 group-hover:opacity-100 transition-opacity">{r.icon}</span>
                            <span className="text-[9px] font-black tracking-widest text-cyan-400 group-hover:text-white transition-colors">{r.label}</span>
                        </button>
                    ))}
                </div>

                {/* 🌀 3D_ORBITAL_ENGINE */}
                <div className="relative w-[600px] h-[600px] flex items-center justify-center" style={{ perspective: '1200px' }}>
                    <motion.div 
                        animate={{ rotateY: 360 }}
                        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
                        className="relative w-full h-full"
                        style={{ transformStyle: 'preserve-3d' }}
                    >
                        {nodes.map((node) => (
                            <motion.div
                                key={node.id}
                                className="absolute left-1/2 top-1/2 -ml-16 -mt-16 w-32 h-32 flex flex-col items-center justify-center cursor-pointer group"
                                style={{ 
                                    transform: `rotateY(${node.angle}deg) translateZ(250px)`,
                                    transformStyle: 'preserve-3d'
                                }}
                                whileHover={{ scale: 1.1 }}
                                onClick={() => handleAction(node.id, 'toggle')}
                            >
                                {/* Holographic Node UI */}
                                <div className="absolute inset-0 border border-cyan-500/30 rounded-full bg-cyan-900/10 backdrop-blur-md group-hover:border-cyan-400 transition-all shadow-[0_0_20px_rgba(0,240,255,0.1)] group-hover:shadow-[0_0_40px_rgba(0,240,255,0.3)]" />
                                
                                <motion.div 
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                                    className="absolute inset-2 border border-dashed border-cyan-500/20 rounded-full" 
                                />

                                <div className="relative z-10 flex flex-col items-center text-center px-4">
                                    <span className="text-[10px] font-black tracking-widest text-cyan-400 uppercase mb-1">{node.label}</span>
                                    <div className="flex flex-col gap-0.5">
                                        <span className={`text-[7px] font-mono ${node.status === 'ONLINE' ? 'text-green-400' : 'text-red-400'}`}>STATUS: {node.status}</span>
                                        <span className="text-[6px] font-mono text-white/40 tracking-wider">RES_SIG: {node.status === 'ONLINE' ? '98.4%' : '0.0%'}</span>
                                    </div>
                                </div>

                                {/* Radial Glow */}
                                <div className="absolute inset-[-10px] bg-cyan-400/5 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                            </motion.div>
                        ))}
                    </motion.div>

                    {/* Central Core Signal */}
                    <div className="absolute w-24 h-24 flex items-center justify-center">
                        <div className="absolute inset-0 border-2 border-cyan-500/20 rounded-full animate-ping" />
                        <div className="w-4 h-4 bg-cyan-400 rounded-full shadow-[0_0_30px_cyan]" />
                    </div>
                </div>

                {/* 🏹 CLOSE_PROCEDURE */}
                <button 
                    onClick={onClose}
                    className="absolute bottom-24 px-8 py-2 border border-cyan-500/50 bg-cyan-500/10 font-mono text-cyan-400 text-[9px] tracking-[0.5em] uppercase hover:bg-cyan-500 hover:text-black transition-all"
                >
                    Disengage_Dominion
                </button>

                <div className="absolute bottom-12 flex flex-col items-center gap-1 opacity-40">
                    <span className="text-[7px] font-mono tracking-widest text-white/60">ESTATE_NODE_SYNCHRONIZATION_ACTIVE</span>
                    <div className="flex gap-2">
                        {[1, 2, 3, 4, 5].map(i => <div key={i} className="w-1 h-1 bg-cyan-400 animate-pulse" style={{ animationDelay: `${i * 0.2}s` }} />)}
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default DominionHUD;
