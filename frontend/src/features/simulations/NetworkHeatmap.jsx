import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function NetworkHeatmap() {
  const [nodes, setNodes] = useState([
    { name: "GOOGLE_PRIMARY", status: "STABLE", latency: "24ms" },
    { name: "CLOUDFLARE_EDGE", status: "STABLE", latency: "12ms" },
    { name: "AWS_US_EAST_1", status: "STABLE", latency: "142ms" },
    { name: "GITHUB_MAIN", status: "STABLE", latency: "78ms" },
  ]);

  // 🧪 SENTIENT_DATA_PULSE
  useEffect(() => {
    const interval = setInterval(() => {
      setNodes(prev => prev.map(n => ({
        ...n,
        latency: `${Math.floor(20 + Math.random() * 180)}ms`,
        status: Math.random() > 0.08 ? "STABLE" : "JITTER_WARNING"
      })));
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col gap-3 p-2 w-full">
      <div className="flex flex-col gap-1 px-1">
         <div className="flex justify-between items-center">
            <span className="text-[6px] text-cyan-400 font-black tracking-[0.4em] uppercase opacity-60">LINK_LATENCY</span>
            <motion.div 
               animate={{ opacity: [0.3, 1, 0.3] }}
               transition={{ duration: 2, repeat: Infinity }}
               className="w-1 h-1 rounded-full bg-cyan-400 shadow-[0_0_8px_cyan]" 
            />
         </div>
         <div className="w-full h-[1px] bg-gradient-to-r from-cyan-500/20 to-transparent" />
      </div>

      <div className="grid grid-cols-1 gap-3">
        {nodes.map((node, i) => (
          <div key={i} className="flex flex-col gap-1 relative px-1">
            <div className="flex justify-between items-end">
                <span className="text-[6px] text-cyan-500/40 font-mono tracking-widest uppercase truncate max-w-[100px]">{node.name}</span>
                <span className={`text-[8px] font-mono font-black ${node.status === 'STABLE' ? 'text-cyan-400' : 'text-red-500'}`}>
                    {node.latency}
                </span>
            </div>
            
            <div className="h-[1.5px] w-full bg-cyan-500/5 rounded-full overflow-hidden">
                <motion.div 
                    initial={{ width: "0%" }}
                    animate={{ 
                        width: `${Math.min(100, (parseInt(node.latency) / 2))}%`,
                        backgroundColor: node.status === 'STABLE' ? "rgba(34, 211, 238, 0.6)" : "rgba(239, 68, 68, 0.6)"
                    }}
                    transition={{ type: "spring", stiffness: 50, damping: 20 }}
                    className="h-full rounded-full"
                />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-1 px-1 flex items-center justify-between font-mono text-[5px] text-white/10 tracking-[0.3em] uppercase">
         <span>Sync_OK</span>
         <span className="text-cyan-500/20">V4.2.1</span>
      </div>
    </div>
  );
}
