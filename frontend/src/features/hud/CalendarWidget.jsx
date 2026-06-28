import React from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function CalendarWidget({ data: _data }) {
  // Simulated intelligence data
  const events = [
    { time: "09:00", title: "Neural Link Calibration", priority: "high" },
    { time: "14:30", title: "Stark-Cloud Sync", priority: "low" }
  ];

  const emails = [
    { from: "P. POTTS", subject: "Board Meeting Prep", encrypted: true },
    { from: "H. HOGAN", subject: "Armor Maintenance", encrypted: false }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex flex-col gap-6 pointer-events-auto w-64"
    >
      {/* 📅 Schedule Subsection */}
      <div className="flex flex-col gap-3">
         <div className="flex justify-between items-center">
            <span className="text-[9px] text-cyan-500/50 font-mono tracking-[0.4em] uppercase font-black">Active_Schedule</span>
            <div className="w-16 h-[1px] bg-cyan-500/20" />
         </div>

         <div className="flex flex-col gap-2">
            {events.map((ev, i) => (
                <div key={i} className="flex gap-4 items-center group transition-all">
                    <div className="flex flex-col items-center">
                        <span className="text-[10px] font-black text-cyan-400">{ev.time}</span>
                        <div className={`w-1 h-1 rounded-full mt-1 ${ev.priority === 'high' ? 'bg-amber-500 animate-pulse shadow-[0_0_5px_orange]' : 'bg-cyan-500/40'}`} />
                    </div>
                    <div className="flex flex-col overflow-hidden">
                        <span className="text-[10px] text-cyan-500/80 truncate uppercase tracking-widest">{ev.title}</span>
                    </div>
                </div>
            ))}
         </div>
      </div>

      {/* 📧 Encrypted Comms Subsection */}
      <div className="flex flex-col gap-3">
         <div className="flex justify-between items-center">
            <span className="text-[9px] text-cyan-500/50 font-mono tracking-[0.4em] uppercase font-black">Encrypted_Comms</span>
            <div className="w-16 h-[1px] bg-cyan-500/20" />
         </div>

         <div className="flex flex-col gap-2">
            {emails.map((email, i) => (
                <div key={i} className="group transition-all">
                    <div className="flex justify-between items-center mb-1">
                        <span className="text-[8px] font-black text-amber-500/60 uppercase">{email.from}</span>
                        {email.encrypted && <div className="text-[8px] text-cyan-400 font-black animate-pulse">SECURE</div>}
                    </div>
                    <span className="text-[10px] text-cyan-500/80 font-mono truncate block uppercase tracking-tighter">
                        {email.subject}
                    </span>
                </div>
            ))}
         </div>
      </div>
      
      {/* Visual Data Flow Indicator */}
      <div className="flex items-center gap-2 mt-2 opacity-30">
         <div className="w-full h-[1px] bg-cyan-700" />
         <span className="text-[7px] text-cyan-500/50 tracking-[0.6em] font-mono whitespace-nowrap">STARK_HUD_V4_COMMS</span>
      </div>
    </motion.div>
  );
}
