import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Edges } from '@react-three/drei'
import * as THREE from 'three'

export default function Canvas4D() {
  const coreRef = useRef<THREE.Group>(null)
  const midRef = useRef<THREE.Group>(null)
  const outerRef = useRef<THREE.Group>(null)
  const particlesRef = useRef<THREE.Points>(null)

  // Particle positions
  const particlesCount = 2000
  const positions = new Float32Array(particlesCount * 3)
  for (let i = 0; i < particlesCount * 3; i++) {
    positions[i] = (Math.random() - 0.5) * 15
  }

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    
    // Mouse interaction for subtle rotation
    const targetX = (state.mouse.x * Math.PI) / 10
    const targetY = (state.mouse.y * Math.PI) / 10

    if (coreRef.current) {
      coreRef.current.rotation.x += 0.01
      coreRef.current.rotation.y += 0.02
      coreRef.current.rotation.x += 0.05 * (targetY - coreRef.current.rotation.x)
      coreRef.current.rotation.y += 0.05 * (targetX - coreRef.current.rotation.y)
    }

    if (midRef.current) {
      midRef.current.rotation.x -= 0.005
      midRef.current.rotation.z += 0.01
      midRef.current.rotation.x += 0.05 * (targetY - midRef.current.rotation.x)
      midRef.current.rotation.y += 0.05 * (targetX - midRef.current.rotation.y)
    }

    if (outerRef.current) {
      outerRef.current.rotation.y -= 0.002
      outerRef.current.rotation.x -= 0.001
    }

    if (particlesRef.current) {
      particlesRef.current.rotation.y = t * 0.05
    }
  })

  return (
    <group>
      <fog attach="fog" args={['#000000', 1, 15]} />
      <ambientLight intensity={0.5} />
      
      {/* Core */}
      <group ref={coreRef}>
        <mesh>
          <boxGeometry args={[1, 1, 1]} />
          <meshBasicMaterial visible={false} />
          <Edges color="#22d3ee" transparent opacity={0.8} />
        </mesh>
      </group>

      {/* Middle Dimension */}
      <group ref={midRef}>
        <mesh>
          <boxGeometry args={[2, 2, 2]} />
          <meshBasicMaterial visible={false} />
          <Edges color="#0ea5e9" transparent opacity={0.3} />
        </mesh>
      </group>

      {/* Outer Void */}
      <group ref={outerRef}>
        <mesh>
          <boxGeometry args={[4, 4, 4]} />
          <meshBasicMaterial visible={false} />
          <Edges color="#38bdf8" transparent opacity={0.1} />
        </mesh>
      </group>

      {/* Particles Data Stream */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particlesCount}
            args={[positions, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.02}
          color="#22d3ee"
          transparent
          opacity={0.5}
          blending={THREE.AdditiveBlending}
        />
      </points>
    </group>
  )
}
