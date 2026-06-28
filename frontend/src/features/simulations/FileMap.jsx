import React from "react";
import { motion, AnimatePresence } from "framer-motion";

const seededValue = (index, seed = 67) => {
  const value = Math.sin(index * 97.13 + seed) * 10000;
  return value - Math.floor(value);
};

export default function FileMap({ files, onFileClick }) {
  const memoizedFiles = React.useMemo(() => {
    const fileList = files ?? [];
    const count = fileList.length || 1;

    return fileList.map((file, i) => {
        const angle = (i / count) * Math.PI * 2;
        const radius = 250 + seededValue(i, 5) * 100;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        return { ...file, x, y, index: i };
    });
  }, [files]);

  if (!files || files.length === 0) return null;

  return (
    <div className="absolute inset-0 z-30 pointer-events-none overflow-hidden">
      <AnimatePresence>
        {memoizedFiles.map((file) => {

          return (
            <motion.div
              key={file.path}
              initial={{ opacity: 0, scale: 0, x: 0, y: 0 }}
              animate={{ 
                opacity: 0.8, 
                scale: 1, 
                x: file.x, 
                y: file.y,
              }}
              exit={{ opacity: 0, scale: 0 }}
              transition={{ 
                type: "spring", 
                stiffness: 100, 
                damping: 20, 
                delay: file.index * 0.1 
              }}
              whileHover={{ scale: 1.2, opacity: 1 }}
              className="absolute left-1/2 top-1/2 -ml-16 -mt-8 w-32 pointer-events-auto cursor-pointer flex flex-col items-center group"
              onClick={() => onFileClick(file.path)}
            >
              {/* The Data Node */}
              <div className="w-4 h-4 rounded-full bg-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.8)] border border-white/20 mb-2 group-hover:bg-amber-400 transition-colors" />
              
              {/* File Label */}
              <div className="bg-black/80 backdrop-blur-md px-3 py-1 rounded border border-cyan-500/20 shadow-xl overflow-hidden">
                <span className="text-[10px] font-mono text-cyan-400 truncate block w-24">
                  {file.name}
                </span>
                <div className="w-full h-px bg-cyan-500/10 mt-1" />
                <span className="text-[7px] text-cyan-600/60 font-mono uppercase tracking-tighter">
                  System.Node_Seq_{file.index+100}
                </span>
              </div>

              {/* Connecting Line to Core (Visual Only) */}
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.1 }}
                className="absolute top-2 left-1/2 h-[500px] w-px bg-linear-to-b from-cyan-400 to-transparent origin-top -z-10 rotate-180"
              />
            </motion.div>
          );
        })}
      </AnimatePresence>
      
      {/* HUD Scanner Overlay */}
      <motion.div 
        animate={{ rotate: 360 }}
        transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
        className="absolute left-1/2 top-1/2 -ml-[400px] -mt-[400px] w-[800px] h-[800px] border border-cyan-500/5 rounded-full border-dashed"
      />
    </div>
  );
}
