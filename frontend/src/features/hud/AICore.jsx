import React, { useMemo, useRef } from "react";
import * as THREE from "three";
import { useFrame } from "@react-three/fiber";
import { View, Points, PointMaterial } from "@react-three/drei";
import { motion } from "framer-motion";
import MemoryLattice from "@/features/simulations/MemoryLattice";

const seededValue = (index, seed = 19) => {
  const value = Math.sin(index * 57.31 + seed) * 10000;
  return value - Math.floor(value);
};

// 🌀 THE SWARM: Molecular Point Cloud
const ParticleSwarm = ({ status, mode, powerMode = "BALANCED" }) => {
  const pointsRef = useRef();

  // 🧬 Generate 5000 High-Fidelity Neural Particles
  const positions = useMemo(() => {
    const count = 1000;
    const positions = new Float32Array(count * 3);
    
    for (let i = 0; i < count; i++) {
       const r = 2.0 + Math.pow(seededValue(i, 3), 2) * 1.5; 
       const theta = 2 * Math.PI * seededValue(i, 7);
       const phi = Math.acos(2 * seededValue(i, 11) - 1);
       
       const x = r * Math.sin(phi) * Math.cos(theta);
       const y = r * Math.sin(phi) * Math.sin(theta);
       const z = r * Math.cos(phi);
       
       positions[i*3] = x;
       positions[i*3+1] = y;
       positions[i*3+2] = z;
    }
    return positions;
  }, []);

  useFrame((_state, delta) => {
    if (!pointsRef.current) return;
    
    const time = performance.now() / 1000;
    
    let rotationScale = 1.0;
    if (powerMode === "OVERCLOCK") rotationScale = 5.0;
    if (powerMode === "STEALTH") rotationScale = 0.3;

    pointsRef.current.rotation.y += delta * 0.2 * rotationScale; 
    const isSupernova = powerMode === 'OVERCLOCK' && status === 'speaking';
    const targetScale = isSupernova ? 3.5 : (status === 'thinking' ? 1.1 : (status === 'listening' ? 2.2 : 1.5));
    const lerpSpeed = isSupernova ? 0.02 : (status === 'speaking' ? 0.15 : 0.05);
    pointsRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), lerpSpeed);

    const rotationMultiplier = isSupernova ? 8.0 : (powerMode === 'OVERCLOCK' ? 4.0 : (powerMode === 'STEALTH' ? 0.5 : 1.0));
    pointsRef.current.rotation.y += 0.005 * rotationMultiplier;
    pointsRef.current.rotation.z += 0.002 * rotationMultiplier;

    const intensityBase = isSupernova ? 4.0 : (status === 'speaking' ? 2.0 : 1.0);
    const intensityPulse = intensityBase + Math.sin(time * 4) * (isSupernova ? 1.5 : 0.3);
    pointsRef.current.material.opacity = Math.min(1.0, intensityPulse * 0.4);
    pointsRef.current.material.size = isSupernova ? 0.025 : 0.015;
    
    // ⚡ Tier 10: Breathing Resonance (LISTENING)
    if (status === 'listening') {
        const breathingScale = 1.0 + Math.sin(time * 3) * 0.1; 
        // Apply breathing scale offset to the base scale
        pointsRef.current.scale.multiplyScalar(breathingScale);
        pointsRef.current.rotation.z += delta * 0.4 * rotationScale;
    } else if (status === 'thinking') {
        pointsRef.current.rotation.y += delta * 1.5 * rotationScale; 
    } else {
        pointsRef.current.position.y = THREE.MathUtils.lerp(pointsRef.current.position.y, 0, 0.1);
    }
  });

  let color = "#00f0ff";
  if (mode === "offline") color = "#ff0000";
  if (mode === "system") color = "#ff00ff";
  if (status === "listening") color = "#ffb900";
  if (status === "thinking" || status === "speaking") color = "#00f0ff";

  const circleTexture = useMemo(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext("2d");
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, "rgba(255,255,255,1)");
    gradient.addColorStop(0.2, "rgba(255,255,255,0.8)");
    gradient.addColorStop(0.5, "rgba(255,255,255,0.2)");
    gradient.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(32, 32, 32, 0, 2 * Math.PI);
    ctx.fill();
    return new THREE.CanvasTexture(canvas);
  }, []);

  return (
    <group>
      <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
        <PointMaterial
          transparent
          color={color}
          size={status === "listening" ? 0.15 : 0.08}
          sizeAttenuation={true}
          depthWrite={false}
          depthTest={false}
          blending={THREE.AdditiveBlending}
          map={circleTexture}
          opacity={0.8}
        />
      </Points>
      {/* 🌀 Energy Core Glow (3D) */}
      <mesh scale={[2, 2, 2]}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.05} />
      </mesh>
    </group>
  );
};

const OrbitalRings = ({ status, mode }) => {
    const ringRef1 = useRef();
    const ringRef2 = useRef();
    const ringRef3 = useRef();

    useFrame(() => {
        if (!ringRef1.current || !ringRef2.current || !ringRef3.current) return;
        
        const t = performance.now() / 1000;
        ringRef1.current.rotation.x = t * 0.1;
        ringRef1.current.rotation.y = t * 0.2;
        ringRef2.current.rotation.x = t * -0.15;
        ringRef2.current.rotation.z = t * 0.15;
        ringRef3.current.rotation.y = t * 0.1;
        ringRef3.current.rotation.z = t * -0.2;

        const scale = status === 'thinking' ? 0.9 : (status === 'listening' ? 1.6 : 1.2);
        [ringRef1, ringRef2, ringRef3].forEach(ref => {
            if (ref.current) {
                ref.current.scale.lerp(new THREE.Vector3(scale, scale, scale), 0.05);
            }
        });
    });

    const ringColor = mode === "offline" ? "#ff0000" : (status === "listening" ? "#ffb900" : "#00f0ff");

    return (
        <group>
            <mesh ref={ringRef1}>
                <torusGeometry args={[3.8, 0.02, 16, 100]} />
                <meshBasicMaterial color={ringColor} transparent opacity={0.5} wireframe />
            </mesh>
            <mesh ref={ringRef2}>
                <torusGeometry args={[4.4, 0.015, 16, 100]} />
                <meshBasicMaterial color={mode === "system" ? "#ff00ff" : ringColor} transparent opacity={0.3} wireframe />
            </mesh>
            <mesh ref={ringRef3}>
                <torusGeometry args={[5.2, 0.01, 16, 100]} />
                <meshBasicMaterial color="#ffffff" transparent opacity={0.15} wireframe />
            </mesh>
            {/* ⚡ Tactical Orbital Markers */}
            <group rotation={[Math.PI / 4, 0, 0]}>
                 <mesh position={[5.2, 0, 0]}>
                     <sphereGeometry args={[0.05, 8, 8]} />
                     <meshBasicMaterial color="#ffffff" />
                 </mesh>
            </group>
        </group>
    );
};

const CameraRig = ({ status }) => {
    useFrame((state) => {
       if (!state.camera) return;
       const targetZ = status === "thinking" ? 6 : (status === "listening" ? 10 : 8);
       state.camera.position.z = THREE.MathUtils.lerp(state.camera.position.z, targetZ, 0.05);
       state.camera.position.x = 0;
       state.camera.position.y = 0;
       state.camera.lookAt(0,0,0);
    });
    return null;
};

export default function AICore({ 
  mode = "offline", 
  status = "idle", 
  systemPulse = false, 
  powerMode = "BALANCED", 
  themeColor = "#00f0ff",
  acousticStats = { intelligenceScore: 98 }, // 🎙️ Linked to OMEGA_ACOUSTICS
  onClick 
}) {
  const parallax = { x: 0, y: 0 };

  return (
    <div 
        className="relative flex items-center justify-center w-[1000px] h-[1000px] select-none cursor-pointer"
        onClick={onClick}
    >
      <div className="absolute inset-0 z-10 w-full h-full">
          <View className="w-full h-full">
              <CameraRig status={status} />
              <ParticleSwarm status={status} mode={mode} powerMode={powerMode} />
              <OrbitalRings status={status} mode={mode} />
              <MemoryLattice />
          </View>
      </div>

      <motion.div 
        animate={{ 
            scale: status === "thinking" ? [1, 1.1, 1] : (systemPulse ? [1, 1.05, 1] : 1),
            opacity: status === "thinking" ? 0.3 : 0.15,
            x: parallax.x * -5, 
            y: parallax.y * 5
        }}
        animate={{ 
            scale: status === "listening" ? [1, 1.1, 1] : [1, 1.05, 1],
            opacity: status === "thinking" ? [0.4, 0.8, 0.4] : 0.6
        }}
        transition={{ duration: status === "thinking" ? 0.8 : 4, repeat: Infinity }}
        className={`absolute w-[500px] h-[500px] rounded-full blur-[60px] z-0 energy-pulse ${status === 'listening' ? 'stark-glow-amber' : 'stark-glow-cyan'}`}
        style={{ 
            background: `radial-gradient(circle, ${themeColor}66 0%, transparent 70%)`,
            mixBlendMode: 'screen',
            filter: `brightness(${acousticStats.intelligenceScore / 100}) saturate(1.5)`
        }}
      />

      <div className="absolute inset-0 flex items-center justify-center z-50 pointer-events-none">
          <motion.div 
              className="flex flex-col items-center justify-center relative p-16"
              animate={{
                  scale: status === "thinking" ? 0.8 : (status === "listening" ? 1.3 : 1),
                  opacity: status === "thinking" ? [0.5, 1, 0.5] : 1,
                  x: parallax.x * -10,
                  y: parallax.y * 10
              }}
              transition={{ duration: status === "thinking" ? 0.3 : 1, repeat: Infinity, type: "spring", stiffness: 300, damping: 30 }}
          >
              {/* 🏮 ZENITH_CYAN_RING */}
              <motion.div 
                animate={{ 
                    rotate: 360,
                    scale: status === "listening" ? [1, 1.05, 1] : 1
                }}
                transition={{ 
                    rotate: { duration: 15, repeat: Infinity, ease: "linear" },
                    scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
                }}
                className="absolute inset-0 border-[3px] border-cyan-400/40 rounded-full shadow-[0_0_30px_rgba(34,211,238,0.3)] ring-offset-4 ring-2 ring-cyan-500/10"
              />
              
              <span className="font-mono text-[18px] font-black tracking-[1.2em] text-white mix-blend-screen drop-shadow-[0_0_20px_rgba(255,255,255,0.8)] relative z-10 pl-[1.2em]">
                  JARVIS
              </span>
              
              <div className="flex gap-1 items-center mt-2 relative z-10">
                  <div className="w-8 h-[1px] bg-white/40" />
                  <div className="w-[3px] h-[3px] rounded-full bg-white/80 animate-ping" />
                  <div className="w-28 h-[1px] bg-white/80 shadow-[0_0_15px_white]" />
                  <div className="w-[3px] h-[3px] rounded-full bg-white/80 animate-ping" />
                  <div className="w-8 h-[1px] bg-white/40" />
              </div>
          </motion.div>
      </div>
    </div>
  );
}
