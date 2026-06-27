"use client";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatResponse } from "@/lib/api";
import ConfidenceGauge from "./ConfidenceGauge";
import AgentTimeline from "./AgentTimeline";
import SourceCards from "./SourceCards";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  data?: ChatResponse;
  timestamp: Date;
}

interface Props {
  message: Message;
  showExplainability?: boolean;
}

export default function MessageBubble({ message, showExplainability = true }: Props) {
  const isUser = message.role === "user";
  const data = message.data;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"} gap-3 mb-4`}
    >
      {/* AI avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-xl bg-farm-gradient flex items-center justify-center text-sm shrink-0 mt-1 shadow-farm">
          🌾
        </div>
      )}

      <div className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"} max-w-[85%]`}>
        {/* Main bubble */}
        {isUser ? (
          <div className="chat-bubble-user">
            <p className="text-sm leading-relaxed">{message.content}</p>
          </div>
        ) : (
          <div className="chat-bubble-ai">
            <div className="prose-farm text-sm leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs text-gray-400 px-1">
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          {data && (
            <span className="ml-2 text-farm-500">
              · {data.total_latency_ms?.toFixed(0)}ms
              · {data.agents_invoked?.length} agents
            </span>
          )}
        </p>

        {/* Explainability panel (only for AI messages with data) */}
        {!isUser && data && showExplainability && (
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="w-full space-y-3"
            >
              {/* Disease confidence gauge */}
              {data.disease && (
                <div className="glass-card p-4 w-full">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-base">🔬</span>
                    <p className="text-xs font-bold text-gray-700 dark:text-white uppercase tracking-wide">
                      Disease Analysis
                    </p>
                    {data.disease.hitl_required && (
                      <span className="ml-auto text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-semibold">
                        ⚠️ Review Needed
                      </span>
                    )}
                  </div>
                  <ConfidenceGauge
                    confidence={data.disease.confidence}
                    label={data.disease.name}
                    alternatives={data.disease.alternatives}
                  />
                  {data.disease.symptoms?.length > 0 && (
                    <div className="mt-3">
                      <p className="text-xs font-semibold text-gray-500 mb-1.5">Symptoms observed:</p>
                      <div className="flex flex-wrap gap-1">
                        {data.disease.symptoms.map((s, i) => (
                          <span key={i} className="text-xs bg-farm-50 dark:bg-farm-950/40 text-farm-700 dark:text-farm-300 px-2 py-0.5 rounded-full border border-farm-200 dark:border-farm-800">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Risk scores */}
              {data.risk_scores && (
                <div className="glass-card p-4 w-full">
                  <p className="text-xs font-bold text-gray-700 dark:text-white uppercase tracking-wide mb-3">
                    ⚠️ Risk Assessment
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(data.risk_scores)
                      .filter(([k]) => k !== "overall_risk")
                      .map(([key, val]) => {
                        const pct = Math.round((val as number) * 100);
                        return (
                          <div key={key}>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-gray-500 dark:text-gray-400 capitalize">
                                {key.replace("_risk", "").replace("_", " ")}
                              </span>
                              <span className={`font-semibold ${
                                pct > 65 ? "text-red-500" : pct > 40 ? "text-amber-500" : "text-farm-600"
                              }`}>{pct}%</span>
                            </div>
                            <div className="confidence-bar-track h-1.5">
                              <motion.div
                                className={`h-1.5 rounded-full transition-all ${
                                  pct > 65 ? "bg-red-500" : pct > 40 ? "bg-amber-500" : "bg-farm-500"
                                }`}
                                initial={{ width: 0 }}
                                animate={{ width: `${pct}%` }}
                                transition={{ duration: 0.8, delay: 0.2 }}
                              />
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </div>
              )}

              {/* Agent timeline */}
              {data.execution_timeline && data.execution_timeline.length > 0 && (
                <div className="glass-card p-4 w-full">
                  <AgentTimeline timeline={data.execution_timeline} />
                </div>
              )}

              {/* Source cards */}
              {data.source_documents && data.source_documents.length > 0 && (
                <div className="glass-card p-4 w-full">
                  <p className="text-xs font-bold text-gray-700 dark:text-white uppercase tracking-wide mb-3">
                    📌 Sources
                  </p>
                  <SourceCards sources={data.source_documents} />
                </div>
              )}

              {/* Evaluation score */}
              {data.evaluation && (
                <div className="flex items-center gap-2 px-1">
                  <div className="flex gap-1">
                    {data.evaluation.metrics?.map((m: any, i: number) => (
                      <div key={i} title={`${m.metric}: ${m.details}`}
                        className={`w-2 h-2 rounded-full ${
                          m.label === "pass" ? "bg-farm-500" :
                          m.label === "warn" ? "bg-amber-500" : "bg-red-500"
                        }`} />
                    ))}
                  </div>
                  <p className="text-xs text-gray-400">
                    Evaluation: {data.evaluation.evaluation_summary}
                  </p>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-xl bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-sm shrink-0 mt-1">
          👨‍🌾
        </div>
      )}
    </motion.div>
  );
}
