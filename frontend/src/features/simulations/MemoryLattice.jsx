import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Points, PointMaterial } from "@react-three/drei";

/**
 * 🛰️ O.M.E.G.A. LIX: MEMORY_LATTICE_V3 (CINEMATIC_EDITION)
 * FIXED: Nodes now dynamically link in real-time as they drift.
 * VISIBILITY: Boosted opacity and added "Glow Trace" effects.
 */

const MAX_NODES = 40; 
const MAX_CONNECTIONS = 200;

const seededValue = (index, seed = 53) => {
    const value = Math.sin(index * 79.19 + seed) * 10000;
    return value - Math.floor(value);
};

export default function MemoryLattice({ status = 'idle', mode = 'default' }) {
    const pointsRef = useRef();
    const linesRef = useRef();
    const groupRef = useRef();

    // 🧬 Generate initial data
    const [positions, offsets, velocities, lineArray] = useMemo(() => {
        const pos = new Float32Array(MAX_NODES * 3);
        const off = new Float32Array(MAX_NODES);
        const vel = new Float32Array(MAX_NODES * 3);
        const lines = new Float32Array(MAX_CONNECTIONS * 6);

        for (let i = 0; i < MAX_NODES; i++) {
            const r = 5 + seededValue(i, 3) * 5; 
            const theta = 2 * Math.PI * seededValue(i, 7);
            const phi = Math.acos(2 * seededValue(i, 11) - 1);

            pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
            pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
            pos[i * 3 + 2] = r * Math.cos(phi);

            off[i] = seededValue(i, 13) * 100;
            
            vel[i * 3] = (seededValue(i, 17) - 0.5) * 0.01;
            vel[i * 3 + 1] = (seededValue(i, 19) - 0.5) * 0.01;
            vel[i * 3 + 2] = (seededValue(i, 23) - 0.5) * 0.01;
        }
        return [pos, off, vel, lines];
    }, []);

    useFrame((state, delta) => {
        if (!pointsRef.current || !linesRef.current) return;
        
        const time = performance.now() / 1000;
        const nodePositions = pointsRef.current.geometry.attributes.position.array;
        const linePositions = linesRef.current.geometry.attributes.position.array;
        
        let lineIdx = 0;
        for(let k=0; k < linePositions.length; k++) linePositions[k] = 0;

        const isThinking = status === 'thinking';
        const isOffline = mode === 'offline';
        
        for (let i = 0; i < MAX_NODES; i++) {
            const i3 = i * 3;
            const x = nodePositions[i3];
            const y = nodePositions[i3+1];
            const z = nodePositions[i3+2];
            const dist = Math.sqrt(x*x + y*y + z*z);
            
            nodePositions[i3] += velocities[i3] + Math.sin(time + offsets[i]) * 0.005;
            nodePositions[i3+1] += velocities[i3+1] + Math.cos(time + offsets[i] * 0.7) * 0.005;
            nodePositions[i3+2] += velocities[i3+2] + Math.sin(time * 0.5 + offsets[i]) * 0.005;

            if (dist > 15) {
                nodePositions[i3] *= 0.98;
                nodePositions[i3+1] *= 0.98;
                nodePositions[i3+2] *= 0.98;
            }
            if (dist < 4) {
                nodePositions[i3] *= 1.02;
            }

            for (let j = i + 1; j < MAX_NODES; j++) {
                if (lineIdx >= linePositions.length - 6) break;
                
                const j3 = j * 3;
                const dx = nodePositions[i3] - nodePositions[j3];
                const dy = nodePositions[i3+1] - nodePositions[j3+1];
                const dz = nodePositions[i3+2] - nodePositions[j3+2];
                const d2 = dx*dx + dy*dy + dz*dz;
                
                const threshold = isThinking ? 25 : 12;
                if (d2 < threshold) {
                    linePositions[lineIdx++] = nodePositions[i3];
                    linePositions[lineIdx++] = nodePositions[i3+1];
                    linePositions[lineIdx++] = nodePositions[i3+2];
                    linePositions[lineIdx++] = nodePositions[j3];
                    linePositions[lineIdx++] = nodePositions[j3+1];
                    linePositions[lineIdx++] = nodePositions[j3+2];
                }
            }
        }

        pointsRef.current.geometry.attributes.position.needsUpdate = true;
        linesRef.current.geometry.attributes.position.needsUpdate = true;

        if (groupRef.current) {
            groupRef.current.rotation.y += delta * (isThinking ? 0.3 : 0.05);
        }
        linesRef.current.material.opacity = (isOffline ? 0.4 : 0.2) + Math.sin(time * 3) * 0.05;
    });

    const primaryColor = mode === 'offline' ? "#ff0000" : (status === 'listening' ? "#ffb900" : "#00f0ff");

    return (
        <group ref={groupRef}>
            <lineSegments ref={linesRef}>
                <bufferGeometry>
                    <bufferAttribute
                        attach="attributes-position"
                        count={lineArray.length / 3}
                        array={lineArray}
                        itemSize={3}
                    />
                </bufferGeometry>
                <lineBasicMaterial 
                    color={primaryColor} 
                    transparent 
                    opacity={0.3} 
                    blending={THREE.AdditiveBlending} 
                    depthWrite={false}
                />
            </lineSegments>

            <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
                <PointMaterial
                    transparent
                    color={primaryColor}
                    size={0.15}
                    sizeAttenuation={true}
                    depthWrite={false}
                    blending={THREE.AdditiveBlending}
                    opacity={0.8}
                />
            </Points>

            <mesh rotation={[Math.PI / 2, 0, 0]}>
                <torusGeometry args={[10, 0.01, 16, 128]} />
                <meshBasicMaterial color={primaryColor} transparent opacity={0.1} wireframe />
            </mesh>
            <mesh rotation={[0, Math.PI / 4, 0]}>
                <torusGeometry args={[14, 0.005, 16, 100]} />
                <meshBasicMaterial color={primaryColor} transparent opacity={0.05} wireframe />
            </mesh>
        </group>
    );
}
