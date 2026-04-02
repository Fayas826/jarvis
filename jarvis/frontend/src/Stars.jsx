import { Canvas } from "@react-three/fiber";
import { Stars } from "@react-three/drei";

export default function StarField() {
  return (
    <div className="absolute inset-0 -z-20 pointer-events-none">
      <Canvas>
        <Stars radius={100} depth={50} count={5000} factor={4} fade speed={1} />
      </Canvas>
    </div>
  );
}
