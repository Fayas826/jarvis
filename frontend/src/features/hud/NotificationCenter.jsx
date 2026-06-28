import React from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function NotificationCenter({ notifications = [] }) {
  // 🛡️ O.M.E.G.A. STABILITY: FALLBACK FOR EMPTY NOTIFICATIONS
  const displayNotifications = notifications.length > 0 ? notifications : [
    { id: 'boot', title: 'SYSTEM_BOOT', message: 'Neural link established successfully.', type: 'info' },
    { id: 'sec', title: 'SECURITY_HARDENED', message: 'Encryption layer V20.0 active.', type: 'success' }
  ];

  return (
    <div className="fixed top-8 right-10 flex flex-col gap-3 z-[1000] w-72 pointer-events-none">
      <AnimatePresence>
        {displayNotifications.map((note, i) => (
          <motion.div
            key={note.id || i}
            initial={{ opacity: 0, x: 100, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 20, scale: 0.95, filter: "blur(10px)" }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
            className="pointer-events-auto stark-panel p-4 flex flex-col gap-1 relative overflow-hidden group"
          >
            {/* 🧪 GLOSS_GLOW_OVERLAY */}
            <div className="absolute inset-0 bg-linear-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            
            <div className="flex items-center gap-2">
              <div className={`w-1.5 h-1.5 rounded-full ${note.type === 'error' ? 'bg-red-500' : 'bg-cyan-400'} animate-pulse`} />
              <span className="text-[10px] font-black tracking-[0.4em] uppercase text-white/90">
                {note.title}
              </span>
            </div>
            
            <p className="text-[11px] text-white/60 font-medium leading-relaxed mt-1">
              {note.message}
            </p>

            {/* Progress Bar (Simulated for growth metrics) */}
            <div className="mt-2 w-full h-[1px] bg-white/5 relative overflow-hidden">
                <motion.div 
                    initial={{ x: "-100%" }}
                    animate={{ x: "0%" }}
                    transition={{ duration: 3, ease: "linear" }}
                    className="absolute inset-0 bg-linear-to-r from-transparent via-cyan-400/40 to-transparent"
                />
            </div>

            {/* Corner Bracket Parity */}
            <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-white/10" />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
