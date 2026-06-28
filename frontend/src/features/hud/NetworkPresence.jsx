import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/services/api";

export default function NetworkPresence({ active }) {
  const [ghosts, setGhosts] = useState([]);
  const [syncStatus, setSyncStatus] = useState("SEARCHING...");
  const [showQR, setShowQR] = useState(false);
  const [hostIp, setHostIp] = useState("localhost");
  // 🧬 V31.0: SENTIENT_ORIGIN_DETECTION
  const [globalUrl, setGlobalUrl] = useState(() => {
    return window.location.hostname.includes("trycloudflare.com") ? window.location.origin : "";
  });

  useEffect(() => {
    const fetchSync = async () => {
      try {
        
        const res = await api.getGhostSync();
        
        // 🧬 V42.1: ABSOLUTE_ANCHOR_FALLBACK
        const detectedIp = res.data.host_ip || 'localhost';
        const isLoopback = detectedIp === 'localhost' || detectedIp === '127.0.0.1';
        
        let finalUrl = res.data.global_frontend_url;
        
        // Safety Fallback Coordinates (known good LAN IP)
        const safeIp = "10.225.133.36";
        const localUrl = `http://${isLoopback ? safeIp : detectedIp}:5173`;

        // Only fallback to local IP if the tunnel is non-resonant
        if ((!finalUrl || finalUrl === "RESONATING...")) {
            finalUrl = localUrl;
        }

        // Force manifestation of globalUrl even if loopback detected (by using safeIp)
        setGlobalUrl(finalUrl);
        setGhosts(res.data.ghost_devices || []);
        setHostIp(res.data.host_ip || safeIp);

        // Force manifestation of globalUrl even if loopback detected (by using safeIp)
        setGlobalUrl(finalUrl);
        setGhosts(res.data.ghost_devices || []);
        setHostIp(res.data.host_ip || safeIp);
        
        // 🛡️ SECURITY_FEEDBACK_MANIFEST
        const isSecure = finalUrl.startsWith("https");
        setSyncStatus(isSecure ? "SECURE_BRIDGE_ACTIVE" : "VOICE_INHIBITED_HTTP");
      } catch {
        // Absolute fallback if backend is unreachable but we are on a tunnel
        if (window.location.hostname.includes("trycloudflare.com")) {
            setGlobalUrl(window.location.origin);
            setSyncStatus("GHOST_SYNC_ACTIVE");
        } else {
            setSyncStatus("SIGNAL_LOST");
        }
      }
    };

    fetchSync();
    // 🧬 V38.2: STABILIZED_PERSISTENCE (Throttled for Mobile Resonance)
    const burstInterval = setInterval(fetchSync, 5000); 
    
    return () => clearInterval(burstInterval);
  }, []);

  if (!active) return null;

  return (
    <div className="relative flex flex-col items-center pointer-events-none">
      {/* 🧬 NEURAL_SYNC_POPUP (V14_GLOBAL_LOCKED) */}
      <AnimatePresence>
        {showQR && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.8, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 1.1, y: 5 }}
            className="mb-4 p-4 zenith-glass border border-cyan-500/30 rounded-sm bg-black/90 backdrop-blur-3xl z-[1000] w-[200px] pointer-events-auto"
          >
            <div className="flex flex-col items-center gap-2">
              <div className="flex items-center justify-between w-full mb-1">
                <span className="text-[7px] text-cyan-400 font-black tracking-[0.3em] uppercase">SYNC_MATRIX [V19_STABILIZED]</span>
                <button onClick={() => setShowQR(false)} className="text-[8px] text-white/20 hover:text-white transition-colors">✕</button>
              </div>
              <div className="p-2 bg-white rounded-sm">
                {globalUrl ? (
                  <img 
                      src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${globalUrl}&bgcolor=fff&color=000`} 
                      alt="Sync QR" 
                      className="w-[120px] h-[120px] rounded-sm"
                  />
                ) : (
                  <div className="w-[120px] h-[120px] flex items-center justify-center bg-black/10">
                    <span className="text-[6px] text-cyan-400 animate-pulse">SYNCHRONIZING...</span>
                  </div>
                )}
              </div>
              <div className="flex flex-col gap-1 items-center mt-1">
                <span className="text-[6px] text-cyan-400/50 font-mono text-center break-all">
                  {globalUrl ? "GLOBAL_GATEWAY" : "WAITING_FOR_RESONANCE"}
                </span>
                {globalUrl && !globalUrl.startsWith("https") && (
                   <span className="text-[7px] text-red-500 font-black animate-pulse bg-red-500/10 px-2 py-0.5 rounded-full mt-1">
                      VOICE_INHIBITED: INSECURE_LINK
                   </span>
                )}
                {globalUrl && globalUrl.startsWith("https") && (
                   <span className="text-[7px] text-green-400 font-black bg-green-400/10 px-2 py-0.5 rounded-full mt-1">
                      SECURE_CONTEXT_ACTIVE
                   </span>
                )}
                {/* 🛡️ EMERGENCY_FORCE_SYNC (Fail-Safe for Mobile) */}
                {globalUrl && globalUrl.startsWith("https") && window.location.protocol === "http:" && (
                    <button 
                        onClick={() => window.location.href = globalUrl}
                        className="mt-2 px-4 py-1.5 bg-cyan-500/80 hover:bg-cyan-400 text-black font-black text-[8px] tracking-widest rounded-sm animate-bounce"
                    >
                        FORCE SECURE BRIDGE
                    </button>
                )}
                <span className="text-[8px] text-white/40 font-mono text-center break-all mt-1">
                  {globalUrl}
                </span>
                <span className="text-[5px] text-white/10 font-mono text-center mt-2">
                  ID: {hostIp}
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 📡 GHOST_LINK_BAR */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4 px-4 py-2 zenith-glass border border-cyan-500/10 rounded-sm bg-black/40 backdrop-blur-xl pointer-events-auto"
      >
        <div className="flex flex-col">
           <span className="text-[6px] text-cyan-400 font-black tracking-widest uppercase">{syncStatus}</span>
           <span className="text-[8px] text-white/70 font-mono tracking-tighter">
              {ghosts.length} GHOST_NODES_ACTIVE
           </span>
        </div>

        {/* 🏮 NODES */}
        <div className="flex gap-2">
           {ghosts.map((ghost, i) => (
              <div key={i} className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_cyan]" title={ghost.ip} />
           ))}
        </div>

        {/* 🏹 TRIGGER */}
        <button 
          onClick={(e) => {
              e.stopPropagation();
              setShowQR(!showQR);
          }}
          className={`ml-2 px-3 py-1 text-[8px] font-black tracking-[0.2em] transition-all border ${showQR ? 'bg-cyan-500/20 border-cyan-400 text-white' : 'border-white/10 text-white/40 hover:text-cyan-400 hover:border-cyan-500/50'}`}
        >
          {showQR ? "HIDE_MATRIX" : "SCAN_TO_SYNC"}
        </button>
      </motion.div>
    </div>
  );
}
