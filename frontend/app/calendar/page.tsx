"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Calendar, CheckCircle, Clock, Leaf, Droplets, FlaskConical, Scissors, TrendingUp, TrendingDown, Minus } from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import { getCalendar } from "@/lib/api";

const rawApiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_BASE = rawApiBase.endsWith('/') ? rawApiBase.slice(0, -1) : rawApiBase;

const CROPS = ["tomato", "wheat", "rice", "cotton", "onion", "potato", "maize", "soybean"];

const cropEmoji: Record<string, string> = {
  tomato: "🍅", wheat: "🌾", rice: "🌾", cotton: "🌱",
  onion: "🧅", potato: "🥔", maize: "🌽", soybean: "🌿",
};

const taskTypeConfig: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
  sowing:      { icon: <Leaf size={14} />,         color: "text-green-700 dark:text-green-300",  bg: "bg-green-50 dark:bg-green-950/30 border-green-100 dark:border-green-800" },
  irrigation:  { icon: <Droplets size={14} />,     color: "text-blue-700 dark:text-blue-300",    bg: "bg-blue-50 dark:bg-blue-950/30 border-blue-100 dark:border-blue-800" },
  fertilizer:  { icon: <FlaskConical size={14} />, color: "text-amber-700 dark:text-amber-300",  bg: "bg-amber-50 dark:bg-amber-950/30 border-amber-100 dark:border-amber-800" },
  harvest:     { icon: <Scissors size={14} />,     color: "text-purple-700 dark:text-purple-300",bg: "bg-purple-50 dark:bg-purple-950/30 border-purple-100 dark:border-purple-800" },
  maintenance: { icon: <CheckCircle size={14} />,  color: "text-slate-700 dark:text-slate-300",  bg: "bg-slate-50 dark:bg-slate-950/30 border-slate-100 dark:border-slate-800" },
  monitoring:  { icon: <Clock size={14} />,        color: "text-rose-700 dark:text-rose-300",    bg: "bg-rose-50 dark:bg-rose-950/30 border-rose-100 dark:border-rose-800" },
};

// Comprehensive fallback calendars for client-side
const TODAY = new Date();
const daysFromNow = (n: number) => {
  const d = new Date(TODAY);
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
};

const buildFallback = (tasks: any[]) => tasks.map(t => ({
  ...t, date: daysFromNow(t.days_from_now),
  is_due: t.days_from_now <= 7 && t.days_from_now >= 0,
}));

const FALLBACK_CALENDARS: Record<string, any[]> = {
  tomato: buildFallback([
    { task: "Nursery preparation", type: "sowing", days_from_now: -30, description: "Prepare nursery beds" },
    { task: "Transplanting", type: "sowing", days_from_now: 0, description: "Transplant 25-day-old seedlings" },
    { task: "First irrigation", type: "irrigation", days_from_now: 2, description: "Light irrigation after transplanting" },
    { task: "Basal fertilizer", type: "fertilizer", days_from_now: 7, description: "Apply NPK 75:50:50 kg/ha" },
    { task: "Weeding", type: "maintenance", days_from_now: 20, description: "First weeding operation" },
    { task: "Stake installation", type: "maintenance", days_from_now: 30, description: "Install stakes for vine support" },
    { task: "Top dressing 1", type: "fertilizer", days_from_now: 35, description: "Apply 37.5 kg N/ha" },
    { task: "Flowering check", type: "monitoring", days_from_now: 45, description: "Monitor for flower drop" },
    { task: "Top dressing 2", type: "fertilizer", days_from_now: 65, description: "Apply remaining N dose" },
    { task: "Harvest begins", type: "harvest", days_from_now: 75, description: "First harvest — green stage" },
  ]),
  wheat: buildFallback([
    { task: "Soil preparation", type: "sowing", days_from_now: -10, description: "Deep ploughing and leveling" },
    { task: "Sowing", type: "sowing", days_from_now: 0, description: "Sow at 100-125 kg seed/ha in rows" },
    { task: "Crown root irrigation", type: "irrigation", days_from_now: 21, description: "Critical first irrigation" },
    { task: "Top dressing", type: "fertilizer", days_from_now: 21, description: "Apply 65 kg Urea/ha" },
    { task: "Tillering irrigation", type: "irrigation", days_from_now: 40, description: "Tillering stage irrigation" },
    { task: "Rust monitoring", type: "monitoring", days_from_now: 60, description: "Check for yellow rust symptoms" },
    { task: "Flag leaf irrigation", type: "irrigation", days_from_now: 80, description: "Irrigation at flag leaf" },
    { task: "Harvest", type: "harvest", days_from_now: 120, description: "Harvest when grains are hard" },
  ]),
  rice: buildFallback([
    { task: "Nursery preparation", type: "sowing", days_from_now: -30, description: "Prepare nursery beds, soak seeds" },
    { task: "Transplanting", type: "sowing", days_from_now: 0, description: "Transplant 25-day seedlings at 20×15 cm" },
    { task: "Weed control", type: "maintenance", days_from_now: 7, description: "Apply pre-emergence herbicide" },
    { task: "Basal fertilizer", type: "fertilizer", days_from_now: 7, description: "Apply NPK 80:40:40 kg/ha" },
    { task: "First top dressing", type: "fertilizer", days_from_now: 21, description: "Apply 40 kg N/ha at tillering" },
    { task: "Blast monitoring", type: "monitoring", days_from_now: 40, description: "Check for neck blast" },
    { task: "Second top dressing", type: "fertilizer", days_from_now: 45, description: "Apply 40 kg N/ha at panicle initiation" },
    { task: "Drain field", type: "maintenance", days_from_now: 100, description: "Drain water 10 days before harvest" },
    { task: "Harvest", type: "harvest", days_from_now: 110, description: "Harvest at 85% grain ripening" },
  ]),
  cotton: buildFallback([
    { task: "Land preparation", type: "sowing", days_from_now: -7, description: "Deep ploughing, FYM application" },
    { task: "Sowing", type: "sowing", days_from_now: 0, description: "Sow Bt cotton at 90×60 cm" },
    { task: "Thinning", type: "maintenance", days_from_now: 14, description: "Thin to 1 plant/hill" },
    { task: "Basal fertilizer", type: "fertilizer", days_from_now: 7, description: "Apply NPK 150:75:75 kg/ha" },
    { task: "Top dressing 1", type: "fertilizer", days_from_now: 45, description: "Apply 50 kg N/ha at squaring" },
    { task: "Boll worm monitoring", type: "monitoring", days_from_now: 60, description: "Check for boll worm" },
    { task: "First picking", type: "harvest", days_from_now: 130, description: "Pick open bolls" },
    { task: "Final harvest", type: "harvest", days_from_now: 175, description: "Final picking" },
  ]),
  onion: buildFallback([
    { task: "Nursery sowing", type: "sowing", days_from_now: -45, description: "Sow seeds in raised nursery beds" },
    { task: "Transplanting", type: "sowing", days_from_now: 0, description: "Transplant 6-week seedlings at 15×10 cm" },
    { task: "Basal fertilizer", type: "fertilizer", days_from_now: 7, description: "Apply NPK 50:50:50 kg/ha" },
    { task: "Top dressing", type: "fertilizer", days_from_now: 30, description: "Apply 25 kg N/ha at bulb initiation" },
    { task: "Purple blotch check", type: "monitoring", days_from_now: 50, description: "Check for purple blotch" },
    { task: "Withhold water", type: "irrigation", days_from_now: 90, description: "Stop irrigation 10 days before harvest" },
    { task: "Harvest", type: "harvest", days_from_now: 100, description: "Harvest when 50% tops fall over" },
  ]),
  potato: buildFallback([
    { task: "Seed treatment", type: "sowing", days_from_now: -5, description: "Treat seed pieces with Captan" },
    { task: "Planting", type: "sowing", days_from_now: 0, description: "Plant at 60×20 cm, 5-7 cm deep" },
    { task: "Earthing up", type: "maintenance", days_from_now: 25, description: "Hill up soil to prevent greening" },
    { task: "Top dressing", type: "fertilizer", days_from_now: 25, description: "Apply 60 kg N/ha at earthing up" },
    { task: "Late blight monitoring", type: "monitoring", days_from_now: 35, description: "Daily check — spray Mancozeb at first sign" },
    { task: "Vine killing", type: "maintenance", days_from_now: 80, description: "Cut vines 10 days before harvest" },
    { task: "Harvest", type: "harvest", days_from_now: 90, description: "Dig when skin is firm" },
  ]),
  maize: buildFallback([
    { task: "Sowing", type: "sowing", days_from_now: 0, description: "Sow 2 seeds/hill at 60×20 cm, thin to 1" },
    { task: "Thinning & gap filling", type: "maintenance", days_from_now: 14, description: "Thin to 1 plant/hill" },
    { task: "Earthing up", type: "maintenance", days_from_now: 25, description: "Hill up to support plants" },
    { task: "Top dressing 1", type: "fertilizer", days_from_now: 25, description: "Apply 60 kg N/ha at knee-high stage" },
    { task: "Fall armyworm check", type: "monitoring", days_from_now: 20, description: "Check whorls for fall armyworm" },
    { task: "Top dressing 2", type: "fertilizer", days_from_now: 45, description: "Apply 60 kg N/ha before tasseling" },
    { task: "Irrigation at silking", type: "irrigation", days_from_now: 55, description: "Critical irrigation at silking" },
    { task: "Harvest", type: "harvest", days_from_now: 100, description: "Harvest when husks are dry" },
  ]),
  soybean: buildFallback([
    { task: "Seed inoculation", type: "sowing", days_from_now: -1, description: "Inoculate seeds with Rhizobium" },
    { task: "Sowing", type: "sowing", days_from_now: 0, description: "Sow at 45×5 cm, 3-4 cm deep" },
    { task: "Weeding", type: "maintenance", days_from_now: 20, description: "Hand weeding or inter-cultivation" },
    { task: "Flowering check", type: "monitoring", days_from_now: 35, description: "Monitor for girdle beetle" },
    { task: "Yellow mosaic monitoring", type: "monitoring", days_from_now: 45, description: "Check for yellow mosaic virus" },
    { task: "Pod filling irrigation", type: "irrigation", days_from_now: 60, description: "Critical irrigation at pod filling" },
    { task: "Harvest", type: "harvest", days_from_now: 95, description: "Harvest when 90% pods turn yellow" },
  ]),
};

const MARKET_PRICES: Record<string, { price: number; trend: string; change: number }> = {
  tomato: { price: 1850, trend: "rising", change: 12.5 },
  wheat:  { price: 2275, trend: "stable", change: 1.2 },
  rice:   { price: 2183, trend: "falling", change: -3.4 },
  cotton: { price: 6800, trend: "rising", change: 5.2 },
  onion:  { price: 2400, trend: "rising", change: 18.0 },
  potato: { price: 1200, trend: "stable", change: 0.5 },
  maize:  { price: 1850, trend: "stable", change: 2.1 },
  soybean:{ price: 4600, trend: "rising", change: 8.3 },
};

export default function CalendarPage() {
  const [crop, setCrop] = useState("tomato");
  const [tasks, setTasks] = useState<any[]>(FALLBACK_CALENDARS["tomato"]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setTasks(FALLBACK_CALENDARS[crop] || FALLBACK_CALENDARS["tomato"]);
    setLoading(true);
    getCalendar(crop)
      .then((d: any) => {
        if (d?.tasks?.length) setTasks(d.tasks);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [crop]);

  const upcoming = tasks.filter(t => t.days_from_now >= 0);
  const past = tasks.filter(t => t.days_from_now < 0);
  const marketInfo = MARKET_PRICES[crop];

  const renderTask = (t: any, i: number, dimmed = false) => {
    const cfg = taskTypeConfig[t.type] ?? taskTypeConfig.maintenance;
    return (
      <motion.div
        key={i}
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: i * 0.04 }}
        className={`flex gap-4 p-4 rounded-xl border ${cfg.bg} ${t.is_due ? "ring-2 ring-farm-400" : ""} ${dimmed ? "opacity-50" : ""}`}
      >
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${cfg.color} bg-white dark:bg-gray-800 border border-current/20 shrink-0 mt-0.5`}>
          {cfg.icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <p className="font-semibold text-gray-800 dark:text-white text-sm">{t.task}</p>
            {t.is_due && (
              <span className="text-xs font-bold text-farm-700 dark:text-farm-300 bg-farm-100 dark:bg-farm-900/40 px-2 py-0.5 rounded-full animate-pulse shrink-0">
                DUE NOW
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{t.description}</p>
          <p className="text-xs font-medium text-gray-400 mt-1">
            📅 {t.date}
            {t.days_from_now === 0 ? " (Today)" :
              t.days_from_now > 0 ? ` (in ${t.days_from_now} days)` :
              ` (${Math.abs(t.days_from_now)} days ago)`}
          </p>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto space-y-6">
          {/* Header */}
          <div className="bg-gradient-to-r from-farm-600 to-farm-700 rounded-2xl p-6 text-white relative overflow-hidden">
            <div className="absolute -right-6 -top-6 text-8xl opacity-20">📅</div>
            <h1 className="text-2xl font-bold capitalize">{cropEmoji[crop] || "🌱"} {crop.charAt(0).toUpperCase() + crop.slice(1)} Season Calendar</h1>
            <p className="text-farm-200 text-sm mt-1">AI-generated task schedule based on ICAR guidelines</p>

            {/* Market price inline */}
            {marketInfo && (
              <div className="mt-3 flex items-center gap-3 bg-white/15 rounded-xl px-4 py-2 w-fit">
                <div>
                  <p className="text-xs text-farm-200">Current Market Price</p>
                  <p className="text-lg font-bold">₹{marketInfo.price.toLocaleString("en-IN")}<span className="text-xs font-normal text-farm-200">/quintal</span></p>
                </div>
                <div className={`flex items-center gap-1 text-sm font-bold px-2 py-1 rounded-lg ${marketInfo.trend === "rising" ? "bg-green-400/20 text-green-200" : marketInfo.trend === "falling" ? "bg-red-400/20 text-red-200" : "bg-amber-400/20 text-amber-200"}`}>
                  {marketInfo.trend === "rising" ? <TrendingUp size={14} /> : marketInfo.trend === "falling" ? <TrendingDown size={14} /> : <Minus size={14} />}
                  {marketInfo.change > 0 ? "+" : ""}{marketInfo.change}%
                </div>
              </div>
            )}
          </div>

          {/* Crop selector */}
          <div className="flex flex-wrap gap-2">
            {CROPS.map(c => (
              <button key={c} onClick={() => setCrop(c)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  crop === c
                    ? "bg-farm-600 text-white shadow-lg"
                    : "bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:border-farm-400"
                }`}
              >
                {cropEmoji[c] || "🌱"} {c.charAt(0).toUpperCase() + c.slice(1)}
              </button>
            ))}
          </div>

          {/* Task type legend */}
          <div className="flex flex-wrap gap-2">
            {Object.entries(taskTypeConfig).map(([type, cfg]) => (
              <span key={type} className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full border ${cfg.bg} ${cfg.color}`}>
                {cfg.icon} {type.charAt(0).toUpperCase() + type.slice(1)}
              </span>
            ))}
          </div>

          {/* Upcoming Tasks */}
          <div>
            <p className="font-semibold text-gray-700 dark:text-gray-200 mb-3 flex items-center gap-2">
              <span className="w-2 h-2 bg-farm-500 rounded-full" /> Upcoming Tasks ({upcoming.length})
            </p>
            <div className="space-y-2.5">
              {upcoming.map((t, i) => renderTask(t, i))}
              {upcoming.length === 0 && (
                <p className="text-gray-400 text-sm text-center py-6">No upcoming tasks</p>
              )}
            </div>
          </div>

          {/* Completed / Past Tasks */}
          {past.length > 0 && (
            <div>
              <p className="font-semibold text-gray-500 mb-3 flex items-center gap-2">
                <CheckCircle size={16} className="text-green-500" /> Completed / Past Tasks
              </p>
              <div className="space-y-2">
                {past.map((t, i) => renderTask(t, i, true))}
              </div>
            </div>
          )}
        </motion.div>
      </main>
    </div>
  );
}
