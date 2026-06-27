"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { getSatelliteData } from "@/lib/api";
import Sidebar from "@/components/layout/Sidebar";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Satellite, Activity, Droplets, Leaf } from "lucide-react";

const CROPS = ["tomato", "wheat", "rice", "cotton", "soybean"];

// Generate realistic NDVI mock data client-side as immediate fallback
function generateMockNDVI(crop: string, days = 30) {
  const baseNDVI: Record<string, number> = { tomato: 0.55, wheat: 0.65, rice: 0.60, cotton: 0.58, soybean: 0.62 };
  const base = baseNDVI[crop] ?? 0.50;
  const today = new Date();
  return Array.from({ length: days }, (_, i) => {
    const d = new Date(today);
    d.setDate(today.getDate() - (days - i));
    const growth = 1 + i / (days * 3);
    const noise = (Math.sin(i * 0.7 + crop.length) * 0.03);
    const ndvi = Math.min(0.95, Math.max(0.10, base * growth + noise));
    return {
      date: d.toISOString().slice(0, 10),
      ndvi: Math.round(ndvi * 1000) / 1000,
      health: ndvi > 0.55 ? "Healthy" : ndvi > 0.35 ? "Stressed" : "Critical",
    };
  });
}

function buildMockData(crop: string) {
  const series = generateMockNDVI(crop, 30);
  const current = series[series.length - 1].ndvi;
  const avg = Math.round((series.reduce((s, d) => s + d.ndvi, 0) / series.length) * 1000) / 1000;
  const trend = current > series[series.length - 7].ndvi ? "improving" : "declining";
  return {
    current_ndvi: current,
    average_ndvi_30d: avg,
    vegetation_health: current > 0.55 ? "Healthy" : current > 0.35 ? "Moderate Stress" : "High Stress",
    ndvi_trend: trend,
    drought_stress: current > 0.55 ? "low" : current > 0.40 ? "moderate" : "high",
    water_stress_index: Math.round(Math.max(0, 1 - current) * 100) / 100,
    crop_coverage_pct: Math.round(Math.min(100, current * 140) * 10) / 10,
    anomaly_detected: current < 0.35,
    anomaly_description: current < 0.35 ? "Significant vegetation stress detected in northeast quadrant" : null,
    ndvi_timeseries: series,
    source: "Simulated (Demo Mode)",
    last_updated: new Date().toISOString(),
  };
}

export default function SatellitePage() {
  const [data, setData] = useState<any>(() => buildMockData("tomato")); // immediate mock
  const [crop, setCrop] = useState("tomato");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    // Show mock immediately, update if backend responds
    setData(buildMockData(crop));
    getSatelliteData(crop)
      .then((d: any) => { if (d?.current_ndvi) setData(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [crop]);

  const healthColor = (h: string) =>
    h === "Healthy" ? "text-green-600 dark:text-green-400" :
    h?.includes("Moderate") ? "text-amber-600 dark:text-amber-400" : "text-red-600 dark:text-red-400";

  const healthBg = (h: string) =>
    h === "Healthy" ? "bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800" :
    h?.includes("Moderate") ? "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800" :
    "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800";

  const ndviGradientColor = data?.current_ndvi > 0.55 ? "#22c55e" : data?.current_ndvi > 0.35 ? "#f59e0b" : "#ef4444";

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-6 text-white relative overflow-hidden">
            <div className="absolute -right-6 -top-6 text-8xl opacity-20">🛰️</div>
            <div className="flex items-center gap-3">
              <Satellite size={24} />
              <div>
                <h1 className="text-2xl font-bold">Satellite Intelligence</h1>
                <p className="text-blue-200 text-sm mt-0.5">NDVI vegetation health monitoring via Google Earth Engine</p>
              </div>
            </div>
          </div>

          {/* Crop selector */}
          <div className="flex flex-wrap gap-2">
            {CROPS.map(c => (
              <button key={c} onClick={() => setCrop(c)}
                className={`text-sm px-4 py-2 rounded-full capitalize border transition-all font-medium ${
                  crop === c
                    ? "bg-blue-600 text-white border-blue-600 shadow"
                    : "bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-blue-400"
                }`}>
                {c}
              </button>
            ))}
          </div>

          {data && (
            <>
              {/* Key metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "Current NDVI", value: data.current_ndvi?.toFixed(3), sub: data.vegetation_health, icon: <Leaf size={18} className="text-green-500" /> },
                  { label: "30-Day Avg", value: data.average_ndvi_30d?.toFixed(3), sub: `Trend: ${data.ndvi_trend}`, icon: <Activity size={18} className="text-blue-500" /> },
                  { label: "Crop Coverage", value: `${data.crop_coverage_pct}%`, sub: "of field area", icon: <Satellite size={18} className="text-indigo-500" /> },
                  { label: "Water Stress", value: data.water_stress_index?.toFixed(2), sub: `${data.drought_stress} stress`, icon: <Droplets size={18} className="text-sky-500" /> },
                ].map((m, i) => (
                  <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.07 }}
                    className="glass-card bg-white dark:bg-gray-900 p-4"
                  >
                    <div className="flex items-center gap-2 mb-2">{m.icon}<p className="text-xs text-gray-400">{m.label}</p></div>
                    <p className="text-2xl font-bold" style={{ color: ndviGradientColor }}>{m.value}</p>
                    <p className="text-xs text-gray-500 mt-0.5 capitalize">{m.sub}</p>
                  </motion.div>
                ))}
              </div>

              {/* Health status banner */}
              <div className={`rounded-xl p-4 flex items-center gap-3 border ${healthBg(data.vegetation_health)}`}>
                <span className="text-3xl">{data.vegetation_health === "Healthy" ? "🌿" : data.vegetation_health?.includes("Moderate") ? "⚠️" : "🚨"}</span>
                <div className="flex-1">
                  <p className={`font-bold ${healthColor(data.vegetation_health)}`}>{data.vegetation_health}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    NDVI trend is <strong>{data.ndvi_trend}</strong> · Drought stress: <strong>{data.drought_stress}</strong>
                    {data.anomaly_detected && ` · ⚠️ ${data.anomaly_description}`}
                  </p>
                </div>
                <div className="text-xs text-gray-400 text-right shrink-0">
                  {data.source}<br />{new Date(data.last_updated).toLocaleDateString("en-IN")}
                </div>
              </div>

              {/* NDVI Chart */}
              <div className="glass-card bg-white dark:bg-gray-900 p-5">
                <div className="flex items-center justify-between mb-4">
                  <p className="font-semibold text-gray-800 dark:text-white">📈 30-Day NDVI Timeseries</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1"><span className="w-3 h-1 bg-green-400 inline-block rounded" /> Healthy (&gt;0.55)</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-1 bg-amber-400 inline-block rounded" /> Moderate (0.35–0.55)</span>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={data.ndvi_timeseries || []}>
                    <defs>
                      <linearGradient id="ndviGradSat" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={ndviGradientColor} stopOpacity={0.35} />
                        <stop offset="95%" stopColor={ndviGradientColor} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} interval={4} />
                    <YAxis domain={[0.2, 0.9]} tick={{ fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ background: "#1e293b", border: "none", borderRadius: 8, color: "white", fontSize: 11 }}
                      formatter={(v: number) => [v.toFixed(3), "NDVI"]}
                      labelFormatter={l => `Date: ${l}`}
                    />
                    <Area type="monotone" dataKey="ndvi" stroke={ndviGradientColor} strokeWidth={2}
                      fill="url(#ndviGradSat)" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
                <p className="text-xs text-gray-400 text-center mt-2">
                  Values above 0.55 = healthy vegetation · Source: {data.source}
                </p>
              </div>

              {/* Field recommendations */}
              <div className="glass-card bg-white dark:bg-gray-900 p-5">
                <p className="font-semibold text-gray-800 dark:text-white mb-3">🌾 Field Recommendations</p>
                <div className="space-y-2 text-sm">
                  {data.vegetation_health === "Healthy" ? (
                    <div className="flex gap-2 p-3 bg-green-50 dark:bg-green-950/30 rounded-xl border border-green-100 dark:border-green-900">
                      <span>✅</span>
                      <p className="text-green-700 dark:text-green-300">Vegetation health is excellent. Continue current management practices. NDVI indicates optimal biomass accumulation.</p>
                    </div>
                  ) : (
                    <>
                      <div className="flex gap-2 p-3 bg-amber-50 dark:bg-amber-950/30 rounded-xl border border-amber-100 dark:border-amber-900">
                        <span>⚠️</span>
                        <p className="text-amber-700 dark:text-amber-300">Vegetation stress detected. Check irrigation schedule and soil moisture. Consider foliar spray of micronutrients.</p>
                      </div>
                      <div className="flex gap-2 p-3 bg-blue-50 dark:bg-blue-950/30 rounded-xl border border-blue-100 dark:border-blue-900">
                        <span>💧</span>
                        <p className="text-blue-700 dark:text-blue-300">Water stress index: {data.water_stress_index}. {data.water_stress_index > 0.5 ? "Irrigation required immediately." : "Monitor moisture levels closely."}</p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </>
          )}
        </motion.div>
      </main>
    </div>
  );
}
