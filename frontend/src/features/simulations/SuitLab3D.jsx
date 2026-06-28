import React, { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// 🧬 O.M.E.G.A. TIER_12: SUIT_LAB_CONTENT (Hook Container)
const SuitLabContent = ({ themeColor: _themeColor, vitals, rigRef }) => {
    useFrame(() => {
        if (!rigRef.current) return;
        
        const time = performance.now() / 1000;
        
        // Smooth rotation and floating animation
        rigRef.current.rotation.y += 0.005;
        rigRef.current.position.y = Math.sin(time * 0.8) * 0.05;
        
        // 🚀 SYNAPTIC_PULSE: SCALE JITTER ON NEURAL LOAD
        const synaptic = vitals?.synaptic || 0;
        const pulse = 1 + (Math.sin(time * 10) * (synaptic > 99 ? 0.02 : 0.005));
        rigRef.current.scale.set(pulse * 1.2, pulse * 1.2, pulse * 1.2);
    });

    return null;
};

export default function SuitLab3D({ themeColor = "#00f0ff", vitals = {} }) {
    const rigRef = useRef();
    
    // 🌀 Generating high-fidelity wireframe geometry
    const radius = 1.2;

    return (
        <group ref={rigRef} scale={[1.2, 1.2, 1.2]}>
            {/* Inject Hook Logic */}
            <SuitLabContent themeColor={themeColor} vitals={vitals} rigRef={rigRef} />

            {/* 🛡️ THE_CORE: SUIT_CHASSIS_VISUALIZER */}
            <mesh>
                <octahedronGeometry args={[radius, 2]} />
                <meshBasicMaterial color={themeColor} wireframe transparent opacity={0.3} />
            </mesh>

            {/* ⚛️ RESONANCE_RINGS */}
            {Array.from({ length: 3 }).map((_, i) => (
                <mesh key={i} rotation={[Math.PI / (i + 1), i, 0]}>
                    <torusGeometry args={[radius + 0.3 + i * 0.1, 0.01, 16, 100]} />
                    <meshBasicMaterial color={themeColor} transparent opacity={0.15 - i * 0.04} />
                </mesh>
            ))}

            {/* 🛰️ TELEMETRY_NODES */}
            <points>
                <sphereGeometry args={[radius + 0.1, 16, 16]} />
                <pointsMaterial size={0.02} color={themeColor} transparent opacity={0.6} blending={THREE.AdditiveBlending} />
            </points>

            {/* ⚡ SYNAPTIC_CONNECTOR_BEAMS */}
            <gridHelper args={[radius * 3, 10, themeColor, themeColor]} rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
                <meshBasicMaterial transparent opacity={0.05} />
            </gridHelper>
        </group>
    );
}
