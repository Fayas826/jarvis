import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function LeftSidebar({ onOpenSettings }) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Mock data for token limits and MCP
  const tokensUsed = 45020;
  const tokensLimit = 100000;
  const tokenPercentage = (tokensUsed / tokensLimit) * 100;

  const mcpServers = [
    { name: "MongoDB", status: "Active", ping: "12ms" },
    { name: "Postman", status: "Active", ping: "45ms" },
    { name: "Firebase", status: "Disconnected", ping: "--" }
  ];

  const chatHistory = [
    { id: 1, title: "Jarvis System Architecture", time: "Today" },
    { id: 2, title: "Optimize Core Routing", time: "Yesterday" },
    { id: 3, title: "Initialize Omega Protocol", time: "Previous 7 Days" },
    { id: 4, title: "Debug React ReferenceError", time: "Previous 7 Days" },
    { id: 5, title: "Voice-to-Voice HUD Concept", time: "Previous 30 Days" }
  ];

  return (
    <>
      {/* Toggle Button - ChatGPT Style (Top Left) */}
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className={`fixed top-4 left-4 z-[2000] p-2 hover:bg-white/10 transition-colors rounded-md ${isExpanded ? 'text-white' : 'text-white/50 hover:text-white bg-black/40 border border-white/10 backdrop-blur-md'}`}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Sidebar Panel - Translucent Iron Man / ChatGPT Style */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ x: -320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -320, opacity: 0 }}
            transition={{ type: "spring", bounce: 0, duration: 0.3 }}
            className="fixed top-0 left-0 bottom-0 w-80 z-[1900] bg-black/40 backdrop-blur-3xl border-r border-white/10 flex flex-col shadow-[20px_0_50px_rgba(0,0,0,0.5)]"
          >
            {/* Top Header & New Chat */}
            <div className="p-4 pt-16 flex items-center justify-between">
              <button className="flex-1 flex items-center gap-2 group hover:bg-white/10 p-2 rounded-lg transition-all border border-transparent hover:border-white/10">
                <div className="p-1 rounded-full bg-cyan-500/20 text-cyan-400 group-hover:bg-cyan-500 group-hover:text-black transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <span className="text-sm font-semibold text-white tracking-wide">New Protocol</span>
              </button>
            </div>

            {/* Scrollable Chat History */}
            <div className="flex-1 overflow-y-auto px-4 pb-4 custom-scrollbar">
              <div className="flex flex-col gap-1">
                {chatHistory.map((chat) => (
                  <button key={chat.id} className="text-left text-sm text-white/70 p-2 hover:bg-white/10 rounded-lg truncate transition-colors hover:text-white group relative">
                    {chat.title}
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-500/50" />
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-500/50" />
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-500/50" />
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Bottom Status & Profile Section */}
            <div className="p-4 border-t border-white/10 flex flex-col gap-4 bg-black/20">
              
              {/* MCP Servers */}
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between px-1">
                  <span className="text-[10px] text-white/40 font-mono tracking-widest uppercase">MCP Links</span>
                  <button onClick={onOpenSettings} className="text-[10px] text-cyan-400 hover:text-cyan-300 font-mono">MANAGE</button>
                </div>
                <div className="flex gap-2">
                  {mcpServers.map((server, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center justify-center p-2 rounded-lg bg-white/5 border border-white/5 relative group cursor-default">
                      <div className={`w-2 h-2 rounded-full mb-1 ${server.status === 'Active' ? 'bg-cyan-500 shadow-[0_0_5px_cyan]' : 'bg-red-500 shadow-[0_0_5px_red]'}`} />
                      <span className="text-[9px] text-white/60 truncate w-full text-center">{server.name}</span>
                      
                      {/* Tooltip */}
                      <div className="absolute -top-8 bg-black border border-white/10 text-[10px] p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                        {server.ping}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Token Limits */}
              <div className="flex flex-col gap-1.5 px-1">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] text-white/40 font-mono tracking-widest uppercase">Tokens (Tier 4)</span>
                  <span className="text-[10px] text-cyan-400 font-mono">{tokenPercentage.toFixed(1)}%</span>
                </div>
                <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${tokenPercentage}%` }}
                    className="h-full bg-cyan-500 shadow-[0_0_10px_cyan]"
                  />
                </div>
              </div>

              {/* User Profile */}
              <button 
                onClick={onOpenSettings}
                className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors mt-2"
              >
                <div className="w-10 h-10 rounded-full bg-linear-to-tr from-cyan-600 to-blue-900 flex items-center justify-center border border-white/20 overflow-hidden">
                  <span className="text-sm font-bold text-white">MF</span>
                </div>
                <div className="flex flex-col items-start">
                  <span className="text-sm font-semibold text-white/90">Master Fayas</span>
                  <span className="text-[10px] text-cyan-400 font-mono">Omniscient Plan</span>
                </div>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white/40 ml-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                </svg>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
