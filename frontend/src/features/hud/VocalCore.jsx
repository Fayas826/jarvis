import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function VocalCore({ onClick, isListening }) {
  const [pulse, setPulse] = useState(1);

  // Simulate voice reaction if listening
  useEffect(() => {
    if (!isListening) return;

    const interval = setInterval(() => {
      setPulse(1 + Math.random() * 0.4);
    }, 80);
    return () => clearInterval(interval);
  }, [isListening]);

  return (
    <div 
      className="relative flex items-center justify-center cursor-pointer group"
      onClick={onClick}
    >
      {/* Red GALAXY Circuit Background Glow */}
      <div className="absolute w-96 h-96 bg-red-600/10 rounded-full blur-3xl animate-pulse"></div>

      {/* Intricate Outer Rotating Ring (Red) */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="absolute w-[400px] h-[400px] rounded-full border border-red-500/20 border-dashed"
      />

      {/* Yellow/Gold Progress Segment (Inspired by Image) */}
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        className="absolute w-80 h-80 rounded-full border-t-[4px] border-yellow-500/50 border-r-transparent border-l-transparent border-b-transparent"
      />

      {/* Red GALAXY Arc (Inspired by Image) */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        className="absolute w-72 h-72 rounded-full border-b-[6px] border-red-600 border-l-transparent border-r-transparent opacity-80"
      />

      {/* Pulsing Core Circle */}
      <motion.div
        animate={{ 
            scale: isListening ? pulse : 1,
            boxShadow: isListening 
                ? ["0 0 20px rgba(255,0,0,0.4)", "0 0 80px rgba(255,0,0,0.9)", "0 0 20px rgba(255,0,0,0.4)"] 
                : "0 0 30px rgba(255,0,0,0.3)"
        }}
        transition={{ duration: 0.8, repeat: Infinity }}
        className={`w-40 h-40 rounded-full bg-black border-2 border-red-500 flex flex-col items-center justify-center z-10 shadow-[inset_0_0_20px_rgba(255,0,0,0.3)] ${
            isListening ? "border-red-400" : "border-red-600"
        }`}
      >
        <span className="text-red-500 font-bold tracking-[0.4em] text-lg drop-shadow-[0_0_10px_rgba(255,0,0,0.8)]">JARVIS</span>
        <div className="w-16 h-px bg-red-500/40 my-2"></div>
        <div className="flex gap-1">
             {[1, 2, 3].map(i => (
                 <motion.div 
                    key={i}
                    animate={{ height: isListening ? [4, 12, 4] : 4 }}
                    transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.1 }}
                    className="w-[2px] bg-red-400 rounded-full"
                 />
             ))}
        </div>
      </motion.div>

      {/* GALAXY Circuit Ornaments */}
      {[0, 90, 180, 270].map((deg) => (
        <div 
          key={deg} 
          style={{ transform: `rotate(${deg}deg)` }}
          className="absolute w-[450px] h-px flex justify-between px-10 pointer-events-none"
        >
           <div className="w-10 h-px bg-red-500/30"></div>
           <div className="w-10 h-px bg-red-500/30"></div>
        </div>
      ))}
      
      {/* Rotating Gears (Mechanical Feel) */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        className="absolute w-[500px] h-[500px] opacity-10 pointer-events-none"
        style={{
            backgroundImage: `url('https://www.transparenttextures.com/patterns/carbon-fibre.png')`
        }}
      />
    </div>
  );
}
