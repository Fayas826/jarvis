import React, { useRef, useMemo, useEffect } from "react";
import { useFrame, extend } from "@react-three/fiber";
import { View, OrbitControls, shaderMaterial } from "@react-three/drei";
import { motion } from "framer-motion";
import * as THREE from "three";

// 🌀 O.M.E.G.A. XXV: SPECTRAL_SHIELD_SHADER
const SpectralMaterial = shaderMaterial(
  {
    uTime: 0,
    uColor: new THREE.Color("#ff0000"),
    uIntensity: 0.5,
    uNoiseFreq: 2.0,
    uPulse: 0.0,
  },
  `
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vPosition;
  uniform float uTime;
  uniform float uNoiseFreq;
  uniform float uPulse;

  float hash(float n) { return fract(sin(n) * 43758.5453123); }
  float noise(vec3 x) {
    vec3 p = floor(x);
    vec3 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);
    float n = p.x + p.y * 57.0 + 113.0 * p.z;
    return mix(mix(mix(hash(n + 0.0), hash(n + 1.0), f.x),
                   mix(hash(n + 57.0), hash(n + 58.0), f.x), f.y),
               mix(mix(hash(n + 113.0), hash(n + 114.0), f.x),
                   mix(hash(n + 170.0), hash(n + 171.0), f.x), f.y), f.z);
  }

  void main() {
    vUv = uv;
    vNormal = normalize(normalMatrix * normal);
    vPosition = position;
    float n = noise(position * uNoiseFreq + uTime * 0.5);
    vec3 pos = position + normal * n * 0.12 * (1.0 + uPulse);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
  `,
  `
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vPosition;
  uniform vec3 uColor;
  uniform float uIntensity;
  uniform float uTime;

  void main() {
    float fresnel = pow(1.5 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 3.0);
    vec3 color = uColor * (fresnel + 0.2);
    float scanline = sin(vPosition.y * 45.0 - uTime * 5.0) * 0.08;
    gl_FragColor = vec4(color + scanline, fresnel * uIntensity);
  }
  `
);

extend({ SpectralMaterial });

function SpectralSphere({ isOnline: _isOnline, status, systemPulse, themeColor, vitals }) {
  const meshRef = useRef();
  const materialRef = useRef();
  
  const targetColor = useMemo(() => {
    // 🧬 O.M.E.G.A. VIII: COLOR_SANITIZER
    const cleanColor = typeof themeColor === "string" && themeColor.startsWith("rgba") 
      ? themeColor.replace(/rgba?\((\d+),\s*(\d+),\s*(\d+).*\)/, "rgb($1,$2,$3)")
      : themeColor;
    return new THREE.Color(cleanColor);
  }, [themeColor]);

  useFrame(() => {
    if (!materialRef.current) return;
    
    const t = performance.now() / 1000;
    materialRef.current.uTime = t;
    materialRef.current.uIntensity = THREE.MathUtils.lerp(
        materialRef.current.uIntensity, 
        systemPulse ? 0.9 : 0.4, 
        0.05
    );
    materialRef.current.uColor.lerp(targetColor, 0.08);
    materialRef.current.uPulse = Math.sin(t * 3.5) * 0.05;

    const cpuLoad = vitals?.cpu_load ? parseFloat(vitals.cpu_load) : 0;
    const rotationSpeed = 0.005 + (cpuLoad / 1000); 
    if (meshRef.current) meshRef.current.rotation.y += (status === "thinking" ? rotationSpeed * 3 : rotationSpeed);
  });

  useEffect(() => {
    const currentMesh = meshRef.current;
    return () => {
        if (currentMesh) {
            currentMesh.geometry.dispose();
            if (currentMesh.material) currentMesh.material.dispose();
        }
    };
  }, []);

  return (
    <mesh ref={meshRef} rotation={[0.4, 0.2, 0]}>
      <sphereGeometry args={[2.5, 64, 64]} />
      <spectralMaterial ref={materialRef} transparent depthWrite={false} blending={THREE.AdditiveBlending} />
    </mesh>
  );
}

export default function Globe({ isOnline = false, status = "idle", systemPulse = false, themeColor = "#00f0ff", vitals, minimal = false }) {
  const size = minimal ? 60 : 100;

  return (
    <motion.div 
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 0.9, x: 0 }}
      className={`relative z-[120] pointer-events-none flex flex-col items-center ${minimal ? 'gap-0' : 'gap-4'}`}
    >
      <div 
        className={`relative flex items-center justify-center rounded-full transition-shadow duration-1000 ${minimal ? 'border-none p-0' : 'border p-1 shadow-[0_0_60px_rgba(var(--stark-glow-rgb),0.1)]'}`}
        style={{ 
            width: `${size}px`, 
            height: `${size}px`,
            borderColor: minimal ? 'transparent' : 'rgba(var(--stark-glow-rgb), 0.1)' 
        }}
      >
        {/* 🌀 Cinematic Peripheral Ring (Rotating Telemetry) */}
        {!minimal && (
            <motion.div 
               animate={{ rotate: 360 }}
               transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
               className="absolute inset-[-15px] border rounded-full"
               style={{ borderColor: 'rgba(var(--stark-glow-rgb), 0.1)' }}
            >
               <div 
                className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-black px-2 text-[5px] font-mono tracking-widest uppercase"
                style={{ color: 'var(--stark-glow)' }}
               >
                  ZENITH_NAV_ACTIVE
               </div>
            </motion.div>
        )}

        {/* 💓 Heartbeat Pulse Ring - ABSOLUTE CENTERED */}
        <motion.div 
            animate={{ 
                scale: systemPulse ? 1.1 : 1, 
                opacity: systemPulse ? (minimal ? 0.3 : 0.4) : 0.1 
            }}
            className="absolute inset-0 border rounded-full transition-colors duration-1000"
            style={{ borderColor: 'var(--stark-glow)' }}
        />
        
        <div style={{ width: `${size}px`, height: `${size}px` }} className="flex items-center justify-center">
            <View className="w-full h-full">
                <ambientLight intensity={0.2} />
                <SpectralSphere isOnline={isOnline} status={status} systemPulse={systemPulse} themeColor={themeColor} vitals={vitals} />
                <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={2} />
            </View>
        </div>
      </div>

      {!minimal && (
          <div className="flex flex-col items-center gap-1">
             <span 
                className="text-[5px] transition-colors duration-1000 font-mono tracking-[0.5em] uppercase"
                style={{ color: systemPulse ? 'var(--stark-glow)' : 'rgba(var(--stark-glow-rgb), 0.3)' }}
             >
                Sector_Scan_{status === 'thinking' ? 'Deep' : (vitals?.cpu_load ? `LOAD_${vitals.cpu_load}` : 'Standby')}
             </span>
             <div className="flex gap-1 items-center">
                <div 
                    className="w-1 h-1 rounded-full transition-all duration-1000"
                    style={{ 
                        backgroundColor: systemPulse ? 'var(--stark-glow)' : 'rgba(var(--stark-glow-rgb), 0.1)',
                        boxShadow: systemPulse ? '0 0 8px var(--stark-glow)' : 'none'
                    }} 
                />
                <div 
                    className="w-12 h-[0.5px]" 
                    style={{ backgroundImage: `linear-gradient(to right, rgba(var(--stark-glow-rgb), 0.4), transparent)` }}
                />
             </div>
          </div>
      )}
    </motion.div>
  );
}
