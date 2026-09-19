import React from "react";
import { motion } from "framer-motion";

const formatValue = (value, fallback = "SYNC") => {
  if (value === null || value === undefined || value === "") return fallback;
  return value;
};

export default function TopMetrics({ onDiagnostic, status, healthState, worldState, agentState }) {
  const confidence = worldState?.confidence ?? healthState?.confidence ?? 0;
  const risk = worldState?.risk?.level || healthState?.risk?.level || "UNKNOWN";
  const events = worldState?.dimensions?.d4_timeline_events ?? 0;
  const engineStatus = healthState?.status || "BOOTING";
  const lastAgent = agentState?.last_route?.agent_name || agentState?.last_route?.topic || "STANDBY";

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="top-metrics pointer-events-auto cursor-pointer w-full flex flex-col items-end gap-1"
      onClick={onDiagnostic}
    >
      <div className="flex justify-between items-center w-full font-mono text-[8px] tracking-[0.2em] uppercase bg-black/40 px-3 py-1 rounded-sm border border-cyan-500/20 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
         <span className="text-cyan-500/60 font-bold">WORLD_ENGINE</span>
         <span className="text-cyan-400 font-black animate-pulse">{engineStatus}</span>
      </div>

      <div className="grid grid-cols-2 gap-x-3 gap-y-1 w-full font-mono text-[7px] tracking-[0.18em] uppercase opacity-80">
        <div className="flex justify-between gap-1">
          <span className="text-white/40">4D_EVENTS</span>
          <span className="text-cyan-400 font-bold">{events}</span>
        </div>
        <div className="flex justify-between gap-1">
          <span className="text-white/40">5D_CONF</span>
          <span className="text-green-400 font-bold">{formatValue(confidence)}%</span>
        </div>
        <div className="flex justify-between gap-1">
          <span className="text-white/40">RISK</span>
          <span className={risk === "HIGH" || risk === "CRITICAL" ? "text-red-400 font-bold" : "text-amber-300 font-bold"}>{risk}</span>
        </div>
        <div className="flex justify-between gap-1">
          <span className="text-white/40">AURA</span>
          <span className="text-cyan-400 font-bold">{status === "thinking" ? "SYNC" : "LIVE"}</span>
        </div>
      </div>

      <div className="w-full font-mono text-[6px] text-cyan-300/50 tracking-[0.22em] uppercase truncate">
        AGENT_ROUTE: {lastAgent}
      </div>
    </motion.div>
  );
}
