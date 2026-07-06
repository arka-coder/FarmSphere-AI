"use client";
import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatResponse } from "@/lib/api";
import ConfidenceGauge from "./ConfidenceGauge";
import AgentTimeline from "./AgentTimeline";
import SourceCards from "./SourceCards";
import { Copy, Check, RefreshCw, Bot, User, AlertCircle, Clock, BrainCircuit, CloudSun, Database, ShieldCheck } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  data?: ChatResponse;
  timestamp: Date;
  isLoading?: boolean;
  loadingStage?: string;
  isError?: boolean;
}

interface Props {
  message: Message;
  showExplainability?: boolean;
  elapsedSeconds?: number;
  onRetry?: () => void;
}

export default function MessageBubble({ message, showExplainability = true, elapsedSeconds, onRetry }: Props) {
  const isUser = message.role === "user";
  const data = message.data;
  const [copied, setCopied] = useState(false);
  const [formattedTime, setFormattedTime] = useState<string | null>(null);

  // Defer timestamp to avoid SSR hydration mismatch
  useEffect(() => {
    setFormattedTime(
      message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    );
  }, [message.timestamp]);

  const copyToClipboard = useCallback(() => {
    navigator.clipboard.writeText(message.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [message.content]);

  // Loading skeleton state
  if (message.isLoading) {
    const pipeline = [
      { label: "Vision", icon: BrainCircuit },
      { label: "Weather", icon: CloudSun },
      { label: "Knowledge", icon: Database },
      { label: "Risk", icon: ShieldCheck },
    ];

    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-4 flex max-w-[92%] gap-3"
      >
        {/* AI Avatar */}
        <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
          style={{ background: "linear-gradient(135deg, rgba(34,197,94,0.1), rgba(16,185,129,0.1))", border: "1px solid rgba(34,197,94,0.2)" }}>
          <Bot size={16} style={{ color: "var(--emerald)" }} strokeWidth={1.5} />
        </div>

        <div className="flex-1 space-y-2">
          {/* Stage indicator */}
          <div className="space-y-4 rounded-3xl rounded-tl-sm border border-emerald-100/80 bg-white/82 p-5 shadow-[0_18px_60px_rgba(16,185,129,0.10)] backdrop-blur-2xl">
            {/* Stage label */}
            <div className="flex items-center gap-2.5">
              <div className="flex gap-1">
                {[0, 1, 2].map(n => (
                  <motion.div key={n}
                    animate={{ scale: [1, 1.5, 1], opacity: [0.4, 1, 0.4] }}
                    transition={{ repeat: Infinity, duration: 1, delay: n * 0.25 }}
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ background: "var(--emerald)" }}
                  />
                ))}
              </div>
              <p className="text-xs font-semibold text-slate-600">
                {message.loadingStage ?? "Building field context"}
              </p>
            </div>

            <div className="grid gap-2 sm:grid-cols-4">
              {pipeline.map((step, index) => {
                const Icon = step.icon;
                const isActive = ((elapsedSeconds ?? 0) + index) % 4 === 0;
                return (
                  <div
                    key={step.label}
                    className={`rounded-2xl border px-3 py-3 transition ${
                      isActive
                        ? "border-emerald-200 bg-emerald-50 text-emerald-800 shadow-[0_0_28px_rgba(16,185,129,0.16)]"
                        : "border-slate-200 bg-white/70 text-slate-500"
                    }`}
                  >
                    <Icon size={16} />
                    <p className="mt-2 text-xs font-bold">{step.label}</p>
                  </div>
                );
              })}
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
                <span>Confidence forming</span>
                <span>{Math.min(91, 42 + (elapsedSeconds ?? 0) * 4)}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-blue-400 to-amber-300"
                  initial={{ width: "28%" }}
                  animate={{ width: `${Math.min(91, 42 + (elapsedSeconds ?? 0) * 4)}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>

            {/* Elapsed time + slow warning */}
            {elapsedSeconds !== undefined && elapsedSeconds > 0 && (
              <div className="flex items-center gap-1.5 pt-1">
                <Clock size={12} className="text-slate-400" />
                <p className="text-xs font-medium text-slate-500">
                  {elapsedSeconds}s elapsed
                  {elapsedSeconds > 15 && (
                    <span className="text-amber-500 font-semibold ml-1">
                      · Taking a little longer — the AI is processing your request
                    </span>
                  )}
                </p>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    );
  }

  // Error state
  if (message.isError) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex gap-3 mb-4 max-w-[88%]"
      >
        <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
          style={{ background: "rgba(244,63,94,0.1)", border: "1px solid rgba(244,63,94,0.3)" }}>
          <AlertCircle size={16} style={{ color: "#f43f5e" }} strokeWidth={1.5} />
        </div>
        <div className="rounded-2xl rounded-tl-sm p-4 glass-card bg-rose-50/50 border border-rose-100">
          <p className="text-sm font-medium text-rose-600">{message.content}</p>
          {onRetry && (
            <button onClick={onRetry}
              className="mt-3 flex items-center gap-1.5 text-xs font-bold px-4 py-2 rounded-xl transition-all hover:bg-rose-100 bg-white shadow-sm border border-rose-200 text-rose-500">
              <RefreshCw size={12} /> Retry
            </button>
          )}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`flex ${isUser ? "justify-end" : "justify-start"} gap-3 mb-4 group`}
    >
      {/* AI avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5 bg-gradient-to-br from-emerald-100 to-green-100 border border-emerald-200 shadow-sm">
          <Bot size={16} className="text-primary-green" strokeWidth={1.5} />
        </div>
      )}

      <div className={`flex flex-col gap-1.5 ${isUser ? "items-end" : "items-start"}`}
        style={{ maxWidth: isUser ? "72%" : "88%" }}>

        {/* Bubble */}
        {isUser ? (
          <div className="chat-bubble-user relative">
            <p className="text-sm font-medium leading-relaxed text-white">{message.content}</p>
          </div>
        ) : (
          <div className="chat-bubble-ai relative group/bubble w-full">
            {/* Copy button — appears on hover */}
            <button
              onClick={copyToClipboard}
              className="absolute top-3 right-3 w-7 h-7 rounded-lg flex items-center justify-center opacity-0 group-hover/bubble:opacity-100 transition-opacity bg-white/60 border border-slate-200 shadow-sm hover:bg-white"
              title="Copy response"
            >
              {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} className="text-slate-500" />}
            </button>

            <div className="pr-6">
              {(() => {
                const parts = message.content.split(/(?=^##\s)/gm);
                return (
                  <div className="flex flex-col gap-4">
                    {parts.map((part, index) => {
                      const isHeaderPart = part.startsWith("## ");
                      if (!isHeaderPart) {
                        return (
                          <div key={index} className="prose-farm text-sm">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{part}</ReactMarkdown>
                          </div>
                        );
                      }
                      
                      const lines = part.split("\n");
                      const titleLine = lines[0].replace(/^##\s*/, "");
                      const body = lines.slice(1).join("\n").trim();
                      
                      return (
                        <div key={index} className="rounded-[20px] border border-slate-200/60 bg-white/80 p-5 shadow-[0_8px_30px_rgba(15,23,42,0.04)] backdrop-blur-xl">
                          <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
                            <div className="w-1.5 h-4 bg-emerald-500 rounded-full" />
                            {titleLine}
                          </h3>
                          <div className="prose-farm text-sm">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{body}</ReactMarkdown>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                );
              })()}
            </div>
          </div>

        )}

        {/* Timestamp + latency */}
        <div className={`flex items-center gap-2 px-1 ${isUser ? "flex-row-reverse" : ""}`}>
          <p className="text-xs font-semibold text-slate-400">{formattedTime ?? "--:--"}</p>
          {data && (
            <span className="text-xs font-semibold text-slate-400">
              · {data.total_latency_ms?.toFixed(0)}ms · {data.agents_invoked?.length} agents
            </span>
          )}
        </div>

        {/* Explainability panel */}
        {!isUser && data && showExplainability && (
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="w-full space-y-3 mt-1"
            >
              {/* Disease confidence */}
              {data.disease && (
                <div className="glass-card p-5 w-full bg-white/60">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 rounded-xl flex items-center justify-center bg-violet-100 text-violet-600">
                      <span className="text-sm">🔬</span>
                    </div>
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Disease Analysis</p>
                    {data.disease.hitl_required && (
                      <span className="ml-auto text-xs px-2.5 py-1 rounded-lg font-bold bg-amber-100 text-amber-700 border border-amber-200 shadow-sm">
                        Review Needed
                      </span>
                    )}
                  </div>
                  <ConfidenceGauge
                    confidence={data.disease.confidence}
                    label={data.disease.name}
                    alternatives={data.disease.alternatives}
                  />
                  {data.disease.symptoms?.length > 0 && (
                    <div className="mt-4">
                      <p className="text-xs font-bold mb-2 text-slate-600">Symptoms observed:</p>
                      <div className="flex flex-wrap gap-2">
                        {data.disease.symptoms.map((s: string, i: number) => (
                          <span key={i} className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 border border-slate-200">
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
                <div className="glass-card p-5 w-full bg-white/60">
                  <p className="text-xs font-bold uppercase tracking-wider mb-4 text-slate-500">
                    Risk Assessment
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(data.risk_scores)
                      .filter(([k]) => k !== "overall_risk")
                      .map(([key, val]) => {
                        const pct = Math.round((val as number) * 100);
                        const color = pct > 65 ? "#e11d48" : pct > 40 ? "#f59e0b" : "#10b981";
                        return (
                          <div key={key}>
                            <div className="flex justify-between text-xs mb-2 font-semibold text-slate-600">
                              <span className="capitalize">
                                {key.replace("_risk", "").replace(/_/g, " ")}
                              </span>
                              <span style={{ color }}>{pct}%</span>
                            </div>
                            <div className="h-1.5 rounded-full bg-slate-200 overflow-hidden shadow-inner">
                              <motion.div
                                className="h-full rounded-full"
                                style={{ background: color }}
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
                <div className="glass-card p-5 w-full bg-white/60">
                  <AgentTimeline timeline={data.execution_timeline} />
                </div>
              )}

              {/* Source cards */}
              {data.source_documents && data.source_documents.length > 0 && (
                <div className="glass-card p-5 w-full bg-white/60">
                  <p className="text-xs font-bold uppercase tracking-wider mb-4 text-slate-500">Sources</p>
                  <SourceCards sources={data.source_documents} />
                </div>
              )}

              {/* Evaluation */}
              {data.evaluation && (
                <div className="flex items-center gap-2.5 px-2 py-1">
                  <div className="flex gap-1.5">
                    {data.evaluation.metrics?.map((m: any, i: number) => (
                      <div key={i} title={`${m.metric}: ${m.details}`}
                        className="w-2 h-2 rounded-full shadow-sm"
                        style={{ background: m.label === "pass" ? "#10b981" : m.label === "warn" ? "#f59e0b" : "#e11d48" }} />
                    ))}
                  </div>
                  <p className="text-xs font-medium text-slate-500">
                    {data.evaluation.evaluation_summary}
                  </p>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5 bg-slate-100 border border-slate-200 shadow-sm">
          <User size={16} className="text-slate-500" strokeWidth={1.5} />
        </div>
      )}
    </motion.div>
  );
}
