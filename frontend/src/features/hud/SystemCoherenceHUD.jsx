import React from "react";
import { motion, useTime, useTransform, AnimatePresence } from "framer-motion";

export default function AuraHUD({ 
  isIgniting = false, 
  themeColor = "#00f0ff", 
  systemCoherence = { audioTruth: 100, uiTruth: 100, backendTruth: 100, deviceTruth: 100, coherenceScore: 100 } 
}) {
  const time = useTime();

  // 🪐 KINETIC ROTATIONS (ACCELERATED ON IGNITION)
  const rotate2 = useTransform(time, [0, 15000], [0, isIgniting ? 3600 : 360]);
  const rotate3 = useTransform(time, [0, 25000], [0, isIgniting ? -3600 : -360]);

  const hudAmber = "rgba(255, 185, 0, 0.8)";
  const hudCyan = themeColor;
  const hudRed = "rgba(255, 40, 40, 0.9)";

  return (
    <div className="relative w-[700px] h-[700px] flex items-center justify-center select-none pointer-events-none scale-90">
      
      {/* 🌪️ O.M.E.G.A. XXXVII: THE GOLDEN AURA */}
      <AnimatePresence>
        {[1, 2, 3].map((i) => (
          <motion.div 
            key={i}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: [0.8, 1.5, 2.5], opacity: [0.3, 0.1, 0] }}
            transition={{ 
                duration: isIgniting ? 1.6 : 4, 
                repeat: Infinity, 
                delay: i * (isIgniting ? 0.5 : 1.3), 
                ease: "easeOut" 
            }}
            className="absolute w-[400px] h-[400px] border-[2px] rounded-full blur-[1px]"
            style={{ borderColor: hudAmber }}
          />
        ))}
      </AnimatePresence>

      <svg viewBox="0 0 600 600" className="absolute inset-0 w-full h-full drop-shadow-[0_0_15px_rgba(0,240,255,0.2)]">
        
        {/* 🧭 COMPASS_ORBIT (N-MARKING & TICK SYSTEM) */}
        <motion.g style={{ rotate: rotate3, originX: "300px", originY: "300px" }}>
            <circle cx="300" cy="300" r="280" fill="none" stroke={hudCyan} strokeWidth="0.5" strokeOpacity="0.1" />
            {Array.from({ length: 72 }).map((_, i) => (
                <line 
                    key={i}
                    x1="300" y1="20" x2="300" y2={i % 6 === 0 ? "35" : "28"}
                    stroke={i % 6 === 0 ? hudCyan : "white"}
                    strokeWidth={i % 6 === 0 ? "1.5" : "0.5"}
                    strokeOpacity={i % 6 === 0 ? "0.6" : "0.2"}
                    transform={`rotate(${i * 5}, 300, 300)`}
                />
            ))}
            <text x="300" y="55" textAnchor="middle" fill="white" className="font-mono text-[14px] font-black tracking-widest opacity-80">N</text>
            <text x="545" y="300" textAnchor="middle" fill="white" className="font-mono text-[8px] font-black opacity-40" transform="rotate(90, 545, 300)">090</text>
            <text x="300" y="545" textAnchor="middle" fill="white" className="font-mono text-[8px] font-black opacity-40">180</text>
            <text x="55" y="300" textAnchor="middle" fill="white" className="font-mono text-[8px] font-black opacity-40" transform="rotate(-90, 55, 300)">270</text>
        </motion.g>

        {/* ✈️ OMEGA_TELEMETRY: SYSTEM_COHERENCE (TOP LEFT) */}
        <g transform="translate(100, 100)">
            <text x="0" y="0" fill="white" className="font-mono text-[22px] font-black tracking-tighter drop-shadow-[0_0_10px_white]">
                {systemCoherence.coherenceScore}% <tspan fontSize="8" opacity="0.6">COHERENCE</tspan>
            </text>
            <path d="M -10 10 L 120 10" stroke="white" strokeWidth="0.5" strokeOpacity="0.3" />
            <text x="0" y="25" fill="white" className="font-mono text-[10px] font-black opacity-40 uppercase tracking-widest">
                TRUTH_AUDIT: {systemCoherence.coherenceScore > 95 ? "STABLE" : "DEGRADED"}
            </text>
        </g>

        {/* 🛡️ TRUTH_HEATMAP (RIGHT SIDE VERTICAL BARS) */}
        <g transform="translate(520, 180)">
             {[
                { label: "AUDIO", score: systemCoherence.audioTruth },
                { label: "UI", score: systemCoherence.uiTruth },
                { label: "BACKEND", score: systemCoherence.backendTruth },
                { label: "DEVICE", score: systemCoherence.deviceTruth },
                { label: "MEMORY", score: systemCoherence.memoryTruth }
             ].map((truth, i) => (
                <g key={i} transform={`translate(0, ${i * 35})`}>
                    <rect width="40" height="4" fill="white" opacity="0.1" />
                    <motion.rect 
                        initial={{ width: 0 }}
                        animate={{ width: (truth.score / 100) * 40 }}
                        height="4" 
                        fill={truth.score > 90 ? hudCyan : hudRed} 
                    />
                    <text y="15" fill="white" className="font-mono text-[7px] font-black opacity-40 uppercase tracking-widest">{truth.label}</text>
                </g>
             ))}
             <text x="-40" y="160" fill={hudCyan} className="font-mono text-[10px] font-black tracking-[0.4em] uppercase" transform="rotate(-90, -40, 160)">Neural_Integrity</text>
        </g>

        {/* ⚙️ MECHANICAL_RING_SYSTEM */}
        <motion.g style={{ rotate: rotate2, originX: "300px", originY: "300px" }}>
            <circle cx="300" cy="300" r="220" fill="none" stroke={hudAmber} strokeWidth="2" strokeDasharray="5 150" strokeOpacity="0.8" />
            <circle cx="300" cy="300" r="210" fill="none" stroke={hudAmber} strokeWidth="0.5" strokeDasharray="1 10" strokeOpacity="0.3" />
            <motion.circle 
                cx="300" cy="300" r="220" fill="none" stroke="#fff" strokeWidth="3" strokeDasharray="2 218"
                animate={{ strokeDashoffset: [0, -440] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                style={{ filter: "blur(2px)", opacity: isIgniting ? 0.8 : 0.2 }}
            />
            <text className="font-mono text-[10px] font-black tracking-[1.5em]" fill="white" opacity="0.6">
                <textPath href="#innerCirclePath" startOffset="0%">FLIGHT // SUIT // WEAPONS // RECOVERY</textPath>
            </text>
            <defs>
                <path id="innerCirclePath" d="M 300, 300 m -180, 0 a 180, 180 0 1, 1 360, 0 a 180, 180 0 1, 1 -360, 0" />
            </defs>
        </motion.g>

        {/* 🛑 THE LOBED CORE */}
        <g transform="translate(300, 300)">
            <AnimatePresence>
                {isIgniting && (
                    <motion.circle 
                        initial={{ r: 0, opacity: 0 }}
                        animate={{ r: [0, 100, 150], opacity: [0, 0.4, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
                        fill="none"
                        stroke={hudCyan}
                        strokeWidth="20"
                        style={{ filter: "blur(40px)" }}
                    />
                )}
            </AnimatePresence>
            <motion.path 
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                d="M 0,-40 C 20,-40 35,-20 35,0 C 35,20 20,40 0,40 C -20,40 -35,20 -35,0 C -35,-20 -20,-40 0,-40 Z M 0,-25 L 15,-10 L 25,-10 L 0,-35 L -25,-10 L -15,-10 Z"
                fill="black" 
                stroke={hudCyan} 
                strokeWidth="2"
            />
            <g opacity="0.9">
                 <path d="M -20,-20 L 20,-20 L 0,20 Z" fill={hudCyan} stroke="white" strokeWidth="0.5" transform="rotate(0)" />
                 <path d="M -20,-20 L 20,-20 L 0,20 Z" fill={hudCyan} stroke="white" strokeWidth="0.5" transform="rotate(120)" />
                 <path d="M -20,-20 L 20,-20 L 0,20 Z" fill={hudCyan} stroke="white" strokeWidth="0.5" transform="rotate(240)" />
            </g>
            <circle r="60" fill="none" stroke={hudCyan} strokeWidth="1" strokeDasharray="10 20" opacity="0.2" />
        </g>

        {/* 📉 BOTTOM DIAL */}
        <g transform="translate(150, 480)">
            <circle r="40" fill="none" stroke={hudCyan} strokeWidth="0.5" strokeOpacity="0.4" />
            <motion.line 
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                x1="0" y1="0" x2="0" y2="-35" stroke={hudRed} strokeWidth="1.5" 
            />
            <text y="55" textAnchor="middle" fill={hudCyan} className="font-mono text-[7px] tracking-widest opacity-60">XY_SCAN_MODULE</text>
        </g>
      </svg>
    </div>
  );
}
