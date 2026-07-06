"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2 } from "lucide-react";

const AGENT_SEQUENCE = [
  "orchestrator",
  "vision_agent",
  "weather_agent",
  "satellite_agent",
  "knowledge_agent",
  "risk_agent",
  "recommendation_agent",
];

const DISPLAY_NAMES: Record<string, string> = {
  "orchestrator": "Orchestrator",
  "vision_agent": "Vision Analysis",
  "weather_agent": "Weather & Climate",
  "satellite_agent": "Satellite NDVI",
  "knowledge_agent": "Knowledge Retrieval",
  "risk_agent": "Risk Assessment",
  "recommendation_agent": "Final Synthesis",
};

export default function ReasoningChain({ activeAgent, isComplete }: { activeAgent?: string, isComplete?: boolean }) {
  const activeIndex = activeAgent ? AGENT_SEQUENCE.indexOf(activeAgent) : (isComplete ? AGENT_SEQUENCE.length : -1);
  const confidence = isComplete ? 98 : Math.min(95, Math.max(0, (activeIndex + 1) * 14 + 12));

  return (
    <div className="flex flex-col gap-5 p-5 bg-white/40 rounded-3xl border border-slate-100/50 mb-4 shadow-[0_4px_20px_rgba(15,23,42,0.02)] backdrop-blur-md">
      <div className="flex items-center justify-between">
        <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-emerald-600">AI Reasoning Trace</p>
        <span className="text-xs font-bold text-slate-400 font-mono">{confidence}% CONF</span>
      </div>
      
      <div className="flex flex-col gap-3.5">
        <AnimatePresence>
          {AGENT_SEQUENCE.map((agent, i) => {
            const isCompleted = activeIndex > i || isComplete; 
            const isRunning = activeIndex === i && !isComplete;
            const isPending = activeIndex < i && activeIndex !== -1 && !isComplete;
            
            // Hide if not reached yet, but keep it in the DOM conditionally 
            // The prompt says "show execution progress", so showing pending ones faintly is nice.
            return (
              <motion.div 
                key={agent}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: isPending ? 0.3 : 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center gap-4"
              >
                <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border shadow-sm transition-all duration-500 ${
                  isCompleted ? "border-emerald-500 bg-emerald-500 text-white shadow-emerald-500/20" :
                  isRunning ? "border-emerald-400 bg-emerald-50 text-emerald-600 shadow-emerald-400/20 scale-110" :
                  "border-slate-200 bg-slate-50 text-slate-300"
                }`}>
                  {isCompleted ? <Check size={12} strokeWidth={3} /> : 
                   isRunning ? <Loader2 size={12} className="animate-spin" /> : 
                   <span className="w-1.5 h-1.5 rounded-full bg-slate-200" />}
                </div>
                <div className="flex flex-col">
                  <span className={`text-sm font-semibold transition-colors duration-300 ${
                    isCompleted ? "text-slate-700" :
                    isRunning ? "text-emerald-700" :
                    "text-slate-400"
                  }`}>
                    {DISPLAY_NAMES[agent]}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}
