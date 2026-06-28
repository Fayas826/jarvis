import React from "react";
import { Text, Float, MeshDistortMaterial } from "@react-three/drei";
import { Interactive } from "@react-three/xr";

// 🌌 TIER_14: HOLOGRAPHIC_UPLINK (WebXR Evolution)
// Projects JARVIS nodes into 3D AR/VR space.

function DataPanel({ position, title, value, color }) {
    return (
        <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.2}>
            <Interactive onSelect={() => console.log(`Selected ${title}`)}>
                <mesh position={position}>
                    <planeGeometry args={[1.2, 0.6]} />
                    <meshStandardMaterial 
                        color={color} 
                        transparent 
                        opacity={0.1} 
                        emissive={color} 
                        emissiveIntensity={1} 
                    />
                    <Text
                        position={[0, 0.15, 0.05]}
                        fontSize={0.06}
                        color="white"
                    >
                        {title}
                    </Text>
                    <Text
                        position={[0, -0.05, 0.05]}
                        fontSize={0.12}
                        color={color}
                    >
                        {value}
                    </Text>
                </mesh>
            </Interactive>
        </Float>
    );
}

export default function HolographicUplink({ vitals, iotState }) {
    return (
        <group>
            {/* 🧬 Bio-Data Panel - Moved further to the periphery */}
            <DataPanel 
                position={[-4.5, 0.5, -4]} 
                title="PULSE_RESONANCE" 
                value={`${vitals?.heart_rate || '0'} BPM`} 
                color="#ff4444" 
            />

            {/* 🚁 IoT Control Panel - Symmetric positioning */}
            <DataPanel 
                position={[4.5, 0.5, -4]} 
                title="IOT_STATUS" 
                value={iotState?.ROOM_LIGHTS?.status || 'OFFLINE'} 
                color="#44ff44" 
            />

            {/* 🧠 Simplified Core Singularity */}
            <mesh position={[0, -0.5, -5]}>
                <sphereGeometry args={[0.3, 32, 32]} />
                <MeshDistortMaterial
                    color="#00f0ff"
                    speed={2}
                    distort={0.3}
                    transparent
                    opacity={0.3}
                />
            </mesh>
        </group>
    );
}
