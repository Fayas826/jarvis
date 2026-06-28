import React from "react";
import { motion } from "framer-motion";
import NetworkHeatmap from "@/features/simulations/NetworkHeatmap";
import SatelliteMap from "@/features/simulations/SatelliteMap";

export default function RightPanel() {
  const locationMock = { lat: 12.9716, lon: 77.5946, sector: "IND_04" };

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="panel-right zenith-glass w-[220px] p-0 overflow-hidden border-l border-cyan-500/10 shadow-[-20px_0_50px_rgba(0,0,0,0.4)]"
    >
      {/* 🌍 TACTICAL_SATELLITE_OVERLAY */}
      <div className="absolute inset-0 opacity-20 filter grayscale contrast-125">
        <SatelliteMap location={locationMock} />
      </div>

      <div className="relative z-10 p-4 flex flex-col h-full bg-gradient-to-b from-black/60 to-transparent">
        <div className="mb-4">
           <span className="text-[8px] text-cyan-400 font-black tracking-[0.3em] uppercase px-1">NEURAL_LATENCY</span>
           <div className="w-full h-[1px] bg-gradient-to-r from-cyan-500/30 to-transparent mt-1" />
        </div>
        
        <NetworkHeatmap />
        
        <div className="mt-auto pt-3 border-t border-cyan-500/10 flex flex-col gap-1">
            <span className="font-mono text-[6px] text-cyan-400/30 uppercase tracking-[0.5em]">Sector_Authority</span>
            <span className="font-mono text-[8px] text-cyan-400 font-black">ZENITH_NODE_V4.2</span>
        </div>
      </div>
    </motion.div>
  );
}
