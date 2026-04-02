import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

function Sphere() {
  return (
    <mesh rotation={[0.4, 0.2, 0]}>
      <sphereGeometry args={[2.5, 64, 64]} />
      <meshStandardMaterial color="#00bfff" wireframe transparent opacity={0.15} />
    </mesh>
  );
}

export default function Globe() {
  return (
    <div className="absolute inset-0 opacity-40 mix-blend-screen pointer-events-none z-0 flex items-center justify-center">
      <Canvas style={{ width: '500px', height: '500px' }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} color="#00bfff" intensity={2} />
        <Sphere />
        <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={1} />
      </Canvas>
    </div>
  );
}
