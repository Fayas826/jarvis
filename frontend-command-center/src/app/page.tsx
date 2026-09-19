import React from 'react';

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-white font-sans p-8 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] relative overflow-hidden">
      
      {/* Pitch Black Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-200 h-200 bg-cyan-900 rounded-full mix-blend-screen filter blur-[200px] opacity-10 pointer-events-none"></div>
      
      <div className="relative z-10 max-w-350 mx-auto">
        
        {/* Header */}
        <header className="flex justify-between items-center mb-10 border-b border-zinc-800 pb-6">
          <div className="flex items-center gap-4">
            <div className="w-3 h-3 bg-cyan-400 rounded-full shadow-[0_0_15px_rgba(34,211,238,1)] animate-pulse"></div>
            <h1 className="text-3xl font-black tracking-widest text-white">
              JARVIS <span className="text-cyan-500 font-light">OS</span>
            </h1>
          </div>
          <div className="flex gap-6 items-center">
            <div className="text-xs font-mono text-zinc-500 tracking-wider">
              SERVER <span className="text-cyan-400 ml-2">localhost:3000</span>
            </div>
            <button className="bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 px-6 py-2 rounded-lg transition-all text-xs font-bold tracking-widest uppercase shadow-[0_0_15px_rgba(34,211,238,0.1)]">
              System Settings
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* LEFT SIDEBAR: Admin & SaaS */}
          <div className="space-y-8 lg:col-span-1">
            
            {/* SaaS Premium Module */}
            <div className="bg-zinc-950/80 backdrop-blur-xl border border-zinc-800 rounded-xl p-6 shadow-2xl">
              <h2 className="text-xs font-bold mb-4 text-zinc-500 uppercase tracking-widest">Subscription</h2>
              <div className="mb-4">
                <span className="text-2xl font-black text-white">Enterprise</span>
                <span className="text-zinc-500 text-sm ml-2">Tier</span>
              </div>
              <div className="space-y-3 mb-6">
                <div>
                  <div className="flex justify-between text-xs text-zinc-400 mb-1">
                    <span>API Token Usage</span>
                    <span className="text-cyan-400">84%</span>
                  </div>
                  <div className="h-1 bg-zinc-900 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-500 w-[84%] shadow-[0_0_10px_rgba(34,211,238,0.5)]"></div>
                  </div>
                </div>
              </div>
              <button className="w-full bg-linear-to-r from-zinc-800 to-zinc-900 hover:from-zinc-700 hover:to-zinc-800 text-white border border-zinc-700 py-2 rounded text-xs font-bold uppercase transition-all">
                Manage Billing
              </button>
            </div>

            {/* 4-Tier Admin Management */}
            <div className="bg-zinc-950/80 backdrop-blur-xl border border-zinc-800 rounded-xl p-6 shadow-2xl">
              <h2 className="text-xs font-bold mb-4 text-zinc-500 uppercase tracking-widest">Security Clearance</h2>
              <div className="space-y-2">
                {[
                  { level: 1, name: 'User', desc: 'Basic Monitoring', active: false },
                  { level: 2, name: 'Operator', desc: 'Manual Triggers', active: false },
                  { level: 3, name: 'Architect', desc: 'Sandbox Approval', active: false },
                  { level: 4, name: 'God Mode', desc: 'System Overrides', active: true },
                ].map((tier) => (
                  <div key={tier.level} className={`p-3 rounded-lg border flex items-center gap-4 transition-all cursor-pointer ${tier.active ? 'bg-cyan-950/30 border-cyan-500/50 shadow-[inset_0_0_20px_rgba(34,211,238,0.1)]' : 'bg-black border-zinc-800 hover:border-zinc-700'}`}>
                    <div className={`w-6 h-6 flex items-center justify-center rounded text-xs font-bold ${tier.active ? 'bg-cyan-500 text-black' : 'bg-zinc-800 text-zinc-500'}`}>
                      L{tier.level}
                    </div>
                    <div>
                      <div className={`text-sm font-bold ${tier.active ? 'text-cyan-400' : 'text-zinc-300'}`}>{tier.name}</div>
                      <div className="text-[10px] text-zinc-500 uppercase tracking-wider">{tier.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* MAIN CONTENT */}
          <div className="lg:col-span-3 space-y-8">
            
            {/* MCP Servers */}
            <div className="bg-zinc-950/80 backdrop-blur-xl border border-zinc-800 rounded-xl p-6 shadow-2xl">
              <h2 className="text-xs font-bold mb-6 text-zinc-500 uppercase tracking-widest border-b border-zinc-800 pb-2">MCP Interoperability</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { name: 'MongoDB', status: 'Connected', ping: '12ms' },
                  { name: 'Postman', status: 'Connected', ping: '45ms' },
                  { name: 'Firebase', status: 'Disconnected', ping: '--' },
                ].map((mcp) => (
                  <div key={mcp.name} className="bg-black border border-zinc-800 p-4 rounded-lg flex flex-col justify-between">
                    <div className="flex justify-between items-start mb-4">
                      <span className="font-medium text-white">{mcp.name}</span>
                      <div className={`w-2 h-2 rounded-full ${mcp.status === 'Connected' ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                    </div>
                    <div className="flex justify-between text-xs text-zinc-500">
                      <span>{mcp.status}</span>
                      <span className="font-mono">{mcp.ping}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Cryogenic Agent Registry */}
            <div className="bg-zinc-950/80 backdrop-blur-xl border border-zinc-800 rounded-xl p-6 shadow-2xl">
              <h2 className="text-xs font-bold mb-6 text-zinc-500 uppercase tracking-widest border-b border-zinc-800 pb-2 flex justify-between">
                100-Agent Cryogenic Array
                <span className="text-cyan-400">99 DORMANT / 1 AWAKE</span>
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {['UI/UX Designer', 'Quantum Analyst', 'DB Optimizer', 'Kubernetes Admin', 'Security Pentester', 'React Refactorer', 'System Architect', 'LLM Prompt Eng'].map((agent, i) => (
                  <div key={agent} className={`p-4 rounded-lg border transition-all cursor-pointer ${i === 5 ? 'bg-cyan-950/20 border-cyan-500/50' : 'bg-black border-zinc-800 hover:border-zinc-700'}`}>
                    <div className="text-[10px] text-zinc-600 mb-2 font-mono">AGENT-{String(i+1).padStart(3, '0')}</div>
                    <div className={`text-sm font-medium mb-3 ${i === 5 ? 'text-white' : 'text-zinc-400'}`}>{agent}</div>
                    <div className="flex items-center gap-2">
                      <div className={`w-1.5 h-1.5 rounded-full ${i === 5 ? 'bg-cyan-400 animate-pulse' : 'bg-zinc-700'}`}></div>
                      <span className={`text-[10px] font-bold tracking-wider ${i === 5 ? 'text-cyan-400' : 'text-zinc-600'}`}>
                        {i === 5 ? 'ACTIVE (EXEC)' : 'CRYOSLEEP'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
