import React from "react";
import { motion } from "framer-motion";
import { View } from "@react-three/drei";
import SuitLab3D from "@/features/simulations/SuitLab3D";

export default function ArmorStatusHUD({ data, themeColor, vitals }) {
  if (!data) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      className="fixed bottom-32 left-10 z-[100] w-80 stark-panel p-6 flex flex-col gap-4"
    >
      <div className="flex justify-between items-center mb-2">
        <div className="flex flex-col">
            <span className="text-[10px] font-black tracking-[0.3em] uppercase text-white/40">Armor_Diagnostic</span>
            <span className="text-[14px] font-black tracking-[0.2em] uppercase italic" style={{ color: themeColor }}>MARK_ZENITH_42</span>
        </div>
        <div className="w-3 h-3 rounded-full animate-pulse shadow-[0_0_15px_rgba(0,240,255,0.5)]" style={{ backgroundColor: themeColor }} />
      </div>

      {/* 🔮 3D SUIT VIEWPORT */}
      <div className="w-full h-48 bg-cyan-500/5 border border-cyan-500/10 relative overflow-hidden group">
          <div className="absolute inset-x-0 bottom-4 text-center z-10 pointer-events-none opacity-20">
              <span className="text-[7px] font-mono tracking-[0.5em] uppercase">SYSTEM_MESH_READY</span>
          </div>
          <View className="w-full h-full">
              <ambientLight intensity={0.5} />
              <SuitLab3D themeColor={themeColor} vitals={vitals} />
          </View>
          <div className="absolute top-0 right-0 p-2 opacity-30">
              <span className="text-[6px] font-mono tracking-widest uppercase">ROT_Y: ACTIVE</span>
          </div>
      </div>

      {/* 🧬 Particle Density */}
      <div className="flex flex-col gap-2 mt-2">
        <div className="flex justify-between text-[8px] font-mono uppercase tracking-widest opacity-80">
          <span>Nano_Particle_Density</span>
          <span style={{ color: themeColor }}>{data.particles}</span>
        </div>
        <div className="w-full h-[2px] bg-white/5 rounded-full overflow-hidden relative">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: data.particles }}
            className="h-full relative z-10"
            style={{ backgroundColor: themeColor }}
          />
        </div>
      </div>

      {/* 🧪 Molecular Sync */}
      <div className="flex flex-col gap-2">
        <div className="flex justify-between text-[8px] font-mono uppercase tracking-widest opacity-80">
          <span>Molecular_Cohesion</span>
          <span style={{ color: themeColor }}>{data.molecular_sync}</span>
        </div>
        <div className="w-full h-[2px] bg-white/5 rounded-full overflow-hidden relative">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: data.molecular_sync }}
            className="h-full opacity-60 relative z-10"
            style={{ backgroundColor: themeColor }}
          />
        </div>
      </div>

      {/* 🧬 Bottom Telemetry */}
      <div className="grid grid-cols-2 gap-4 mt-2 border-t border-white/5 pt-4">
         <div className="flex flex-col gap-1">
            <span className="text-[6px] opacity-30 uppercase tracking-widest">Main_Reactor</span>
            <span className="text-[10px] font-black" style={{ color: themeColor }}>{data.reactor}</span>
         </div>
         <div className="flex flex-col gap-1">
            <span className="text-[6px] opacity-30 uppercase tracking-widest">Bio_Regen</span>
            <span className="text-[10px] font-black" style={{ color: themeColor }}>{data.regeneration}</span>
         </div>
      </div>

      <div className="absolute -left-[1px] top-4 bottom-4 w-[2px] opacity-50" style={{ backgroundColor: themeColor }} />
    </motion.div>
  );
}

