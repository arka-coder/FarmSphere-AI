"use client";
import { motion, AnimatePresence } from "framer-motion";
import type { AgentTrace } from "@/lib/api";

interface Props {
  timeline: AgentTrace[];
  isStreaming?: boolean;
  activeAgent?: string;
}

const AGENT_META: Record<string, { label: string; color: string }> = {
  orchestrator:             { label: "Orchestrator",      color: "#8b5cf6" },
  disease_agent:            { label: "Disease Agent",     color: "#f43f5e" },
  knowledge_agent:          { label: "Knowledge Agent",   color: "#3b82f6" },
  weather_agent:            { label: "Weather Agent",     color: "#0ea5e9" },
  seasonal_agent:           { label: "Seasonal Agent",    color: "#10b981" },
  risk_agent:               { label: "Risk Agent",        color: "#f59e0b" },
  recommendation_agent:     { label: "Recommendation",    color: "#eab308" },
  explainability_agent:     { label: "Explainability",    color: "#6366f1" },
  translation_agent:        { label: "Translation",       color: "#14b8a6" },
  memory_agent:             { label: "Memory Agent",      color: "#64748b" },
  scheme_agent:             { label: "Schemes Agent",     color: "#22c55e" },
  market_agent:             { label: "Market Agent",      color: "#10b981" },
  crop_calendar_agent:      { label: "Crop Calendar",     color: "#84cc16" },
  alert_agent:              { label: "Alert Agent",       color: "#f97316" },
  satellite_agent:          { label: "Satellite Agent",   color: "#60a5fa" },
  scenario_simulation_agent:{ label: "Simulator",         color: "#a855f7" },
  community_agent:          { label: "Community Agent",   color: "#ec4899" },
  sustainability_agent:     { label: "Sustainability",    color: "#22c55e" },
};

export default function AgentTimeline({ timeline, isStreaming, activeAgent }: Props) {
  if (!timeline.length && !activeAgent) return null;

  return (
    <div className="space-y-0.5">
      <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: "#475569" }}>
        Agent Execution Timeline
      </p>
      <AnimatePresence>
        {timeline.map((step, i) => {
          const meta = AGENT_META[step.agent] ?? { label: step.display_name, color: "#64748b" };
          const statusColor =
            step.status === "success" ? "#10b981" :
            step.status === "error"   ? "#f43f5e" : "#475569";

          return (
            <motion.div
              key={step.agent + i}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05, duration: 0.25 }}
              className="timeline-step"
            >
              <div className="timeline-dot" style={{ background: statusColor, boxShadow: `0 0 6px ${statusColor}80` }} />
              <div className="flex items-start justify-between gap-2 pb-3.5">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold truncate" style={{ color: "#0f172a" }}>
                      {meta.label}
                    </span>
                    <span className="text-xs px-1.5 py-0.5 rounded-md font-medium shrink-0"
                      style={{ background: `${meta.color}18`, color: meta.color, border: `1px solid ${meta.color}30` }}>
                      {step.status}
                    </span>
                  </div>
                  {step.output_summary && (
                    <p className="text-xs mt-0.5 leading-relaxed line-clamp-2" style={{ color: "#64748b" }}>
                      {step.output_summary}
                    </p>
                  )}
                </div>
                <span className="text-xs font-mono shrink-0 mt-0.5" style={{ color: "#475569" }}>
                  {step.duration_ms.toFixed(0)}ms
                </span>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* Active streaming agent */}
      {isStreaming && activeAgent && (
        <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} className="timeline-step">
          <div className="timeline-dot timeline-dot-running" />
          <div className="flex items-center gap-2 pb-3">
            <p className="text-xs font-semibold" style={{ color: "#8b5cf6" }}>
              {AGENT_META[activeAgent]?.label ?? activeAgent.replace(/_/g, " ")}
            </p>
            <div className="flex gap-0.5">
              {[0, 1, 2].map(n => (
                <motion.div key={n}
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ repeat: Infinity, duration: 1, delay: n * 0.2 }}
                  className="w-1 h-1 rounded-full"
                  style={{ background: "#8b5cf6" }}
                />
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
