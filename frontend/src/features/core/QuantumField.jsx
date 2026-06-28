import React, { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const seededValue = (index, seed = 23) => {
    const value = Math.sin(index * 43.13 + seed) * 10000;
    return value - Math.floor(value);
};

export default function QuantumField({ progress }) {
    const pointsRef = useRef();
    const count = 2000;
    
    const positions = React.useMemo(() => {
        const p = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            p[i * 3] = (seededValue(i, 3) - 0.5) * 10;
            p[i * 3 + 1] = (seededValue(i, 7) - 0.5) * 10;
            p[i * 3 + 2] = (seededValue(i, 11) - 0.5) * 10;
        }
        return p;
    }, [count]);

    useFrame(() => {
        if (!pointsRef.current) return;
        
        const t = performance.now() / 1000;
        pointsRef.current.rotation.y = t * 0.1;
        pointsRef.current.rotation.z = t * 0.05;
        const scale = 1 + (progress / 100) * 0.5;
        pointsRef.current.scale.set(scale, scale, scale);
    });

    return (
        <points ref={pointsRef}>
            <bufferGeometry>
                <bufferAttribute
                    attach="attributes-position"
                    count={count}
                    array={positions}
                    itemSize={3}
                />
            </bufferGeometry>
            <pointsMaterial 
                size={0.05} 
                color="#00f0ff" 
                transparent 
                opacity={0.4} 
                blending={THREE.AdditiveBlending}
                sizeAttenuation={true}
            />
        </points>
    );
}
