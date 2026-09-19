import React, { useEffect, useState, useRef, useMemo } from "react";
import Webcam from "react-webcam";
import { motion, AnimatePresence, useMotionValue } from "framer-motion";
import { useFrame } from "@react-three/fiber";
import { View } from "@react-three/drei";
import * as THREE from "three";

const seededValue = (index, seed = 79) => {
    const value = Math.sin(index * 103.41 + seed) * 10000;
    return value - Math.floor(value);
};

const TemporalGhostLayer = ({ meshRef, count, positions, progress, opacityFactor }) => (
    <points ref={meshRef}>
        <bufferGeometry>
            <bufferAttribute
                attach="attributes-position"
                count={count}
                array={positions}
                itemSize={3}
            />
        </bufferGeometry>
        <pointsMaterial 
            size={0.035} 
            color="#00f0ff" 
            transparent 
            opacity={Math.min(progress / 100, 0.4) * opacityFactor} 
            blending={THREE.AdditiveBlending}
            sizeAttenuation={true}
        />
    </points>
);

const biometricDrift = (progress, index, min, range, scale = 1) => {
    const phase = progress / 100;
    return min + ((Math.sin(phase * scale + index) + 1) / 2) * range;
};

// 🌀 O.M.E.G.A. SSS-TIER: NEURAL_TEMPORAL_GHOST (The 4D Element)
const TemporalMesh = ({ progress }) => {
    const meshRef = useRef();
    const count = 1500;
    const positions = useMemo(() => {
        const pos = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            const theta = seededValue(i, 3) * Math.PI * 2;
            const phi = seededValue(i, 7) * Math.PI * 2;
            const r = 2.0;
            pos[i * 3] = r * Math.sin(theta) * Math.cos(phi);
            pos[i * 3 + 1] = r * Math.sin(theta) * Math.sin(phi);
            pos[i * 3 + 2] = r * Math.cos(theta);
        }
        return pos;
    }, []);

    useFrame((_state) => {
        if (!meshRef.current) return;
        const t = performance.now() / 1000;
        meshRef.current.rotation.y = Math.sin(t * 0.2) * 0.5;
        meshRef.current.rotation.x = Math.sin(t * 0.1) * 0.2;
        
        // 🚀 4D PULSE: SCALE DRIVEN BY TEMPORAL RESONANCE
        const pulse = 1 + Math.sin(t * 2) * 0.05;
        meshRef.current.scale.set(pulse, pulse, pulse);
    });

    return (
        <group>
            <TemporalGhostLayer meshRef={meshRef} count={count} positions={positions} progress={progress} opacityFactor={1} />
            <TemporalGhostLayer meshRef={meshRef} count={count} positions={positions} progress={progress} opacityFactor={0.5} />
            <TemporalGhostLayer meshRef={meshRef} count={count} positions={positions} progress={progress} opacityFactor={0.2} />
        </group>
    );
};

// 👁️ O.M.E.G.A. SSS-TIER: NEURAL_TELEMETRY_TAG
const TelemetryTag = ({ label, value, unit, position, color = "cyan", mouseX, mouseY }) => {
    const colorMap = {
        cyan: { text: "text-cyan-400", sub: "text-cyan-600/60", line: "from-cyan-500/40", glow: "shadow-[0_0_15px_cyan]" },
        red: { text: "text-red-400", sub: "text-red-600/60", line: "from-red-500/40", glow: "shadow-[0_0_15px_red]" },
        amber: { text: "text-amber-400", sub: "text-amber-600/60", line: "from-amber-500/40", glow: "shadow-[0_0_15px_amber]" }
    };
    const theme = colorMap[color] || colorMap.cyan;

    // 🚀 DEPTH PARALLAX: CALCULATE OFFSET
    return (
        <motion.div 
            initial={{ opacity: 0, x: -20, filter: 'blur(10px)' }}
            animate={{ 
                opacity: 1, 
                filter: 'blur(0px)'
            }}
            style={{ x: mouseX, y: mouseY }}
            transition={{ type: "spring", stiffness: 100, damping: 30 }}
            className={`absolute ${position} flex flex-col gap-1 pointer-events-none z-50`}
        >
            <div className="flex items-center gap-2">
                <div className={`w-1.5 h-1.5 rounded-full ${theme.text.replace('text-', 'bg-')} ${theme.glow}`} />
                <span className={`text-[7px] font-black uppercase tracking-[0.4em] ${theme.sub}`}>{label}</span>
            </div>
            <div className="flex items-baseline gap-1">
                <span className="text-[14px] font-mono font-black text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.4)]">{value}</span>
                <span className="text-[7px] font-mono text-white/40">{unit}</span>
            </div>
            <motion.div 
                animate={{ width: [0, 60, 0] }}
                transition={{ duration: 3, repeat: Infinity }}
                className={`h-[1px] bg-gradient-to-r ${theme.line} to-transparent`} 
            />
        </motion.div>
    );
};

export default function FaceScanner({ onVerify, mode = 'standard' }) {
  // Biometric scanner initialized
  const [status, setStatus] = useState("ESTABLISHING_SSS-TIER_LINK...");
  const [biometrics, setBiometrics] = useState({
    synaptic: 98.2,
    adrenaline: 0.12,
    heartrate: 72,
    retina_sync: 0,
    dna_match: 0
  });
  const [progress, setProgress] = useState(0);
  const [isFaceDetected, setIsFaceDetected] = useState(false);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const webcamRef = useRef(null);
  const completionTimerRef = useRef(null);
  const biometricsRef = useRef(biometrics);
  const ambientFlux = useMemo(() => (
    Array.from({ length: 20 }, (_, i) => ({
      delay: seededValue(i, 31) * 10,
      duration: 5 + seededValue(i, 47) * 10,
      left: `${seededValue(i, 59) * 100}%`
    }))
  ), []);

  useEffect(() => {
    const handleMouse = (e) => {
        mouseX.set((e.clientX / window.innerWidth - 0.5) * 20);
        mouseY.set((e.clientY / window.innerHeight - 0.5) * 20);
    };
    window.addEventListener('mousemove', handleMouse);
    return () => window.removeEventListener('mousemove', handleMouse);
  }, [mouseX, mouseY]);

  useEffect(() => {
    const interval = setInterval(() => {
      setBiometrics(prev => ({
        ...prev,
        synaptic: biometricDrift(progress, 0.4, 98, 2, 5),
        adrenaline: biometricDrift(progress, 1.1, 0.1, 0.05, 6),
        heartrate: biometricDrift(progress, 2.3, 70, 5, 4),
        retina_sync: Math.min(progress * 1.02, 100),
        dna_match: Math.min(progress * 0.98, 100)
      }));
    }, 100);
    return () => clearInterval(interval);
  }, [progress]);

  useEffect(() => {
    biometricsRef.current = biometrics;
  }, [biometrics]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setStatus("SCANNING_NEURAL_GEOMETRY_V4.0...");
      setIsFaceDetected(true);
    }, 1200);
    const detectedMood = mode === "combat" ? "AUTHORITATIVE" : "FOCUSED";

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setStatus(`IDENTITY_SECURED // WELCOME_GENESIS // TIER: SSS+`);
          
          completionTimerRef.current = setTimeout(() => {
              onVerify({ verified: true, mood: detectedMood, biometrics: biometricsRef.current });
          }, 2000); 
          return 100;
        }
        const inc = (100 - prev) * 0.05; // Cinematic easing
        return Math.min(prev + Math.max(inc, 0.5), 100);
      });
    }, 120);

    return () => {
      clearTimeout(timer);
      clearInterval(interval);
      clearTimeout(completionTimerRef.current);
    };
  }, [mode, onVerify]);

  return (
    <div className="absolute inset-0 z-[150] flex flex-col items-center justify-center bg-black overflow-hidden select-none">
      
      {/* 🔮 SSS-TIER: ATMOSPHERIC_DEPTH */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,180,255,0.08)_0%,#000_100%)] z-0" />
      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20 z-0" />
      
      {/* 🎯 SSS-TIER: PRECISION_HUD_ANCHORS */}
      <div className="absolute inset-0 pointer-events-none z-50 p-16">
          <div className="absolute top-16 left-16 w-64 h-64 border-t-2 border-l-2 border-cyan-400/30 shadow-[0_0_50px_rgba(0,240,255,0.1)]" />
          <div className="absolute top-16 right-16 w-64 h-64 border-t-2 border-r-2 border-cyan-400/30 shadow-[0_0_50px_rgba(0,240,255,0.1)]" />
          <div className="absolute bottom-16 left-16 w-64 h-64 border-b-2 border-l-2 border-cyan-400/30 shadow-[0_0_50px_rgba(0,240,255,0.1)]" />
          <div className="absolute bottom-16 right-16 w-64 h-64 border-b-2 border-r-2 border-cyan-400/30 shadow-[0_0_50px_rgba(0,240,255,0.1)]" />
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative flex flex-col items-center gap-24"
      >
        {/* 👁️ THE_LENS: 3D_HOLOGRAPHIC_ORBITAL_INTERFACE */}
        <div className="w-[600px] h-[600px] relative flex items-center justify-center">
            
            {/* 🌌 WEBGL_3D_VOLUMETRIC_ENGINE */}
            <div className="absolute inset-0 z-10 pointer-events-none">
                <View className="w-full h-full">
                    <ambientLight intensity={0.5} />
                    <TemporalMesh progress={progress} />
                </View>
            </div>

            {/* 🧬 HOLOGRAPHIC_DEPTH_RINGS */}
            {Array.from({ length: 3 }).map((_, i) => (
                <motion.div 
                    key={i}
                    animate={{ rotate: i % 2 === 0 ? 360 : -360 }}
                    transition={{ duration: 15 + i * 5, repeat: Infinity, ease: "linear" }}
                    className="absolute rounded-full border border-cyan-500/10"
                    style={{ 
                        width: `${100 + i * 10}%`, 
                        height: `${100 + i * 10}%`,
                        transform: `translateZ(${i * 20}px)` 
                    }}
                />
            ))}

            {/* 🛡️ THE_BRIDGE: ANALYTICAL_FEED */}
            <div className="w-[400px] h-[400px] rounded-full overflow-hidden border-[8px] border-white/5 relative shadow-[0_0_150px_rgba(0,240,255,0.3)] z-20">
                <Webcam
                   ref={webcamRef}
                   audio={false}
                   videoConstraints={{ facingMode: "user", width: 800, height: 800 }}
                   className="w-full h-full object-cover grayscale contrast-[1.4] brightness-150 scale-125"
                />
                
                {/* 🛡️ 4D_TEMPORAL_MASK */}
                <div className="absolute inset-0 bg-[radial-gradient(circle,transparent_40%,rgba(0,0,0,0.9)_100%)] z-10" />
                <motion.div 
                    animate={{ y: [-300, 300] }} 
                    transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute inset-x-0 bg-gradient-to-r from-transparent via-cyan-400 to-transparent h-[2px] shadow-[0_0_50px_cyan] z-20"
                />
                
                <AnimatePresence>
                    {isFaceDetected && (
                        <motion.div 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="absolute inset-0 z-30"
                        >
                             <div className="absolute inset-0 border-[2px] border-cyan-400/20 rounded-full animate-pulse" />
                             <motion.div 
                                animate={{ rotate: 360 }} 
                                transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                                className="absolute inset-4 border-t-2 border-cyan-500 rounded-full shadow-[0_0_20px_cyan]"
                             />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* 🛰️ SSS-TIER: NEURAL_TELEMETRY_ARRAY */}
            <TelemetryTag label="NEURAL_LOAD" value={`${Math.floor(biometrics.synaptic)}%`} unit="GHZ" position="top-[-80px] left-[-40px]" mouseX={mouseX} mouseY={mouseY} />
            <TelemetryTag label="RETINA_SYNC" value={`${Math.floor(biometrics.retina_sync)}%`} unit="V19" position="top-[-100px] right-[-60px]" color="amber" mouseX={mouseX} mouseY={mouseY} />
            <TelemetryTag label="HEART_RATE" value={Math.floor(biometrics.heartrate)} unit="BPM" position="bottom-[0px] left-[-120px]" color="red" mouseX={mouseX} mouseY={mouseY} />
            <TelemetryTag label="GENETIC_ID" value={`${Math.floor(biometrics.dna_match)}%`} unit="SSS" position="bottom-[20px] right-[-140px]" mouseX={mouseX} mouseY={mouseY} />
            
            {/* 🧬 ADDITIONAL_ANALYTICS */}
            <AnimatePresence>
                {progress > 50 && (
                    <TelemetryTag label="SENTIENCE_LEVEL" value="ALPHA_03" unit="OMN" position="bottom-[-80px] left-1/2 -translateX-1/2" color="cyan" mouseX={mouseX} mouseY={mouseY} />
                )}
            </AnimatePresence>
            <TelemetryTag label="dna_sequencing" value={biometrics.dna_match.toFixed(1)} unit="%" position="bottom-1/2 -right-72" color="amber" mouseX={mouseX} mouseY={mouseY} />
            <TelemetryTag label="4d_temporal_lock" value="ALIGNED" unit="SEC" position="bottom-10 -right-60" color="cyan" mouseX={mouseX} mouseY={mouseY} />
        </div>

        {/* 🧩 SSS-TIER: STATUS_HUD */}
        <div className="flex flex-col items-center gap-10">
            <div className="flex flex-col items-center gap-2">
                <motion.span 
                    key={status}
                    initial={{ opacity: 0, y: 10, letterSpacing: "1em" }}
                    animate={{ opacity: 1, y: 0, letterSpacing: "0.8em" }}
                    className="text-cyan-400 font-mono text-[11px] font-black uppercase drop-shadow-[0_0_15px_cyan]"
                >
                    {status}
                </motion.span>
                <div className="w-[500px] h-[2px] bg-white/5 relative overflow-hidden">
                    <motion.div 
                        animate={{ width: `${progress}%` }}
                        className="h-full bg-gradient-to-r from-cyan-600 to-cyan-400 shadow-[0_0_30px_cyan]"
                    />
                </div>
                <div className="flex justify-between w-[500px] mt-2">
                    <span className="text-[7px] font-mono text-cyan-400/40 uppercase tracking-[0.5em]">SYSTEM_VERSION_7.4.2</span>
                    <span className="text-[12px] font-mono text-cyan-400 font-black tracking-widest">{Math.floor(progress)}%</span>
                </div>
            </div>
        </div>
      </motion.div>

      {/* 🚀 4D_AMBIENT_FLUX */}
      <div className="absolute inset-0 pointer-events-none">
          {ambientFlux.map(({ delay, duration, left }, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: "100%" }}
                animate={{ opacity: [0, 0.4, 0], y: "-100%" }}
                transition={{ duration, repeat: Infinity, delay }}
                className="absolute w-[1px] h-20 bg-cyan-400/20"
                style={{ left }}
              />
          ))}
      </div>
    </div>
  );
}
