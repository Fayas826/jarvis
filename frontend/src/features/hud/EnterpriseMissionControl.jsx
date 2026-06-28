import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/services/api";
import { useUI } from "@/core/AppStateProvider";

export default function EnterpriseMissionControl({ onClose }) {
  const { addLog } = useUI();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    projectId: "",
    type: "CODE_GEN",
    input: {
      prompt: "",
      requirements: []
    }
  });

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const res = await api.getEnterpriseProjects();
        setProjects(res.data);
        if (res.data.length > 0) {
          setFormData(prev => ({ ...prev, projectId: res.data[0]._id }));
        }
      } catch (err) {
        console.error("Failed to fetch projects", err);
      }
    };
    fetchProjects();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.postEnterpriseTask(formData);
      addLog(`🚀 [ENTERPRISE_MISSION]: New task initiated: ${res.data.type}`);
      onClose();
    } catch (err) {
      addLog(`❌ [MISSION_FAILURE]: Failed to initialize enterprise task.`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
      animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
      exit={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
      className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
    >
      <div className="w-full max-w-xl glass-panel p-8 border border-cyan-500/30 relative overflow-hidden">
        {/* Decorative background elements */}
        <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-amber-500/10 rounded-full blur-3xl" />

        <div className="flex justify-between items-center mb-8">
          <div className="flex flex-col">
            <span className="text-[10px] text-cyan-400 font-mono tracking-[0.4em] uppercase">Enterprise_Core_v4</span>
            <h2 className="text-2xl font-black text-white tracking-widest uppercase">Mission_Control</h2>
          </div>
          <button 
            onClick={onClose}
            className="w-10 h-10 flex items-center justify-center border border-white/10 rounded-full hover:bg-white/5 hover:border-cyan-500/50 transition-all text-white/50"
          >
            ╳
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="flex flex-col gap-2">
              <label className="text-[9px] text-cyan-500/60 font-mono uppercase tracking-widest">Select_Project</label>
              <select 
                value={formData.projectId}
                onChange={(e) => setFormData({ ...formData, projectId: e.target.value })}
                className="bg-white/5 border border-white/10 p-3 text-white text-xs font-mono focus:border-cyan-500 outline-none transition-all rounded-sm"
                required
              >
                <option value="" disabled className="bg-zinc-900">Choose a project...</option>
                {projects.map(p => (
                  <option key={p._id} value={p._id} className="bg-zinc-900">{p.name}</option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-[9px] text-cyan-500/60 font-mono uppercase tracking-widest">Mission_Type</label>
              <select 
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="bg-white/5 border border-white/10 p-3 text-white text-xs font-mono focus:border-cyan-500 outline-none transition-all rounded-sm"
              >
                <option value="CODE_GEN" className="bg-zinc-900">CODE_GENERATION</option>
                <option value="REFACTOR" className="bg-zinc-900">SYSTEM_REFACTOR</option>
                <option value="DEBUG" className="bg-zinc-900">NEURAL_DEBUG</option>
                <option value="DEPLOY" className="bg-zinc-900">INFRA_DEPLOY</option>
              </select>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[9px] text-cyan-500/60 font-mono uppercase tracking-widest">Mission_Directives</label>
            <textarea 
              value={formData.input.prompt}
              onChange={(e) => setFormData({ 
                ...formData, 
                input: { ...formData.input, prompt: e.target.value } 
              })}
              placeholder="Enter your mission requirements here..."
              className="bg-white/5 border border-white/10 p-4 text-white text-xs font-mono focus:border-cyan-500 outline-none transition-all rounded-sm h-32 resize-none"
              required
            />
          </div>

          <div className="pt-4 flex justify-end">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              disabled={loading}
              type="submit"
              className="px-12 py-4 bg-cyan-600 text-black font-black uppercase tracking-[0.2em] text-xs relative group overflow-hidden"
            >
              <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-500 skew-x-12" />
              {loading ? "INITIALIZING..." : "INITIATE_MISSION"}
            </motion.button>
          </div>
        </form>

        <div className="mt-8 pt-4 border-t border-white/5 flex justify-between items-center opacity-40">
           <span className="text-[7px] font-mono tracking-widest uppercase">O.M.E.G.A. Protocol Active</span>
           <div className="flex gap-1">
             <div className="w-1 h-1 bg-cyan-500 rounded-full animate-pulse" />
             <div className="w-1 h-1 bg-cyan-500 rounded-full animate-pulse [animation-delay:0.2s]" />
             <div className="w-1 h-1 bg-cyan-500 rounded-full animate-pulse [animation-delay:0.4s]" />
           </div>
        </div>
      </div>
    </motion.div>
  );
}
