import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Points, PointMaterial } from "@react-three/drei";
import * as THREE from "three";
import "./PortalMaterials";

const seededValue = (index, seed = 29) => {
    const value = Math.sin(index * 61.73 + seed) * 10000;
    return value - Math.floor(value);
};

// 💎 INNER_CORE_SINGULARITY
export const InnerSingularity = ({ themeColor, focusValue }) => {
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
export const NeuralMist = () => {
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
        if (pointsRef.current) {
            pointsRef.current.rotation.y = t * 0.05;
            pointsRef.current.rotation.x = Math.sin(t * 0.1) * 0.1;
        }
    });

    return (
        <Points ref={pointsRef} positions={positions} stride={3}>
            <PointMaterial transparent color="#00f0ff" size={0.015} sizeAttenuation opacity={0.2} />
        </Points>
    );
};

// 🛰️ ADVANCED_STARK_RINGS (Hex-Segmented Data Arcs)
export const AdvancedStarkRings = ({ themeColor, focusValue }) => {
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
            <mesh rotation={[Math.PI / 2.5, 0, 0]}>
                <ringGeometry args={[1.6, 1.62, 32, 1, 0, Math.PI * 1.6]} />
                <meshBasicMaterial color={themeColor} transparent opacity={0.6} side={THREE.DoubleSide} />
            </mesh>
            <mesh rotation={[-Math.PI / 3, Math.PI / 6, 0]}>
                <ringGeometry args={[1.85, 1.9, 64, 1]} />
                <meshBasicMaterial color={themeColor} transparent opacity={0.3} wireframe />
            </mesh>
            <mesh rotation={[Math.PI / 4, -Math.PI / 3, 0]}>
                <ringGeometry args={[2.0, 2.02, 128, 1, Math.PI, Math.PI * 0.4]} />
                <meshBasicMaterial color={themeColor} transparent opacity={0.4} side={THREE.DoubleSide} />
            </mesh>
            <mesh rotation={[Math.PI / 2, 0, 0]}>
                <ringGeometry args={[1.3, 1.31, 128, 1]} />
                <meshBasicMaterial color="#ffffff" transparent opacity={0.15} />
            </mesh>
            <mesh rotation={[0, Math.PI / 2, 0]}>
                <ringGeometry args={[2.4, 2.41, 128, 1]} />
                <meshBasicMaterial color={themeColor} transparent opacity={0.1} />
            </mesh>
            
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

export const NeuralConstellation = ({ focusValue }) => {
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
            pointsRef.current.rotation.y = t * 0.05;
            pointsRef.current.rotation.z = Math.sin(t * 0.2) * 0.1;
            const s = 1.0 + focusValue * 0.2 + Math.sin(t * 4) * 0.02;
            pointsRef.current.scale.setScalar(s);
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

export const SpectralSurface = ({ themeColor, focusValue }) => {
    const materialRef = useRef();
    useFrame((_state) => {
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
