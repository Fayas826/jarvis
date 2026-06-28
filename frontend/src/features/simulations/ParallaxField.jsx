import React, { useMemo } from "react";
import { motion } from "framer-motion";

const seededValue = (index, seed = 41) => {
  const value = Math.sin(index * 49.37 + seed) * 10000;
  return value - Math.floor(value);
};

export default function ParallaxField({ mouseX, mouseY }) {
  // Generate 40 random data points (dots and coordinates)
  const dataPoints = useMemo(() => {
    return Array.from({ length: 40 }).map((_, i) => ({
      id: i,
      x: seededValue(i, 3) * 100,
      y: seededValue(i, 7) * 100,
      z: seededValue(i, 11) * 3 + 1.0, // Reduced depth for GPU stability
      type: seededValue(i, 13) > 0.85 ? "coord" : "dot",
      color: seededValue(i, 17) > 0.95 ? "stark-amber" : "stark-cyan",
      opacity: seededValue(i, 19) * 0.3 + 0.1,
      label: `${seededValue(i, 23).toFixed(4)}X`
    }));
  }, []);

  return (
    <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
        {dataPoints.map((point) => {
           // Create a unique parallax transform for each point based on its Z-depth
           // Higher Z = closer = more movement
           const xOffset = (mouseX - window.innerWidth / 2) * (point.z / 30);
           const yOffset = (mouseY - window.innerHeight / 2) * (point.z / 30);

           return (
             <motion.div
               key={point.id}
               animate={{ 
                 x: xOffset, 
                 y: yOffset,
                 opacity: point.opacity
               }}
               transition={{ type: "spring", stiffness: 30, damping: 20 }}
               style={{ 
                 left: `${point.x}%`, 
                 top: `${point.y}%`,
               }}
               className="absolute flex items-center gap-2"
             >
                {point.type === "dot" ? (
                   <div className={`w-[2px] h-[2px] rounded-full shadow-[0_0_8px_rgba(0,240,255,0.4)] ${
                     point.color === "stark-amber" ? "bg-amber-400" : "bg-cyan-500"
                   }`} />
                ) : (
                   <span className={`text-[7px] font-mono tracking-widest ${
                     point.color === "stark-amber" ? "text-amber-500/30" : "text-cyan-500/20"
                   }`}>
                      {point.label}
                   </span>
                )}
             </motion.div>
           );
        })}
    </div>
  );
}
