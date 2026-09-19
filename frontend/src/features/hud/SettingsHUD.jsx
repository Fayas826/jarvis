import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function SettingsHUD({ settings, onUpdate, onClose, onOSControl }) {
  const [activeTab, setActiveTab] = useState("General");

  if (!settings) return null;

  const themes = [
    { name: "OMEGA", color: "#0022ff", label: "OMEGA_PRIME" },
    { name: "AVENGER", color: "#ffb900", label: "GOLDEN_SURGE" },
    { name: "THREAT", color: "#ff2828", label: "CRIMSON_SENTRY" },
    { name: "MEMORY", color: "#b300ff", label: "NEURAL_VAULT" }
  ];

  const profileIcons = {
    desktop: "🖥️",
    creator: "🎨",
    trading: "📈",
    silent: "🤫"
  };

  const tabs = ["General", "User Profile", "API Tokens", "Agents & MCP", "Voice & Audio", "Data & Privacy"];

  const renderTabContent = () => {
    switch (activeTab) {
      case "General":
        return (
          <div className="flex flex-col gap-8">
            {/* 🎨 Neural Link Theme (Color Mode) */}
            <div className="flex flex-col gap-4">
              <span className="text-[10px] text-white/40 font-mono tracking-widest uppercase">NEURAL_LINK_PALETTE</span>
              <div className="grid grid-cols-2 gap-2">
                  {themes.map((t) => (
                      <div 
                          key={t.name}
                          onClick={() => onUpdate({ ...settings, theme: t.name, themeColor: t.color })}
                          className={`p-3 border rounded-lg flex justify-between items-center cursor-pointer transition-all ${settings.theme === t.name ? 'border-cyan-500 bg-cyan-500/10' : 'border-white/5 bg-white/5 hover:border-white/20'}`}
                      >
                          <span className="text-[10px] font-bold tracking-widest uppercase" style={{ color: t.color }}>{t.label}</span>
                          <div className="w-2 h-2 rounded-full shadow-[0_0_5px_currentColor]" style={{ backgroundColor: t.color, color: t.color }} />
                      </div>
                  ))}
              </div>
            </div>

            {/* 🧬 Identity Sync Toggle */}
            <div className="flex flex-col gap-4">
              <span className="text-[10px] text-white/40 font-mono tracking-widest uppercase">SYSTEM_AUTH_MODE</span>
              <div 
                  onClick={() => onUpdate({ ...settings, biometric: !settings.biometric })}
                  className="bg-white/5 p-4 rounded-xl border border-white/10 flex justify-between items-center cursor-pointer hover:border-cyan-500/20 group"
              >
                  <span className="text-[11px] text-cyan-400 font-bold uppercase">BIOMETRIC_LOCK</span>
                  <div className={`w-10 h-5 rounded-full p-1 transition-colors ${settings.biometric ? 'bg-cyan-500' : 'bg-white/10'}`}>
                      <motion.div 
                          animate={{ x: settings.biometric ? 20 : 0 }}
                          className="w-3 h-3 bg-white rounded-full shadow-lg"
                      />
                  </div>
              </div>
            </div>

            {/* 🚀 System Power Override */}
            <div className="flex flex-col gap-4 pt-4 border-t border-white/10">
              <span className="text-[10px] text-red-600/80 font-mono tracking-widest uppercase">POWER_FEDERATION</span>
              <div className="grid grid-cols-2 gap-2">
                  <button 
                      onClick={() => onOSControl && onOSControl("sleep")}
                      className="p-3 bg-white/5 border border-white/10 text-[10px] text-white/40 hover:text-white hover:border-white transition-all uppercase font-bold"
                  >
                      Sleep_Node
                  </button>
                  <button 
                      onClick={() => onOSControl && onOSControl("restart")}
                      className="p-3 bg-amber-500/10 border border-amber-500/20 text-[10px] text-amber-500 hover:bg-amber-500 hover:text-black transition-all uppercase font-bold"
                  >
                      Restart_Core
                  </button>
              </div>
            </div>
          </div>
        );
      case "User Profile":
        return (
          <div className="flex flex-col gap-8">
            <div className="flex items-center gap-6">
              <div className="w-24 h-24 rounded-full bg-linear-to-tr from-cyan-600 to-blue-900 flex items-center justify-center border-4 border-white/10 overflow-hidden relative group cursor-pointer">
                <span className="text-3xl font-bold text-white">MF</span>
                <div className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="text-xs text-white">EDIT</span>
                </div>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-xl font-bold text-white">Master Fayas</span>
                <span className="text-sm text-cyan-400 font-mono">Omniscient Tier Plan</span>
              </div>
            </div>
            
            <div className="flex flex-col gap-4 pt-6 border-t border-white/10">
              <div className="flex flex-col gap-2">
                <label className="text-xs text-white/50 uppercase tracking-wider">Display Name</label>
                <input type="text" defaultValue="Master Fayas" className="p-3 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-cyan-500 transition-colors" />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs text-white/50 uppercase tracking-wider">Email Address</label>
                <input type="text" defaultValue="fayas@omega-neural.ai" className="p-3 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-cyan-500 transition-colors" />
              </div>
              <button className="mt-2 p-3 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg transition-colors">
                Save Profile Changes
              </button>
            </div>
          </div>
        );
      case "API Tokens":
        return (
          <div className="flex flex-col gap-8">
            <div className="flex justify-between items-center bg-cyan-900/20 p-4 rounded-lg border border-cyan-500/30">
              <div className="flex flex-col">
                <span className="text-lg font-bold text-white">Current Usage</span>
                <span className="text-sm text-cyan-400 font-mono">45,020 / 100,000 Tokens (Tier 4)</span>
              </div>
              <button className="p-2 px-4 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg text-sm transition-colors">Upgrade Plan</button>
            </div>

            <div className="flex flex-col gap-4">
              <span className="text-xs text-white/50 uppercase tracking-wider">LLM Provider Keys</span>
              
              <div className="flex flex-col gap-2">
                <label className="text-sm text-white/80">OpenAI API Key</label>
                <input type="password" defaultValue="sk-proj-**********************************" className="p-3 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-cyan-500 transition-colors font-mono text-sm" />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm text-white/80">Anthropic API Key</label>
                <input type="password" placeholder="Enter Anthropic Key..." className="p-3 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-cyan-500 transition-colors font-mono text-sm" />
              </div>

              <button className="mt-2 p-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-lg transition-colors border border-white/10">
                Update Keys
              </button>
            </div>
          </div>
        );
      case "Voice & Audio":
        return (
          <div className="flex flex-col gap-8">
            {/* 🔊 Sonic Gain (Volume) */}
            <div className="flex flex-col gap-4">
              <span className="text-[10px] text-white/40 font-mono tracking-widest uppercase">OMEGA_SONIC_GAIN</span>
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
            
            {/* 📦 Deployment Profiles */}
            <div className="flex flex-col gap-4">
              <span className="text-[10px] text-white/40 font-mono tracking-widest uppercase">VOICE_PROFILES</span>
              <div className="grid grid-cols-2 gap-2">
                  {Object.keys(settings.PROFILES || {}).map((p) => (
                      <div 
                          key={p}
                          onClick={() => onUpdate({ ...settings, profile: p })}
                          className={`p-3 border rounded-lg flex flex-col gap-1 cursor-pointer transition-all ${settings.profile === p ? 'border-cyan-500 bg-cyan-500/10' : 'border-white/5 bg-white/5 hover:border-white/20'}`}
                      >
                          <span className="text-xl">{profileIcons[p] || "🛠️"}</span>
                          <span className="text-[10px] font-bold tracking-widest uppercase text-white/80">{p}</span>
                      </div>
                  ))}
              </div>
            </div>
          </div>
        );
      case "Data & Privacy":
        return (
          <div className="flex flex-col gap-6 text-sm text-white/70">
            <p>Data & Privacy controls are managed centrally by the Meta-Architect Agent in the core backend.</p>
            <div className="p-4 bg-white/5 border border-white/10 rounded-lg flex flex-col gap-2">
              <span className="text-xs font-bold text-white">Local Execution Mode</span>
              <span className="text-xs text-white/50">Ensure all LLM processing remains on local hardware without sending data to external APIs.</span>
              <button className="mt-2 p-2 bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 rounded-md font-bold text-xs uppercase hover:bg-cyan-500/40 transition-colors">Toggle Local Mode</button>
            </div>
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex flex-col gap-2">
              <span className="text-xs font-bold text-red-500">Delete Conversation History</span>
              <span className="text-xs text-white/50">Permanently erase all chat logs, memory states, and session data.</span>
              <button className="mt-2 p-2 bg-red-600 hover:bg-red-500 text-white rounded-md font-bold text-xs uppercase transition-colors">Clear Data</button>
            </div>
          </div>
        );
      case "Agents & MCP":
        return (
          <div className="flex flex-col gap-6 text-sm text-white/70">
            <div className="flex justify-between items-center">
              <p>Model Context Protocol (MCP) bridges active on the local network.</p>
              <button className="p-1.5 px-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded text-xs text-white transition-colors">Add Server</button>
            </div>
            
            <div className="flex flex-col gap-3">
              <div className="p-4 bg-white/5 border border-white/10 rounded-lg flex flex-col gap-2 group hover:border-cyan-500/30 transition-colors cursor-pointer">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-white">MongoDB Toolset</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-cyan-400 uppercase font-mono">12ms</span>
                    <div className="w-2 h-2 rounded-full bg-cyan-500 shadow-[0_0_5px_cyan]" />
                  </div>
                </div>
                <span className="text-xs text-white/50">Provides direct database manipulation capabilities.</span>
              </div>

              <div className="p-4 bg-white/5 border border-white/10 rounded-lg flex flex-col gap-2 group hover:border-cyan-500/30 transition-colors cursor-pointer">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-white">Postman MCP</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-cyan-400 uppercase font-mono">45ms</span>
                    <div className="w-2 h-2 rounded-full bg-cyan-500 shadow-[0_0_5px_cyan]" />
                  </div>
                </div>
                <span className="text-xs text-white/50">Enables API testing and automated request execution.</span>
              </div>

              <div className="p-4 bg-white/5 border border-white/10 rounded-lg flex flex-col gap-2 group hover:border-white/20 transition-colors cursor-pointer opacity-60 hover:opacity-100">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-white">Firebase MCP</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-red-500 uppercase font-mono">Offline</span>
                    <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_5px_red]" />
                  </div>
                </div>
                <span className="text-xs text-white/50">Google Cloud backend synchronization tools.</span>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-[3000] flex items-center justify-center pointer-events-none">
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/60 backdrop-blur-md pointer-events-auto"
        onClick={onClose}
      />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative z-10 w-[800px] h-[600px] bg-[#111] border border-white/10 rounded-2xl shadow-2xl flex overflow-hidden pointer-events-auto"
      >
        {/* Left Sidebar Tabs */}
        <div className="w-1/3 bg-[#0a0a0a] border-r border-white/10 p-4 flex flex-col gap-2">
          <div className="pb-4 mb-2 border-b border-white/10">
            <span className="text-lg font-bold text-white tracking-wide">Settings</span>
          </div>
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`p-3 text-left rounded-lg text-sm transition-all ${
                activeTab === tab ? "bg-white/10 text-white font-semibold" : "text-white/50 hover:bg-white/5 hover:text-white"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Right Content Area */}
        <div className="w-2/3 p-8 overflow-y-auto custom-scrollbar">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-semibold text-white">{activeTab}</h2>
            <button onClick={onClose} className="p-2 text-white/50 hover:text-white rounded-md hover:bg-white/5 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderTabContent()}
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}
