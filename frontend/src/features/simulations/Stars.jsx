import { View, Stars } from "@react-three/drei";

export default function StarField({ active = false }) {
  if (!active) return null;
  return (
    <div className="absolute inset-0 -z-20 pointer-events-none">
      <View className="w-full h-full">
        <Stars radius={100} depth={50} count={5000} factor={4} fade speed={1} />
      </View>
    </div>
  );
}
