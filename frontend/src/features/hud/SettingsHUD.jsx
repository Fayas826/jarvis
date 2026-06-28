import React from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function SettingsHUD({ settings, onUpdate, onClose, onOSControl }) {
  if (!settings) return null;

  const themes = [
    { name: "STARK", color: "#0022ff", label: "ZENITH_PRIME" },
    { name: "AVENGER", color: "#ffb900", label: "GOLDEN_AVENGER" },
    { name: "THREAT", color: "#ff2828", label: "CRIMSON_SENTRY" },
    { name: "MEMORY", color: "#b300ff", label: "NEURAL_VAULT" }
  ];

  const profileIcons = {
    desktop: "🖥️",
    creator: "🎨",
    trading: "📈",
    silent: "🤫"
  };

  return (
    <motion.div 
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 100 }}
      className="fixed right-0 top-0 bottom-0 z-200 w-80 bg-black/80 backdrop-blur-3xl border-l border-white/5 p-8 flex flex-col gap-8 shadow-[-50px_0_100px_rgba(0,0,0,0.8)] overflow-y-auto"
    >
      {/* 💠 Header */}
      <div className="flex flex-col gap-2">
         <div className="flex justify-between items-center">
            <span className="text-[10px] text-cyan-400 font-black tracking-[0.4em] uppercase">Tactical_Override</span>
            <button onClick={onClose} className="text-white/40 hover:text-white text-sm">✕</button>
         </div>
          <div className="w-full h-px bg-white/10" />
      </div>

      {/* 📦 Deployment Profiles */}
      <div className="flex flex-col gap-4">
         <span className="text-[9px] text-white/40 font-mono tracking-widest uppercase">DEPLOYMENT_PROFILES</span>
         <div className="grid grid-cols-2 gap-2">
            {Object.keys(settings.PROFILES || {}).map((p) => (
                <div 
                    key={p}
                    onClick={() => onUpdate({ ...settings, profile: p })}
                    className={`p-3 border rounded-lg flex flex-col gap-1 cursor-pointer transition-all ${settings.profile === p ? 'border-cyan-500 bg-cyan-500/10' : 'border-white/5 bg-white/5 hover:border-white/20'}`}
                >
                    <span className="text-xl">{profileIcons[p] || "🛠️"}</span>
                    <span className="text-[9px] font-bold tracking-widest uppercase text-white/80">{p}</span>
                </div>
            ))}
         </div>
      </div>

      {/* 🔊 Sonic Gain (Volume) */}
      <div className="flex flex-col gap-4">
         <span className="text-[9px] text-white/40 font-mono tracking-widest uppercase">STARK_SONIC_GAIN</span>
         <div className="flex items-center gap-4">
            <div className="flex-1 h-1 bg-white/5 rounded-full relative overflow-hidden">
               <motion.div 
                  animate={{ width: `${settings.volume * 100}%` }}
                  className="absolute inset-y-0 bg-cyan-500 shadow-[0_0_10px_cyan]"
               />
            </div>
            <span className="text-xs text-cyan-400 font-mono">{Math.round(settings.volume * 100)}%</span>
         </div>
         <input 
            type="range" min="0" max="1" step="0.01" 
            value={settings.volume} 
            onChange={(e) => {
                const val = parseFloat(e.target.value);
                onUpdate({ ...settings, volume: val });
                onOSControl && onOSControl("volume", Math.round(val * 100));
            }}
            className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-cyan-500"
         />
      </div>

      {/* 🎨 Neural Link Theme (Color Mode) */}
      <div className="flex flex-col gap-4">
         <span className="text-[9px] text-white/40 font-mono tracking-widest uppercase">NEURAL_LINK_PALETTE</span>
         <div className="flex flex-col gap-2">
            {themes.map((t) => (
                <div 
                    key={t.name}
                    onClick={() => onUpdate({ ...settings, theme: t.name, themeColor: t.color })}
                    className={`p-3 border rounded-lg flex justify-between items-center cursor-pointer transition-all ${settings.theme === t.name ? 'border-white/40 bg-white/10' : 'border-white/5 bg-white/5 hover:border-white/20'}`}
                >
                    <span className="text-[10px] font-bold tracking-widest uppercase" style={{ color: t.color }}>{t.label}</span>
                    <div className="w-2 h-2 rounded-full shadow-[0_0_5px_currentColor]" style={{ backgroundColor: t.color, color: t.color }} />
                </div>
            ))}
         </div>
      </div>

      {/* 🧬 Identity Sync Toggle */}
      <div className="flex flex-col gap-4">
         <span className="text-[9px] text-white/40 font-mono tracking-widest uppercase">SYSTEM_AUTH_MODE</span>
         <div 
            onClick={() => onUpdate({ ...settings, biometric: !settings.biometric })}
            className="bg-white/5 p-4 rounded-xl border border-white/10 flex justify-between items-center cursor-pointer hover:border-cyan-500/20 group"
         >
            <span className="text-[10px] text-cyan-400 font-black">BIOMETRIC_LOCK</span>
            <div className={`w-10 h-5 rounded-full p-1 transition-colors ${settings.biometric ? 'bg-cyan-500' : 'bg-white/10'}`}>
                <motion.div 
                    animate={{ x: settings.biometric ? 20 : 0 }}
                    className="w-3 h-3 bg-white rounded-full shadow-lg"
                />
            </div>
         </div>
      </div>

      {/* 🚀 System Power Override */}
      <div className="flex flex-col gap-4">
         <span className="text-[9px] text-red-600/60 font-mono tracking-widest uppercase">POWER_FEDERATION</span>
         <div className="grid grid-cols-2 gap-2">
            <button 
                onClick={() => onOSControl && onOSControl("sleep")}
                className="p-3 bg-white/5 border border-white/10 text-[9px] text-white/40 hover:text-white hover:border-white transition-all uppercase font-black"
            >
                Sleep_Node
            </button>
            <button 
                onClick={() => onOSControl && onOSControl("restart")}
                className="p-3 bg-amber-500/10 border border-amber-500/20 text-[9px] text-amber-500 hover:bg-amber-500 hover:text-black transition-all uppercase font-black"
            >
                Restart_Core
            </button>
         </div>
      </div>

      {/* Visual Data Chain */}
      <div className="mt-auto opacity-20 pointer-events-none">
         {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="flex gap-1 h-3 overflow-hidden">
               {Array.from({ length: 40 }).map((_, j) => (
                  <div key={j} className="text-[6px] font-mono whitespace-nowrap">{Math.random().toString(36).substring(7)}</div>
               ))}
            </div>
         ))}
      </div>
    </motion.div>
  );
}
