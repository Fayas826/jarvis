import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ManualChatInput({ onSubmit }) {
  const [inputText, setInputText] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [selectedModel, setSelectedModel] = useState("GPT-4o Omniscient");

  const models = ["GPT-4o Omniscient", "Claude 3.5 Sonnet", "Local Llama-3 8B", "O.M.E.G.A. Custom ASIC"];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && onSubmit) {
      onSubmit(inputText);
      setInputText("");
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto pointer-events-auto">
      <form 
        onSubmit={handleSubmit}
        className={`relative flex items-center bg-black/40 backdrop-blur-xl border transition-all duration-300 rounded-2xl overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.5)] ${
          isFocused ? 'border-cyan-500 shadow-[0_0_20px_rgba(0,255,255,0.2)]' : 'border-white/10'
        }`}
      >
        {/* Glow Effect */}
        <AnimatePresence>
          {isFocused && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-transparent to-blue-500/10 pointer-events-none"
            />
          )}
        </AnimatePresence>

        {/* Model Selector (Claude Style) */}
        <div className="pl-4 py-2 border-r border-white/10">
          <select 
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-transparent text-xs font-bold text-cyan-400 outline-none cursor-pointer appearance-none uppercase tracking-widest"
          >
            {models.map(model => (
              <option key={model} value={model} className="bg-black text-white">{model}</option>
            ))}
          </select>
        </div>

        {/* Text Input */}
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Message JARVIS or use Voice-to-Voice..."
          className="w-full bg-transparent text-white placeholder-white/30 px-6 py-4 outline-none font-mono text-sm"
        />

        {/* Action Buttons */}
        <div className="flex items-center gap-2 pr-2">
          {/* Voice Mic Icon (Decorative/Link to Voice) */}
          <button 
            type="button"
            className="p-2 rounded-xl text-white/40 hover:text-cyan-400 hover:bg-white/5 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>

          {/* Send Button */}
          <button 
            type="submit"
            disabled={!inputText.trim()}
            className={`p-2 rounded-xl transition-all ${
              inputText.trim() 
                ? 'bg-cyan-600 text-white shadow-[0_0_10px_cyan]' 
                : 'bg-white/5 text-white/20 cursor-not-allowed'
            }`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </form>
      
      {/* Small Hint Text */}
      <div className="text-center mt-2">
        <span className="text-[9px] text-white/30 font-mono tracking-widest uppercase">
          Neural Link • Manual Override Active
        </span>
      </div>
    </div>
  );
}
