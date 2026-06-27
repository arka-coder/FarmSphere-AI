"use client";
import { motion, AnimatePresence } from "framer-motion";
import type { AgentTrace } from "@/lib/api";

interface Props {
  timeline: AgentTrace[];
  isStreaming?: boolean;
  activeAgent?: string;
}

const AGENT_LABELS: Record<string, { icon: string; color: string }> = {
  orchestrator:             { icon: "🧠", color: "bg-purple-500" },
  disease_agent:            { icon: "🔬", color: "bg-red-500" },
  knowledge_agent:          { icon: "📚", color: "bg-blue-500" },
  weather_agent:            { icon: "🌤️", color: "bg-sky-500" },
  seasonal_agent:           { icon: "📅", color: "bg-emerald-500" },
  risk_agent:               { icon: "⚠️", color: "bg-orange-500" },
  recommendation_agent:     { icon: "💡", color: "bg-yellow-500" },
  explainability_agent:     { icon: "🔍", color: "bg-indigo-500" },
  translation_agent:        { icon: "🌐", color: "bg-teal-500" },
  memory_agent:             { icon: "💾", color: "bg-slate-500" },
  scheme_agent:             { icon: "📋", color: "bg-green-600" },
  market_agent:             { icon: "📈", color: "bg-emerald-600" },
  crop_calendar_agent:      { icon: "🌱", color: "bg-lime-500" },
  alert_agent:              { icon: "🔔", color: "bg-amber-500" },
  satellite_agent:          { icon: "🛰️", color: "bg-blue-600" },
  scenario_simulation_agent:{ icon: "🔮", color: "bg-violet-500" },
  community_agent:          { icon: "👥", color: "bg-pink-500" },
  sustainability_agent:     { icon: "♻️", color: "bg-green-500" },
};

export default function AgentTimeline({ timeline, isStreaming, activeAgent }: Props) {
  if (!timeline.length && !activeAgent) return null;

  return (
    <div className="space-y-1">
      <p className="text-xs font-semibold text-gray-500 dark:text-farm-400 uppercase tracking-wider mb-3">
        Agent Execution Timeline
      </p>
      <AnimatePresence>
        {timeline.map((step, i) => {
          const meta = AGENT_LABELS[step.agent] || { icon: "🤖", color: "bg-gray-500" };
          return (
            <motion.div
              key={step.agent + i}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06, duration: 0.3 }}
              className="timeline-step"
            >
              <div className={`timeline-dot ${
                step.status === "success" ? "timeline-dot-success" :
                step.status === "error" ? "timeline-dot-error" : "timeline-dot-skipped"
              }`} />
              <div className="flex items-start gap-2 pb-3">
                <span className="text-base leading-none mt-0.5">{meta.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-xs font-semibold text-gray-800 dark:text-white truncate">
                      {step.display_name}
                    </p>
                    <span className="text-xs text-gray-400 dark:text-farm-500 shrink-0">
                      {step.duration_ms.toFixed(0)}ms
                    </span>
                  </div>
                  {step.output_summary && (
                    <p className="text-xs text-gray-500 dark:text-farm-400 mt-0.5 leading-relaxed line-clamp-2">
                      {step.output_summary}
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* Streaming active agent */}
      {isStreaming && activeAgent && (
        <motion.div
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          className="timeline-step"
        >
          <div className="timeline-dot timeline-dot-running" />
          <div className="flex items-center gap-2 pb-3">
            <span className="text-base">{AGENT_LABELS[activeAgent]?.icon || "🤖"}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-farm-600 dark:text-farm-400">
                  {activeAgent.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}
                </p>
                <div className="flex gap-0.5">
                  {[0, 1, 2].map(n => (
                    <motion.div key={n} animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ repeat: Infinity, duration: 1, delay: n * 0.2 }}
                      className="w-1 h-1 bg-farm-500 rounded-full" />
                  ))}
                </div>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">Processing...</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
