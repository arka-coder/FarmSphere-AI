"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Leaf, Zap, Shield, Brain, Globe, BarChart3 } from "lucide-react";

const features = [
  { icon: Brain, label: "17 AI Agents", desc: "LangGraph orchestrated multi-agent system" },
  { icon: Leaf, label: "Disease Detection", desc: "Gemini Vision + ChromaDB RAG diagnosis" },
  { icon: Zap, label: "Scenario Simulation", desc: "Predictive 'What If?' agricultural modeling" },
  { icon: Shield, label: "HITL Safety", desc: "Human-in-the-loop when confidence < 75%" },
  { icon: Globe, label: "Multilingual", desc: "English, Hindi, Bengali support" },
  { icon: BarChart3, label: "Risk Assessment", desc: "Multi-dimensional predictive risk scoring" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-farm-gradient flex flex-col">
      {/* Hero */}
      <div className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20 relative overflow-hidden">
        {/* Background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/5 rounded-full" />
          <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-white/5 rounded-full" />
          <div className="absolute top-1/2 left-1/4 text-9xl opacity-5">🌾</div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="relative z-10 max-w-4xl"
        >
          <div className="inline-flex items-center gap-2 bg-white/10 border border-white/20 rounded-full px-4 py-1.5 text-farm-200 text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-farm-400 rounded-full animate-pulse" />
            17 AI Agents · Gemini 2.0 Flash · LangGraph
          </div>

          <h1 className="font-display text-5xl md:text-7xl font-black text-white leading-none mb-4">
            Farm<span className="text-farm-400">Sphere</span> AI
          </h1>
          <p className="text-xl text-farm-200 font-medium mb-3">
            Explainable Multi-Agent Agricultural Intelligence Platform
          </p>
          <p className="text-farm-300 text-base max-w-2xl mx-auto mb-10 leading-relaxed">
            Your long-term agricultural companion powered by 17 specialized AI agents. Disease diagnosis,
            weather intelligence, risk prediction, market insights, and predictive scenario simulation — all with full explainability.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/dashboard">
              <motion.button
                whileHover={{ scale: 1.04, y: -2 }}
                whileTap={{ scale: 0.97 }}
                className="btn-farm px-8 py-3.5 rounded-xl text-base flex items-center gap-2 bg-white text-farm-800 hover:bg-farm-50"
              >
                🌾 Open Dashboard
                <ArrowRight size={18} />
              </motion.button>
            </Link>
            <Link href="/chat">
              <motion.button
                whileHover={{ scale: 1.04, y: -2 }}
                whileTap={{ scale: 0.97 }}
                className="px-8 py-3.5 rounded-xl text-base border-2 border-white/30 text-white font-semibold hover:bg-white/10 transition-all flex items-center gap-2"
              >
                💬 Try AI Assistant
              </motion.button>
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Features */}
      <div className="bg-white dark:bg-gray-950 px-6 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="font-display text-3xl font-bold text-gray-900 dark:text-white text-center mb-10">
            Built for Competition-Grade Agricultural AI
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                viewport={{ once: true }}
                className="glass-card bg-white dark:bg-gray-900 p-5"
              >
                <div className="w-10 h-10 bg-farm-50 dark:bg-farm-950/50 rounded-xl flex items-center justify-center mb-3">
                  <f.icon size={20} className="text-farm-600 dark:text-farm-400" />
                </div>
                <p className="font-semibold text-gray-800 dark:text-white text-sm">{f.label}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{f.desc}</p>
              </motion.div>
            ))}
          </div>

          {/* Tech stack */}
          <div className="mt-10 text-center">
            <p className="text-sm text-gray-400 mb-3">Technology Stack</p>
            <div className="flex flex-wrap justify-center gap-2">
              {[
                "Gemini 2.0 Flash", "LangGraph", "ChromaDB", "FastAPI", "Next.js 15",
                "PostgreSQL", "Redis", "Docker", "Prometheus", "OpenWeatherMap", "Google Earth Engine",
              ].map((tech) => (
                <span key={tech} className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 px-3 py-1.5 rounded-full">
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
