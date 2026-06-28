import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

const seededValue = (index, seed = 59) => {
  const value = Math.sin(index * 83.27 + seed) * 10000;
  return value - Math.floor(value);
};

/**
 * 🧬 O.M.E.G.A. TIER_10: MOLECULAR_ASSEMBLY_COMPONENT
 * Manifests the HUD from fragmented particles into a coherent tactical interface.
 */
const MolecularAssembly = ({ step, onComplete }) => {
  const particles = useMemo(() => {
    return Array.from({ length: 12 }, (_, i) => ({
      id: i,
      x: (seededValue(i, 5) - 0.5) * window.innerWidth * 1.5,
      y: (seededValue(i, 9) - 0.5) * window.innerHeight * 1.5,
      rotate: seededValue(i, 13) * 360,
    }));
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-[999] flex items-center justify-center">
      <div className="relative w-full h-full">
        {/* ⚛️ PARTICLE_CONVERGENCE_FIELD */}
        {particles.map((particle, i) => (
          <motion.div
            key={particle.id}
            initial={{ 
              x: particle.x,
              y: particle.y,
              rotate: particle.rotate,
              opacity: 0,
              filter: 'blur(10px)'
            }}
            animate={step > 0 ? {
              x: 0,
              y: 0,
              rotate: 0,
              opacity: [0, 0.8, 0],
              filter: 'blur(2px)',
              scale: [1.5, 0.5, 1.2]
            } : {}}
            transition={{ 
              duration: 2.5, 
              delay: i * 0.1,
              ease: [0.23, 1, 0.32, 1]
            }}
            className="absolute w-20 h-0.5 bg-cyan-400/30"
            style={{ 
              top: '50%', 
              left: '50%',
              boxShadow: '0 0 15px rgba(0, 240, 255, 0.5)'
            }}
          />
        ))}

        {/* 💠 CORE_SNAP_FLASH */}
        {step === 5 && (
          <motion.div
            initial={{ scale: 0, opacity: 0, filter: 'blur(20px)' }}
            animate={{ scale: [0, 4, 1], opacity: [0, 1, 0], filter: ['blur(20px)', 'blur(0px)', 'blur(40px)'] }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            onAnimationComplete={onComplete}
            className="absolute inset-0 bg-white/20"
          />
        )}
        
        {/* 🛰️ TACTICAL_GRID_MANIFEST */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={step > 2 ? { opacity: [0, 0.15, 0.05] } : {}}
          transition={{ duration: 3 }}
          className="absolute inset-0"
          style={{
            backgroundImage: 'linear-gradient(rgba(0, 240, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 240, 255, 0.05) 1px, transparent 1px)',
            backgroundSize: '100px 100px'
          }}
        />
      </div>
    </div>
  );
};

export default MolecularAssembly;
