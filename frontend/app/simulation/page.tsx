"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Zap, TrendingDown, TrendingUp, Minus } from "lucide-react";
import toast from "react-hot-toast";
import Sidebar from "@/components/layout/Sidebar";
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
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="bg-gradient-to-r from-violet-600 to-purple-700 rounded-2xl p-6 text-white relative overflow-hidden">
            <div className="absolute -right-8 -top-8 text-8xl opacity-20">🔮</div>
            <h1 className="font-display text-2xl font-bold flex items-center gap-2">
              <Zap size={24} /> Scenario Simulation
            </h1>
            <p className="text-violet-200 mt-1 text-sm">
              Ask "What if?" questions — FarmSphere predicts disease risk, yield impact, and optimal actions.
            </p>
            <div className="mt-3 text-xs text-violet-300 font-medium">
              ⭐ Advanced Feature — Very few agricultural AI systems offer predictive simulation
            </div>
          </div>

          {/* Preset scenarios */}
          <div>
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Quick Scenarios</p>
            <div className="flex flex-wrap gap-2">
              {SCENARIOS.map((s) => (
                <button key={s.label} onClick={() => handleSimulate(s.message)}
                  className="text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-full hover:border-violet-400 hover:text-violet-600 dark:hover:text-violet-400 transition-all">
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Custom input */}
          <div className="flex gap-3">
            <input
              value={scenario}
              onChange={e => setScenario(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSimulate()}
              placeholder='Type your "What if?" question... e.g., "What if temperatures drop to 5°C?"'
              className="flex-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-3 text-sm text-gray-800 dark:text-white placeholder-gray-400 focus:outline-none focus:border-violet-400"
            />
            <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
              onClick={() => handleSimulate()}
              disabled={loading || !scenario}
              className="bg-gradient-to-r from-violet-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold text-sm flex items-center gap-2 disabled:opacity-50">
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
              Simulate
            </motion.button>
          </div>

          {/* Results */}
          <AnimatePresence>
            {loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12">
                <div className="w-16 h-16 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin mx-auto mb-4" />
                <p className="text-violet-600 font-semibold">Running predictive simulation...</p>
                <p className="text-gray-400 text-sm mt-1">AI agents are modeling multi-dimensional agricultural outcomes</p>
              </motion.div>
            )}

            {/* Show AI text response even without structured simulation data */}
            {!loading && response && !sim && (
              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card bg-white dark:bg-gray-900 p-5">
                <p className="font-semibold text-violet-700 dark:text-violet-300 mb-3">🔮 Simulation Result</p>
                <div className="prose-farm text-sm">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{response}</ReactMarkdown>
                </div>
              </motion.div>
            )}

            {result && sim && !loading && (
              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                {/* Scenario header */}
                <div className="bg-violet-50 dark:bg-violet-900/20 border border-violet-200 dark:border-violet-800 rounded-2xl p-4">
                  <p className="text-sm font-bold text-violet-800 dark:text-violet-300">🔮 Simulating: {result.scenario}</p>
                  <p className="text-xs text-violet-600 dark:text-violet-400 mt-1">
                    Simulation confidence: {Math.round((result.confidence_in_simulation || 0.8) * 100)}%
                  </p>
                </div>

                {/* Impact table */}
                <div className="glass-card bg-white dark:bg-gray-900 p-5">
                  <p className="font-semibold text-gray-800 dark:text-white mb-4">📊 Impact Analysis</p>
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
                          className="bg-gray-50 dark:bg-gray-800 rounded-xl p-3 text-center">
                          <span className="text-xl">{metric.icon}</span>
                          <p className="text-xs text-gray-500 mt-1">{metric.label}</p>
                          <p className="text-lg font-bold text-gray-800 dark:text-white mt-1">
                            {metric.isText ? metric.simulated
                              : metric.isYield ? `${metric.simulated}%`
                              : `${Math.round((metric.simulated as number) * 100)}%`}
                          </p>
                          {metric.change && (
                            <div className={`flex items-center justify-center gap-0.5 text-xs font-semibold mt-1 ${
                              isNegative ? "text-red-500" : "text-farm-500"
                            }`}>
                              {isPositiveChange ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                              {metric.change}
                            </div>
                          )}
                        </motion.div>
                      );
                    })}
                  </div>
                </div>

                {/* Key changes + recommendations */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="glass-card bg-white dark:bg-gray-900 p-4">
                    <p className="font-semibold text-gray-700 dark:text-white text-sm mb-3">🔑 Key Changes</p>
                    <ul className="space-y-2">
                      {(sim.key_changes || []).map((c: string, i: number) => (
                        <li key={i} className="flex gap-2 text-xs text-gray-600 dark:text-gray-300">
                          <span className="text-amber-500 shrink-0">→</span>
                          {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="glass-card bg-white dark:bg-gray-900 p-4">
                    <p className="font-semibold text-gray-700 dark:text-white text-sm mb-3">📋 Adapted Actions</p>
                    <ol className="space-y-2">
                      {(sim.adapted_recommendations || []).map((a: string, i: number) => (
                        <li key={i} className="flex gap-2 text-xs text-gray-600 dark:text-gray-300">
                          <span className="w-4 h-4 bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300 rounded-full flex items-center justify-center text-xs font-bold shrink-0">
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
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
                    <p className="text-sm font-bold text-red-700 dark:text-red-300">⏰ Critical Window</p>
                    <p className="text-sm text-red-600 dark:text-red-400 mt-1">{result.critical_window}</p>
                  </div>
                )}

                {/* Full AI response */}
                {response && (
                  <div className="glass-card bg-white dark:bg-gray-900 p-5">
                    <div className="prose-farm text-sm">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{response}</ReactMarkdown>
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </main>
    </div>
  );
}
