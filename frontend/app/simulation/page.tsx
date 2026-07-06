"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Zap, TrendingDown, TrendingUp, Minus } from "lucide-react";
import toast from "react-hot-toast";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import { sendChat } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const SCENARIOS = [
  { label: "🌧️ Rainfall +50%", message: "What if rainfall increases by 50% next week?" },
  { label: "🌡️ Temperature +5°C", message: "What if temperature rises 5 degrees above normal for 2 weeks?" },
  { label: "🏜️ 3-week drought", message: "What if there is no rainfall for the next 3 weeks?" },
  { label: "🦟 Pest outbreak", message: "What if there is a severe pest outbreak next month?" },
  { label: "📉 Price crash 30%", message: "What if crop prices drop by 30% this season?" },
];

export default function SimulationPage() {
  const [scenario, setScenario] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [response, setResponse] = useState("");

  const handleSimulate = async (msg?: string) => {
    const message = msg || scenario;
    if (!message) return;
    setScenario(message);
    setLoading(true);
    setResult(null);
    try {
      const data = await sendChat({
        message,
        crop_type: "tomato",
        location: "Nashik, Maharashtra",
      });
      setResult(data.simulation_results);
      setResponse(data.response);
    } catch (e: any) {
      toast.error("Simulation failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const sim = result?.simulated;
  const baseline = result?.baseline;

  return (
    <div className="flex h-screen bg-base relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-green-50/50 to-emerald-50/30 pointer-events-none" />

      <Sidebar />

      <main className="flex-1 flex flex-col relative overflow-hidden">
        <TopNav />

        <div className="flex-1 overflow-y-auto px-8 pt-28 pb-12 scrollbar-hide">
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="bg-gradient-to-r from-emerald-500 to-green-600 rounded-3xl p-8 text-white relative overflow-hidden shadow-premium-green">
              <div className="absolute -right-8 -top-8 text-8xl opacity-10">🔮</div>
              <h1 className="font-bold text-4xl flex items-center gap-3 tracking-tight drop-shadow-sm">
                <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center backdrop-blur-md">
                  <Zap size={20} className="text-white" strokeWidth={2.5} />
                </div>
                Scenario Simulation
              </h1>
              <p className="text-emerald-50 mt-3 text-base font-medium leading-relaxed max-w-xl">
                Ask "What if?" questions — FarmSphere predicts disease risk, yield impact, and optimal actions.
              </p>
              <div className="mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 backdrop-blur-sm text-xs font-bold uppercase tracking-wider border border-white/20">
                <span className="text-amber-300">★</span> Predictive AI Modeling
              </div>
            </div>

            {/* Preset scenarios */}
            <div>
              <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500 mb-4">Quick Scenarios</p>
              <div className="flex flex-wrap gap-2.5">
                {SCENARIOS.map((s) => (
                  <button key={s.label} onClick={() => handleSimulate(s.message)}
                    suppressHydrationWarning
                    className="text-sm font-semibold bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-xl hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700 transition-all shadow-sm">
                    {s.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom input */}
            <div className="flex gap-3 relative">
              <input
                value={scenario}
                onChange={e => setScenario(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleSimulate()}
                placeholder='Type your "What if?" question... e.g., "What if temperatures drop to 5°C?"'
                className="flex-1 bg-white border border-slate-200 rounded-2xl px-6 py-4 text-base font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-4 focus:ring-emerald-500/10 shadow-sm transition-all"
                suppressHydrationWarning
              />
              <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                onClick={() => handleSimulate()}
                disabled={loading || !scenario}
                suppressHydrationWarning
                className="btn-primary px-8 py-4 rounded-2xl flex items-center gap-2 text-base shadow-sm disabled:opacity-50">
                {loading ? <Loader2 size={20} className="animate-spin" /> : <Zap size={20} strokeWidth={2.5} />}
                Simulate
              </motion.button>
            </div>

            {/* Results */}
            <AnimatePresence>
              {loading && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-16">
                  <div className="w-16 h-16 border-4 border-emerald-100 border-t-emerald-500 rounded-full animate-spin mx-auto mb-6 shadow-sm" />
                  <p className="text-emerald-700 font-bold text-lg">Running predictive simulation...</p>
                  <p className="text-slate-500 font-medium mt-2">AI agents are modeling multi-dimensional agricultural outcomes</p>
                </motion.div>
              )}

              {/* Show AI text response even without structured simulation data */}
              {!loading && response && !sim && (
                <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
                  <p className="font-bold text-emerald-700 mb-4 flex items-center gap-2">
                    <span className="text-lg">🔮</span> Simulation Result
                  </p>
                  <div className="prose-farm text-sm">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{response}</ReactMarkdown>
                  </div>
                </motion.div>
              )}

              {result && sim && !loading && (
                <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  {/* Scenario header */}
                  <div className="bg-emerald-50 border border-emerald-100 rounded-2xl p-5 shadow-sm">
                    <p className="text-base font-bold text-emerald-900 flex items-center gap-2">
                      <span className="text-xl">🔮</span> Simulating: {result.scenario}
                    </p>
                    <p className="text-sm font-semibold text-emerald-600 mt-2 ml-7">
                      Simulation confidence: {Math.round((result.confidence_in_simulation || 0.8) * 100)}%
                    </p>
                  </div>

                  {/* Impact table */}
                  <div className="glass-card p-6">
                    <p className="font-bold text-slate-800 mb-5 flex items-center gap-2 text-lg">
                      <span className="text-xl">📊</span> Impact Analysis
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {[
                        {
                          label: "Disease Risk",
                          baseline: baseline?.disease_risk,
                          simulated: sim.disease_risk,
                          change: sim.disease_risk_change,
                          icon: "🦠",
                        },
                        {
                          label: "Pest Risk",
                          baseline: baseline?.pest_risk,
                          simulated: sim.pest_risk,
                          change: sim.pest_risk_change,
                          icon: "🐛",
                        },
                        {
                          label: "Est. Yield",
                          baseline: 100,
                          simulated: sim.yield_estimate_pct,
                          change: sim.yield_change,
                          icon: "🌾",
                          isYield: true,
                        },
                        {
                          label: "Water Stress",
                          baseline: "Normal",
                          simulated: sim.water_stress,
                          change: null,
                          icon: "💧",
                          isText: true,
                        },
                      ].map((metric, i) => {
                        const isPositiveChange = metric.change?.startsWith("+");
                        const isNegative = metric.isYield ? isPositiveChange === false : isPositiveChange;
                        return (
                          <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.08 }}
                            className="bg-white rounded-2xl p-4 text-center border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                            <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center mx-auto mb-3">
                              <span className="text-2xl">{metric.icon}</span>
                            </div>
                            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">{metric.label}</p>
                            <p className="text-3xl font-light tracking-tight text-slate-800 mt-1">
                              {metric.isText ? metric.simulated
                                : metric.isYield ? `${metric.simulated}%`
                                : `${Math.round((metric.simulated as number) * 100)}%`}
                            </p>
                            {metric.change && (
                              <div className={`flex items-center justify-center gap-1 text-xs font-bold mt-2 px-2 py-1 rounded-lg w-max mx-auto ${
                                isNegative ? "bg-rose-50 text-rose-600" : "bg-emerald-50 text-emerald-600"
                              }`}>
                                {isPositiveChange ? <TrendingUp size={12} strokeWidth={2.5} /> : <TrendingDown size={12} strokeWidth={2.5} />}
                                {metric.change}
                              </div>
                            )}
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Key changes + recommendations */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="glass-card p-6">
                      <p className="font-bold text-slate-800 text-base mb-4 flex items-center gap-2">
                        <span className="text-lg">🔑</span> Key Changes
                      </p>
                      <ul className="space-y-3">
                        {(sim.key_changes || []).map((c: string, i: number) => (
                          <li key={i} className="flex gap-3 text-sm font-medium text-slate-600 leading-relaxed">
                            <span className="text-amber-500 shrink-0 font-black mt-0.5">→</span>
                            {c}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="glass-card p-6">
                      <p className="font-bold text-slate-800 text-base mb-4 flex items-center gap-2">
                        <span className="text-lg">📋</span> Adapted Actions
                      </p>
                      <ol className="space-y-3">
                        {(sim.adapted_recommendations || []).map((a: string, i: number) => (
                          <li key={i} className="flex gap-3 text-sm font-medium text-slate-600 leading-relaxed">
                            <span className="w-5 h-5 bg-emerald-100 text-emerald-700 rounded-lg flex items-center justify-center text-xs font-black shrink-0 mt-0.5">
                              {i + 1}
                            </span>
                            {a}
                          </li>
                        ))}
                      </ol>
                    </div>
                  </div>

                  {/* Critical window */}
                  {result.critical_window && (
                    <div className="bg-rose-50 border border-rose-200 rounded-2xl p-5 shadow-sm">
                      <p className="text-sm font-bold text-rose-700 flex items-center gap-2">
                        <span className="text-lg">⏰</span> Critical Window
                      </p>
                      <p className="text-sm font-semibold text-rose-600 mt-2 ml-7 leading-relaxed">{result.critical_window}</p>
                    </div>
                  )}

                  {/* Full AI response */}
                  {response && (
                    <div className="glass-card p-6">
                      <div className="prose-farm text-sm">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{response}</ReactMarkdown>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
