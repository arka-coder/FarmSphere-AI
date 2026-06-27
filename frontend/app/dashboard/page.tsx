"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  CloudSun, TrendingUp, AlertTriangle, Leaf, Satellite,
  Calendar, FileText, Zap, Activity, Wind, Droplets, Thermometer,
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis,
} from "recharts";
import Link from "next/link";
import Sidebar from "@/components/layout/Sidebar";
import { getWeather, getAlerts, getMarketData, getSatelliteData } from "@/lib/api";

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.08, duration: 0.4, ease: "easeOut" },
  }),
};

// Mock NDVI chart data
const ndviData = [
  { date: "Jun 1", ndvi: 0.42 }, { date: "Jun 5", ndvi: 0.48 },
  { date: "Jun 10", ndvi: 0.55 }, { date: "Jun 15", ndvi: 0.61 },
  { date: "Jun 18", ndvi: 0.58 }, { date: "Jun 21", ndvi: 0.63 },
];

const riskRadarData = [
  { factor: "Disease", value: 68 },
  { factor: "Pest", value: 42 },
  { factor: "Weather", value: 75 },
  { factor: "Irrigation", value: 28 },
  { factor: "Market", value: 35 },
];

const MARKET_HIGHLIGHTS = [
  { crop: "Tomato 🍅", price: "₹1,850/q", trend: "+12.5%", up: true },
  { crop: "Wheat 🌾", price: "₹2,275/q", trend: "+1.2%", up: true },
  { crop: "Rice 🌾", price: "₹2,183/q", trend: "-3.4%", up: false },
  { crop: "Onion 🧅", price: "₹2,400/q", trend: "+18%", up: true },
];

export default function DashboardPage() {
  const [weather, setWeather] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [satellite, setSatellite] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getWeather().catch(() => null),
      getAlerts().catch(() => ({ alerts: [] })),
      getSatelliteData("tomato").catch(() => null),
    ]).then(([w, a, s]) => {
      setWeather(w);
      setAlerts(a?.alerts || []);
      setSatellite(s);
      setLoading(false);
    });
  }, []);

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="bg-farm-gradient px-8 pt-8 pb-16 relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-4 right-8 text-8xl">🌾</div>
            <div className="absolute bottom-4 right-32 text-4xl">🌱</div>
          </div>
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
            <p className="text-farm-300 text-sm font-medium">Good evening,</p>
            <h1 className="font-display text-3xl font-bold text-white mt-1">Farm Dashboard</h1>
            <p className="text-farm-200 text-sm mt-1">
              17 AI agents monitoring your farm • {new Date().toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
            </p>
          </motion.div>
        </div>

        <div className="px-8 -mt-8 pb-8 space-y-6">
          {/* Quick stats row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: "🌡️", label: "Temperature", value: weather ? `${weather.temperature}°C` : "28°C", sub: weather?.feels_like ? `Feels ${weather.feels_like}°C` : "Loading..." },
              { icon: "💧", label: "Humidity", value: weather ? `${weather.humidity}%` : "72%", sub: weather?.weather_condition || "Partly Cloudy" },
              { icon: "🌱", label: "NDVI Score", value: satellite ? satellite.current_ndvi?.toFixed(2) : "0.63", sub: satellite?.vegetation_health || "Healthy" },
              { icon: "⚠️", label: "Active Alerts", value: alerts.length.toString(), sub: alerts.find(a => a.severity === "high") ? "Action needed" : "No critical issues" },
            ].map((stat, i) => (
              <motion.div key={i} custom={i} variants={cardVariants} initial="hidden" animate="visible"
                className="glass-card bg-white dark:bg-gray-900 p-5"
              >
                <span className="text-2xl">{stat.icon}</span>
                <p className="text-2xl font-display font-bold text-gray-900 dark:text-white mt-2">{stat.value}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{stat.label}</p>
                <p className="text-xs text-farm-600 dark:text-farm-400 mt-0.5">{stat.sub}</p>
              </motion.div>
            ))}
          </div>

          {/* Main grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Weather Card — spans 2 cols */}
            <motion.div custom={4} variants={cardVariants} initial="hidden" animate="visible"
              className="lg:col-span-2 weather-card"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-white/70 text-sm font-medium">Current Weather</p>
                  <p className="text-4xl font-display font-bold text-white mt-1">
                    {weather?.temperature ?? 28}°C
                  </p>
                  <p className="text-white/90 mt-1">{weather?.weather_condition || "Partly Cloudy"}</p>
                  <p className="text-white/60 text-sm">{weather?.location || "Your Location"}</p>
                </div>
                <div className="text-right space-y-1">
                  <div className="flex items-center gap-1.5 justify-end">
                    <Droplets size={14} className="text-white/70" />
                    <span className="text-white text-sm">{weather?.humidity ?? 72}% humidity</span>
                  </div>
                  <div className="flex items-center gap-1.5 justify-end">
                    <Wind size={14} className="text-white/70" />
                    <span className="text-white text-sm">{weather?.wind_speed ?? 3.4} m/s</span>
                  </div>
                  <div className="flex items-center gap-1.5 justify-end">
                    <Thermometer size={14} className="text-white/70" />
                    <span className="text-white text-sm">Feels {weather?.feels_like ?? 31}°C</span>
                  </div>
                </div>
              </div>
              {/* 3-day forecast */}
              <div className="mt-5 grid grid-cols-3 gap-3">
                {(weather?.forecast || [
                  { day: "Tomorrow", condition: "Light Rain", temp_max: 30, rain_chance: 70 },
                  { day: "Day After", condition: "Thunderstorm", temp_max: 27, rain_chance: 85 },
                  { day: "Day 3", condition: "Sunny", temp_max: 32, rain_chance: 20 },
                ]).map((f: any, i: number) => (
                  <div key={i} className="bg-white/10 rounded-xl p-2.5 text-center">
                    <p className="text-white/60 text-xs">{f.day}</p>
                    <p className="text-white font-semibold text-sm mt-1">{f.temp_max}°C</p>
                    <p className="text-white/80 text-xs mt-0.5">{f.condition}</p>
                    <p className="text-blue-200 text-xs mt-0.5">🌧 {f.rain_chance}%</p>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Risk Radar */}
            <motion.div custom={5} variants={cardVariants} initial="hidden" animate="visible"
              className="glass-card bg-white dark:bg-gray-900 p-5"
            >
              <p className="font-semibold text-gray-800 dark:text-white text-sm mb-4 flex items-center gap-2">
                <AlertTriangle size={16} className="text-amber-500" /> Risk Radar
              </p>
              <ResponsiveContainer width="100%" height={180}>
                <RadarChart data={riskRadarData}>
                  <PolarGrid stroke="#22c55e20" />
                  <PolarAngleAxis dataKey="factor" tick={{ fontSize: 10, fill: "#9ca3af" }} />
                  <Radar dataKey="value" stroke="#22c55e" fill="#22c55e" fillOpacity={0.2} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
              <div className="mt-2 space-y-1.5">
                {riskRadarData.map((r) => (
                  <div key={r.factor} className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 w-16">{r.factor}</span>
                    <div className="flex-1 h-1.5 rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden">
                      <div className={`h-full rounded-full ${r.value > 65 ? "bg-red-500" : r.value > 40 ? "bg-amber-500" : "bg-farm-500"}`}
                        style={{ width: `${r.value}%` }} />
                    </div>
                    <span className="text-xs font-semibold text-gray-600 dark:text-gray-300 w-8 text-right">{r.value}%</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* NDVI + Market row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* NDVI Chart */}
            <motion.div custom={6} variants={cardVariants} initial="hidden" animate="visible"
              className="glass-card bg-white dark:bg-gray-900 p-5"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="font-semibold text-gray-800 dark:text-white text-sm flex items-center gap-2">
                    <Satellite size={16} className="text-blue-500" /> Satellite NDVI
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">30-day vegetation health index</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-farm-600 dark:text-farm-400">
                    {satellite?.current_ndvi?.toFixed(2) || "0.63"}
                  </p>
                  <p className={`text-xs font-medium ${
                    satellite?.ndvi_trend === "improving" ? "text-farm-500" : "text-amber-500"
                  }`}>
                    {satellite?.ndvi_trend === "improving" ? "↑ Improving" : "↓ Declining"}
                  </p>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={140}>
                <AreaChart data={ndviData}>
                  <defs>
                    <linearGradient id="ndviGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0fdf4" strokeOpacity={0.5} />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#9ca3af" }} />
                  <YAxis domain={[0.3, 0.8]} tick={{ fontSize: 10, fill: "#9ca3af" }} />
                  <Tooltip
                    contentStyle={{ background: "#052e16", border: "none", borderRadius: 8, color: "white", fontSize: 12 }}
                    formatter={(v: number) => [v.toFixed(3), "NDVI"]}
                  />
                  <Area type="monotone" dataKey="ndvi" stroke="#22c55e" strokeWidth={2.5}
                    fill="url(#ndviGrad)" dot={{ fill: "#22c55e", r: 3 }} />
                </AreaChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Market Prices */}
            <motion.div custom={7} variants={cardVariants} initial="hidden" animate="visible"
              className="glass-card bg-white dark:bg-gray-900 p-5"
            >
              <p className="font-semibold text-gray-800 dark:text-white text-sm flex items-center gap-2 mb-4">
                <TrendingUp size={16} className="text-emerald-500" /> Market Prices Today
              </p>
              <div className="space-y-3">
                {MARKET_HIGHLIGHTS.map((m, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-base">{m.crop.split(" ")[1]}</span>
                      <span className="text-sm text-gray-700 dark:text-gray-200 font-medium">
                        {m.crop.split(" ")[0]}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-bold text-gray-800 dark:text-white">{m.price}</span>
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                        m.up ? "bg-farm-50 text-farm-600 dark:bg-farm-950/50 dark:text-farm-400" :
                               "bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400"
                      }`}>
                        {m.trend}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <Link href="/market" className="mt-4 block text-center text-xs text-farm-600 dark:text-farm-400 hover:underline font-medium">
                View all market data →
              </Link>
            </motion.div>
          </div>

          {/* Active Alerts */}
          {alerts.length > 0 && (
            <motion.div custom={8} variants={cardVariants} initial="hidden" animate="visible"
              className="glass-card bg-white dark:bg-gray-900 p-5"
            >
              <p className="font-semibold text-gray-800 dark:text-white text-sm mb-3 flex items-center gap-2">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                Active Alerts ({alerts.length})
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {alerts.map((alert, i) => (
                  <div key={i} className={`rounded-xl p-3 alert-${alert.severity}`}>
                    <p className="text-sm font-semibold">{alert.title}</p>
                    <p className="text-xs mt-1 opacity-80">{alert.message}</p>
                    <p className="text-xs font-medium mt-1.5 opacity-90">→ {alert.action}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Quick action cards */}
          <motion.div custom={9} variants={cardVariants} initial="hidden" animate="visible"
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
          >
            {[
              { href: "/chat", icon: "💬", label: "AI Assistant", desc: "Ask anything", color: "from-farm-600 to-farm-700" },
              { href: "/disease", icon: "🔬", label: "Disease Scan", desc: "Upload plant image", color: "from-blue-600 to-blue-700" },
              { href: "/simulation", icon: "🔮", label: "What-If Sim", desc: "Predict outcomes ⭐", color: "from-violet-600 to-violet-700" },
              { href: "/schemes", icon: "📋", label: "Schemes", desc: "PM-KISAN & more", color: "from-amber-500 to-amber-600" },
            ].map((card, i) => (
              <Link key={i} href={card.href}>
                <motion.div whileHover={{ y: -4, scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  className={`bg-gradient-to-br ${card.color} rounded-2xl p-4 text-white cursor-pointer shadow-lg`}
                >
                  <span className="text-2xl">{card.icon}</span>
                  <p className="font-display font-bold mt-2 text-sm">{card.label}</p>
                  <p className="text-white/70 text-xs">{card.desc}</p>
                </motion.div>
              </Link>
            ))}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
