import React, { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Points, PointMaterial, Float } from "@react-three/drei";
import * as THREE from "three";

/** Deterministic pseudo-random in [0,1) — stable across re-renders (react-hooks/purity). */
const det01 = (i, salt = 0) => {
  const x = Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453;
  return x - Math.floor(x);
};

// 🌌 THE_SINGULARITY_GEOMETRY (Infinite Recursive Points)
const SingularityCloud = ({ color, count = 2000 }) => {
  const pointsRef = useRef();

  const [positions, colors] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const cols = new Float32Array(count * 3);
    const colorObj = new THREE.Color(color);

    for (let i = 0; i < count; i++) {
      const t = det01(i, 0) * Math.PI * 2;
      const r = 0.5 + Math.pow(det01(i, 1), 3) * 4;
      const h = (det01(i, 2) - 0.5) * 2;

      pos[i * 3] = r * Math.cos(t);
      pos[i * 3 + 1] = h * (1 / (r + 0.1)); // Compressed at center
      pos[i * 3 + 2] = r * Math.sin(t);

      cols[i * 3] = colorObj.r + (det01(i, 3) - 0.5) * 0.2;
      cols[i * 3 + 1] = colorObj.g + (det01(i, 4) - 0.5) * 0.2;
      cols[i * 3 + 2] = colorObj.b + (det01(i, 5) - 0.5) * 0.2;
    }
    return [pos, cols];
  }, [count, color]);

  useFrame(() => {
    if (pointsRef.current) {
        const t = performance.now() / 1000;
        pointsRef.current.rotation.y = t * 0.2;
        pointsRef.current.rotation.z = Math.sin(t * 0.1) * 0.2;
        // Pulse towards singularity
        const s = 1 + Math.sin(t * 4) * 0.05;
        pointsRef.current.scale.set(s, s, s);
    }
  });

  return (
    <Points ref={pointsRef} positions={positions} colors={colors} stride={3}>
      <PointMaterial
        transparent
        vertexColors
        size={0.015}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
};

// 🌀 RECURSIVE_DATA_RINGS
const DataRings = ({ color }) => {
    const groupRef = useRef();
    
    useFrame(() => {
        if (groupRef.current) {
            const t = performance.now() / 1000;
            groupRef.current.children.forEach((child, i) => {
                child.rotation.y = t * (0.5 + i * 0.2);
                child.rotation.x = t * (0.1 + i * 0.1);
                const scale = 1 + Math.sin(t * 2 + i) * 0.1;
                child.scale.set(scale, scale, scale);
            });
        }
    });

    return (
        <group ref={groupRef}>
            {[1.2, 1.8, 2.5, 3.5].map((radius, i) => (
                <mesh key={i} rotation={[det01(i, 10) * Math.PI * 2, det01(i, 11) * Math.PI * 2, 0]}>
                    <torusGeometry args={[radius, 0.005, 16, 100]} />
                    <meshBasicMaterial color={color} transparent opacity={0.2 - i * 0.04} />
                </mesh>
            ))}
        </group>
    );
};

export default function ASICore({ themeColor = "#00f0ff" }) {
  return (
    <group>
      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
        <SingularityCloud color={themeColor} />
        <DataRings color={themeColor} />
        
        {/* The Central Singularity Point */}
        <mesh>
          <sphereGeometry args={[0.05, 32, 32]} />
          <meshBasicMaterial color="#ffffff" />
          <pointLight intensity={10} color={themeColor} distance={10} />
        </mesh>
        
        {/* Infinite Depth Glow */}
        <mesh>
            <sphereGeometry args={[4, 32, 32]} />
            <meshBasicMaterial color={themeColor} transparent opacity={0.02} side={THREE.BackSide} />
        </mesh>
      </Float>
      
      <ambientLight intensity={0.2} />
    </group>
  );
}
