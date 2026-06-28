import React, { useMemo, useRef } from "react";
import { Canvas, useFrame, extend } from "@react-three/fiber";
import { Points, PointMaterial, shaderMaterial, OrbitControls, Float } from "@react-three/drei";
import * as THREE from "three";
import { motion } from "framer-motion";
import { XR, ARButton, Interactive, createXRStore } from "@react-three/xr";
import MemoryLattice from "@/features/simulations/MemoryLattice";
import HolographicUplink from "@/features/simulations/HolographicUplink";
import SuitLab3D from "@/features/simulations/SuitLab3D";
import ASICore from "@/features/simulations/ASICore";

// 🚀 O.M.E.G.A. TIER_15: XR_STORE_SINGLETON (v6 API)
const store = createXRStore();

const seededValue = (index, seed = 29) => {
    const value = Math.sin(index * 61.73 + seed) * 10000;
    return value - Math.floor(value);
};

// 🌀 THE SPECTRAL_SHIELD_SHADER - SSS_TIER_ENERGY_RIPPLE (With Specular Glint)
const SpectralMaterial = shaderMaterial(
  {
    uTime: 0,
    uColor: new THREE.Color("#00f0ff"),
    uIntensity: 0.0,
    uPulse: 0.0,
    uMorph: 0.0,
    uFocus: 0.0,
    uLightPos: new THREE.Vector3(5, 5, 5),
  },
  `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vViewDir;
    varying vec3 vPosition;
    uniform float uTime;
    uniform float uPulse;
    uniform float uFocus;
    uniform vec3 uLightPos;

    // 🌪️ Simplex Noise
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
    vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
    float snoise(vec3 v) {
      const vec2 C = vec2(1.0/6.0, 1.0/3.0);
      const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
      vec3 i  = floor(v + dot(v, C.yyy));
      vec3 x0 = v - i + dot(i, C.xxx);
      vec3 g = step(x0.yzx, x0.xyz);
      vec3 l = 1.0 - g;
      vec3 i1 = min(g.xyz, l.zxy);
      vec3 i2 = max(g.xyz, l.zxy);
      vec3 x1 = x0 - i1 + C.xxx;
      vec3 x2 = x0 - i2 + C.yyy;
      vec3 x3 = x0 - D.yyy;
      i = mod289(i);
      vec4 p = permute(permute(permute(i.z + vec4(0.0, i1.z, i2.z, 1.0)) + i.y + vec4(0.0, i1.y, i2.y, 1.0)) + i.x + vec4(0.0, i1.x, i2.x, 1.0));
      float n_ = 0.142857142857;
      vec3 ns = n_ * D.wyz - D.xzx;
      vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
      vec4 x_ = floor(j * ns.z);
      vec4 y_ = floor(j - 7.0 * x_);
      vec4 x = x_ *ns.x + ns.yyyy;
      vec4 y = y_ *ns.x + ns.yyyy;
      vec4 h = 1.0 - abs(x) - abs(y);
      vec4 b0 = vec4(x.xy, y.xy);
      vec4 b1 = vec4(x.zw, y.zw);
      vec4 s0 = floor(b0)*2.0 + 1.0;
      vec4 s1 = floor(b1)*2.0 + 1.0;
      vec4 sh = -step(h, vec4(0.0));
      vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
      vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
      vec3 p0 = vec3(a0.xy, h.x);
      vec3 p1 = vec3(a0.zw, h.y);
      vec3 p2 = vec3(a1.xy, h.z);
      vec3 p3 = vec3(a1.zw, h.w);
      vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
      p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
      vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
      m = m * m;
      return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
    }

    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      vec4 worldPosition = modelMatrix * vec4(position, 1.0);
      vViewDir = normalize(cameraPosition - worldPosition.xyz);
      vPosition = position;
      
      float ripple = snoise(position * (3.0 + uFocus) + uTime * 0.8) * (0.05 + uPulse * 0.02);
      vec3 newPos = position + vNormal * ripple;
      
      gl_Position = projectionMatrix * modelViewMatrix * vec4(newPos, 1.0);
    }
  `,
  `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vViewDir;
    varying vec3 vPosition;
    uniform vec3 uColor;
    uniform float uIntensity;
    uniform float uTime;
    uniform float uFocus;
    uniform vec3 uLightPos;

    void main() {
      float fresnel = pow(1.5 - dot(vNormal, vViewDir), 3.5);
      vec3 color = uColor * (fresnel + 0.4 + uFocus * 1.5);
      
      // ✨ Specular Glint (Glassy Proof)
      vec3 reflectDir = reflect(-normalize(uLightPos), vNormal);
      float spec = pow(max(dot(vViewDir, reflectDir), 0.0), 128.0) * 1.5;
      
      float neural = sin(vPosition.y * 20.0 + uTime * 4.0) * 0.1;
      float highlight = pow(fresnel, 8.0) * 2.0;
      
      float alpha = fresnel * (uIntensity + uFocus * 0.6) * (0.8 + neural);
      
      gl_FragColor = vec4(color + highlight + spec, alpha);
    }
  `
);

// 🔍 REFRACTION_SHADER (Warping Background Elements)
const RefractionMaterial = shaderMaterial(
  { uTime: 0, uColor: new THREE.Color("#00f0ff"), uTexture: null },
  `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vViewDir;
    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      vViewDir = normalize(-mvPosition.xyz);
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vViewDir;
    uniform vec3 uColor;
    uniform float uTime;
    void main() {
      float fresnel = pow(1.0 - dot(vNormal, vViewDir), 2.0);
      gl_FragColor = vec4(uColor, fresnel * 0.15);
    }
  `
);

extend({ SpectralMaterial, RefractionMaterial });

// 💎 INNER_CORE_SINGULARITY
const InnerSingularity = ({ themeColor, focusValue }) => {
    const meshRef = useRef();
    useFrame(() => {
        if (meshRef.current) {
            const t = performance.now() / 1000;
            meshRef.current.rotation.y -= 0.04;
            const s = 0.7 + Math.sin(t * 6) * 0.02 + focusValue * 0.3;
            meshRef.current.scale.setScalar(s);
        }
    });

    return (
        <mesh ref={meshRef}>
            <sphereGeometry args={[0.42, 32, 32]} />
            <meshBasicMaterial color="#ffffff" transparent opacity={0.9 + focusValue * 0.1} blending={THREE.AdditiveBlending} />
            <pointLight intensity={2 + focusValue * 8} color={themeColor} distance={5} />
        </mesh>
    );
};

// 🌪️ NEURAL_MIST (Volumetric 3D Particle Haze)
const NeuralMist = () => {
    const pointsRef = useRef();
    const count = 100;
    const positions = useMemo(() => {
        const pos = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            const r = 3 + seededValue(i, 5) * 2;
            const theta = seededValue(i, 9) * Math.PI * 2;
            const phi = Math.acos(2 * seededValue(i, 13) - 1);
            pos[i*3] = r * Math.sin(phi) * Math.cos(theta);
            pos[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
            pos[i*3+2] = r * Math.cos(phi);
        }
        return pos;
    }, []);

    useFrame(() => {
        const t = performance.now() / 1000;
        pointsRef.current.rotation.y = t * 0.05;
        pointsRef.current.rotation.x = Math.sin(t * 0.1) * 0.1;
    });

    return (
        <Points ref={pointsRef} positions={positions} stride={3}>
            <PointMaterial transparent color="#00f0ff" size={0.015} sizeAttenuation opacity={0.2} />
        </Points>
    );
};

// 🚁 KINETIC_CAMERA (Smooth Drone Perspektive)
const KineticCamera = () => {
    useFrame((state) => {
        const t = performance.now() / 1000;
        state.camera.position.x = Math.sin(t * 0.5) * 0.5;
        state.camera.position.y = Math.cos(t * 0.3) * 0.5;
        state.camera.lookAt(0, 0, 0);
    });
    return null;
};

// 🛰️ ADVANCED_STARK_RINGS (Hex-Segmented Data Arcs)
const AdvancedStarkRings = ({ themeColor, focusValue }) => {
    const groupRef = useRef();
    
    useFrame(() => {
        if (groupRef.current) {
            const t = performance.now() / 1000;
            groupRef.current.children.forEach((ring, i) => {
                ring.rotation.z += (0.01 + i * 0.005) * (i % 2 === 0 ? 1 : -1);
                ring.rotation.x = Math.sin(t * 0.5 + i) * 0.2;
                const s = 1 + focusValue * 0.1;
                ring.scale.setScalar(s);
            });
        }
    });

    return (
        <group ref={groupRef}>
            {/* 🎯 Precision Target Ring (Shattered) */}
            <mesh rotation={[Math.PI / 2.5, 0, 0]}>
                <ringGeometry args={[1.6, 1.62, 32, 1, 0, Math.PI * 1.6]} />
                <meshBasicMaterial color={themeColor} transparent opacity={0.6} side={THREE.DoubleSide} />
            </mesh>
            {/* 🛡️ Spherical Shield Ring (Precision-Evolved) */}
            <mesh rotation={[-Math.PI / 3, Math.PI / 6, 0]}>
                <ringGeometry args={[1.85, 1.9, 64, 1]} />
                <meshBasicMaterial color={themeColor} transparent opacity={0.3} wireframe />
            </mesh>
            {/* 🚀 Kinetic Data Arcs (Deep) */}
            <mesh rotation={[Math.PI / 4, -Math.PI / 3, 0]}>
                <ringGeometry args={[2.0, 2.02, 128, 1, Math.PI, Math.PI * 0.4]} />
                <meshBasicMaterial color={themeColor} transparent opacity={0.4} side={THREE.DoubleSide} />
            </mesh>
            {/* ⚛️ Singularity Anchor Ring */}
            <mesh rotation={[Math.PI / 2, 0, 0]}>
                <ringGeometry args={[1.3, 1.31, 128, 1]} />
                <meshBasicMaterial color="#ffffff" transparent opacity={0.15} />
            </mesh>
            {/* 🌀 Outer Boundary Ring (Smooth) */}
            <mesh rotation={[0, Math.PI / 2, 0]}>
                <ringGeometry args={[2.4, 2.41, 128, 1]} />
                <meshBasicMaterial color={themeColor} transparent opacity={0.1} />
            </mesh>
            
            {/* 🧊 CONTAINMENT_SPHERE: Organic Lattice Shell */}
            <mesh scale={[1.95, 1.95, 1.95]}>
                <icosahedronGeometry args={[1.2, 1 ]} />
                <meshBasicMaterial 
                    color={themeColor} 
                    transparent 
                    opacity={0.08} 
                    wireframe 
                    blending={THREE.AdditiveBlending}
                />
            </mesh>
        </group>
    );
};

const NeuralConstellation = ({ focusValue }) => {
    const pointsRef = useRef();
    const count = 200;
    const positions = useMemo(() => {
        const pos = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            const theta = seededValue(i, 17) * Math.PI * 2;
            const phi = Math.acos(2 * seededValue(i, 21) - 1);
            const r = 1.6 + seededValue(i, 25) * 0.4;
            pos[i*3] = r * Math.sin(phi) * Math.cos(theta);
            pos[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
            pos[i*3+2] = r * Math.cos(phi);
        }
        return pos;
    }, []);

    useFrame((state) => {
        if (pointsRef.current) {
            const t = performance.now() / 1000;
            
            // 🌀 TURBULENT_FLOW: Dynamic orbital rotation
            pointsRef.current.rotation.y = t * 0.05;
            pointsRef.current.rotation.z = Math.sin(t * 0.2) * 0.1;
            
            // ⚡ PULSE_RESONANCE: Turbulence instead of breathing
            const s = 1.0 + focusValue * 0.2 + Math.sin(t * 4) * 0.02;
            pointsRef.current.scale.setScalar(s);
            
            // Parallax Interaction
            pointsRef.current.rotation.x = THREE.MathUtils.lerp(pointsRef.current.rotation.x, -state.mouse.y * 0.3, 0.05);
            pointsRef.current.rotation.y += THREE.MathUtils.lerp(0, state.mouse.x * 0.15, 0.05);
        }
    });

    return (
        <Points ref={pointsRef} positions={positions} stride={3}>
            <PointMaterial transparent color="#ffffff" size={0.035} sizeAttenuation blending={THREE.AdditiveBlending} opacity={0.7} />
        </Points>
    );
};

const SpectralSurface = ({ themeColor, focusValue }) => {
    const materialRef = useRef();
    useFrame((state) => {
        if (materialRef.current) {
            const t = performance.now() / 1000;
            materialRef.current.uIntensity = 0.85;
            materialRef.current.uFocus = THREE.MathUtils.lerp(materialRef.current.uFocus, focusValue, 0.1);
            materialRef.current.uTime = t;
            materialRef.current.uPulse = Math.sin(t * 3);
            
            if (materialRef.current.uLightPos) {
                materialRef.current.uLightPos.set(
                    Math.sin(t) * 5, 
                    5, 
                    Math.cos(t) * 5
                );
            }
        }
    });

    return (
        <group>
            <mesh>
                <sphereGeometry args={[1.35, 32, 32]} />
                <spectralMaterial 
                    ref={materialRef} 
                    uColor={new THREE.Color(themeColor)} 
                    transparent 
                    blending={THREE.AdditiveBlending} 
                    depthWrite={false}
                />
            </mesh>
            {/* 🛡️ REFRACTIVE_OUTER_SHELL (Proof of Depth) */}
            <mesh>
                <sphereGeometry args={[1.45, 32, 32]} />
                <refractionMaterial 
                    uColor={new THREE.Color(themeColor)} 
                    transparent 
                    side={THREE.DoubleSide} 
                    depthWrite={false}
                />
            </mesh>
        </group>
    );
};

const ParallaxController = () => {
    useFrame((state) => {
        const parallaxGroup = state.scene.getObjectByName("ParallaxLayer");
        if (parallaxGroup) {
            parallaxGroup.rotation.x = THREE.MathUtils.lerp(parallaxGroup.rotation.x, -state.mouse.y * 0.2, 0.1);
            parallaxGroup.rotation.y = THREE.MathUtils.lerp(parallaxGroup.rotation.y, state.mouse.x * 0.2, 0.1);
        }
    });
    return null;
};

export default function ZenithPortal({ status, mode, themeColor, onClick, focusValue, vitals, iotState, showArmory = false }) {

    return (
        <div className="relative aspect-square w-full max-w-[90vh] flex items-center justify-center cursor-pointer select-none" onClick={onClick}>
            <div className="absolute inset-0 z-10">
                <View className="absolute inset-0">
                    <HolographicUplink vitals={vitals} iotState={iotState} />
                    {showArmory && (
                        <group position={[0, 0, 0]} scale={[1.5, 1.5, 1.5]}>
                            <SuitLab3D themeColor={themeColor} vitals={vitals} />
                        </group>
                    )}
                    <ambientLight intensity={0.5} />
                    <KineticCamera />
                    <ParallaxController />
                    <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.2}>
                        <group name="ParallaxLayer">
                            <NeuralConstellation focusValue={focusValue} />
                            <SpectralSurface themeColor={themeColor} focusValue={focusValue} />
                            <InnerSingularity themeColor={themeColor} focusValue={focusValue} />
                            <ASICore themeColor={themeColor} />
                            <AdvancedStarkRings themeColor={themeColor} focusValue={focusValue} />
                            <NeuralMist />
                            <MemoryLattice status={status} mode={mode} />
                        </group>
                    </Float>
                    <OrbitControls enableZoom={false} enablePan={false} makeDefault />
                    
                    {/* 🔘 O.M.E.G.A. TIER_14: XR_AR_ENTRY_NODE */}
                    <Float speed={1} rotationIntensity={0} floatIntensity={0}>
                        <Interactive onSelect={() => console.log("XR_SESSION_START")}>
                            <mesh position={[3, 2, -2]} onClick={() => console.log("FORCE_AR")}>
                                <planeGeometry args={[1, 0.4]} />
                                <meshBasicMaterial color="#00f0ff" transparent opacity={0.1} />
                            </mesh>
                        </Interactive>
                    </Float>
                </View>
            </div>

            <div className="absolute top-10 right-10 z-200 pointer-events-auto">
                <ARButton store={store} className="holographic-btn" />
            </div>

            <div className="absolute inset-0 flex items-center justify-center z-50 pointer-events-none">
                <motion.div 
                    animate={{ scale: 0.85 + focusValue * 0.1 }}
                    className="flex flex-col items-center justify-center"
                >
                    <span className="font-mono text-[14px] font-black tracking-[1.2em] text-white/95 drop-shadow-[0_0_20px_rgba(255,255,255,0.6)]">
                        JARVIS
                        {focusValue > 0.5 && <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ duration: 0.2, repeat: Infinity }} className="absolute -right-6 top-0 text-[10px] text-cyan-400 font-bold">!!</motion.span>}
                    </span>
                    
                    <div className="flex gap-2 items-center mt-2 opacity-50">
                        <div className="w-10 h-px bg-white shadow-[0_0_5px_white]" />
                        <div className="w-4 h-px bg-cyan-400 shadow-[0_0_5px_cyan]" />
                        <div className="w-10 h-px bg-white shadow-[0_0_5px_white]" />
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
