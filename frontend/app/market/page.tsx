"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus, MapPin, Search } from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";

const rawApiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_BASE = rawApiBase.endsWith('/') ? rawApiBase.slice(0, -1) : rawApiBase;

const cropEmoji: Record<string, string> = {
  tomato: "🍅", wheat: "🌾", rice: "🌾", onion: "🧅",
  potato: "🥔", cotton: "🌱", sugarcane: "🎋", soybean: "🌿",
  maize: "🌽", groundnut: "🥜", chilli: "🌶️", banana: "🍌",
};

// Comprehensive fallback with India market data (June 2026 estimates)
const FALLBACK_MARKETS: Record<string, any> = {
  tomato:    { price_per_quintal: 1850, trend: "rising",  change_pct: 12.5, best_market: "Azadpur Mandi, Delhi",             harvest_recommendation: "Sell within 3-5 days", msp: null },
  wheat:     { price_per_quintal: 2275, trend: "stable",  change_pct:  1.2, best_market: "Khanna Mandi, Punjab",             harvest_recommendation: "MSP guaranteed — use government procurement", msp: 2275 },
  rice:      { price_per_quintal: 2183, trend: "falling", change_pct: -3.4, best_market: "Karnal Mandi, Haryana",            harvest_recommendation: "Store 2 weeks — prices expected to recover", msp: 2183 },
  onion:     { price_per_quintal: 2400, trend: "rising",  change_pct: 18.0, best_market: "Lasalgaon Mandi, Nashik",          harvest_recommendation: "Peak prices — sell immediately", msp: null },
  potato:    { price_per_quintal: 1200, trend: "stable",  change_pct:  0.5, best_market: "Agra Mandi, Uttar Pradesh",        harvest_recommendation: "Average market — sell in next 10 days", msp: null },
  cotton:    { price_per_quintal: 6800, trend: "rising",  change_pct:  5.2, best_market: "Rajkot Mandi, Gujarat",            harvest_recommendation: "Good prices — sell in next 15 days", msp: 6620 },
  sugarcane: { price_per_quintal:  340, trend: "stable",  change_pct:  0.0, best_market: "Sell to nearest sugar mill (FRP)", harvest_recommendation: "FRP guaranteed at ₹340/quintal", msp: 340 },
  soybean:   { price_per_quintal: 4600, trend: "rising",  change_pct:  8.3, best_market: "Indore Mandi, Madhya Pradesh",     harvest_recommendation: "Rising trend — consider selling now", msp: 4600 },
  maize:     { price_per_quintal: 1850, trend: "stable",  change_pct:  2.1, best_market: "Davangere Mandi, Karnataka",       harvest_recommendation: "Stable prices — sell as needed", msp: 1850 },
  groundnut: { price_per_quintal: 5800, trend: "rising",  change_pct:  6.7, best_market: "Junagadh Mandi, Gujarat",          harvest_recommendation: "High demand — sell in bulk", msp: 5440 },
  chilli:    { price_per_quintal: 9500, trend: "rising",  change_pct: 14.2, best_market: "Guntur Mandi, Andhra Pradesh",     harvest_recommendation: "Peak season prices — sell immediately", msp: null },
  banana:    { price_per_quintal: 1600, trend: "stable",  change_pct: -1.5, best_market: "Jalgaon Mandi, Maharashtra",       harvest_recommendation: "Sell to local aggregators", msp: null },
};

export default function MarketPage() {
  const [markets, setMarkets] = useState<Record<string, any>>(FALLBACK_MARKETS);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [usingFallback, setUsingFallback] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/api/market`)
      .then(r => r.json())
      .then(d => {
        const data = d?.markets || d;
        if (data && Object.keys(data).length > 0) {
          setMarkets({ ...FALLBACK_MARKETS, ...data });
        } else {
          setUsingFallback(true);
        }
      })
      .catch(() => setUsingFallback(true))
      .finally(() => setLoading(false));
  }, []);

  const TrendIcon = ({ trend }: { trend: string }) => {
    if (trend === "rising")  return <TrendingUp  size={15} className="text-green-500" />;
    if (trend === "falling") return <TrendingDown size={15} className="text-red-500" />;
    return <Minus size={15} className="text-amber-500" />;
  };

  const trendColor = (t: string) =>
    t === "rising"  ? "text-green-600 dark:text-green-400" :
    t === "falling" ? "text-red-600 dark:text-red-400" : "text-amber-600 dark:text-amber-400";

  const trendBadge = (t: string) =>
    t === "rising"  ? "bg-green-50 dark:bg-green-950/30 text-green-700 dark:text-green-300" :
    t === "falling" ? "bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-300" :
                      "bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-300";

  const filtered = Object.entries(markets).filter(([crop]) =>
    crop.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="bg-gradient-to-r from-emerald-600 to-teal-700 rounded-2xl p-6 text-white relative overflow-hidden">
            <div className="absolute -right-6 -top-6 text-8xl opacity-20">📈</div>
            <h1 className="text-2xl font-bold">India Crop Market Prices</h1>
            <p className="text-emerald-200 text-sm mt-1">
              {Object.keys(markets).length} crops · Agmarknet & eNAM · Updated June 2026
            </p>
            {usingFallback && (
              <p className="text-yellow-200 text-xs mt-2 bg-yellow-500/20 px-3 py-1 rounded-full inline-block">
                ⚠️ Showing reference prices — live API unavailable
              </p>
            )}
          </div>

          {/* Summary stats */}
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: "Rising Crops", count: Object.values(markets).filter((m: any) => m.trend === "rising").length, color: "text-green-600", bg: "bg-green-50 dark:bg-green-950/30" },
              { label: "Stable Crops", count: Object.values(markets).filter((m: any) => m.trend === "stable").length, color: "text-amber-600", bg: "bg-amber-50 dark:bg-amber-950/30" },
              { label: "Falling Crops", count: Object.values(markets).filter((m: any) => m.trend === "falling").length, color: "text-red-600", bg: "bg-red-50 dark:bg-red-950/30" },
            ].map((s, i) => (
              <div key={i} className={`glass-card ${s.bg} p-4 text-center`}>
                <p className={`text-2xl font-bold ${s.color}`}>{s.count}</p>
                <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search crop..."
              className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm text-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-400"
            />
          </div>

          {/* Price cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filtered.map(([crop, data]: [string, any], i) => (
              <motion.div
                key={crop}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className="glass-card bg-white dark:bg-gray-900 p-5"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{cropEmoji[crop] ?? "🌱"}</span>
                    <div>
                      <p className="font-bold text-gray-800 dark:text-white capitalize">{crop}</p>
                      <p className="text-xs text-gray-400">per quintal (100 kg)</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-800 dark:text-white">
                      ₹{data.price_per_quintal?.toLocaleString("en-IN")}
                    </p>
                    <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${trendBadge(data.trend)}`}>
                      <TrendIcon trend={data.trend} />
                      {data.change_pct > 0 ? "+" : ""}{data.change_pct}%
                    </span>
                  </div>
                </div>

                <div className="mt-3 space-y-2">
                  {data.msp && (
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">MSP (Govt. Support)</span>
                      <span className="font-semibold text-blue-600 dark:text-blue-400">₹{data.msp?.toLocaleString("en-IN")}/q</span>
                    </div>
                  )}
                  <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                    <MapPin size={11} />
                    <span>Best: <strong className="text-gray-700 dark:text-gray-200">{data.best_market}</strong></span>
                  </div>
                  <div className="text-xs text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 rounded-lg px-3 py-2">
                    💡 {data.harvest_recommendation}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Insights */}
          <div className="glass-card bg-white dark:bg-gray-900 p-5">
            <p className="font-semibold text-gray-800 dark:text-white mb-3">📊 Market Insights</p>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
              <div className="flex gap-2"><span className="text-green-500 shrink-0">→</span><p><strong>Chilli, Onion, Tomato</strong> at seasonal highs — sell quickly before market correction.</p></div>
              <div className="flex gap-2"><span className="text-blue-500 shrink-0">→</span><p>Crops with <strong>MSP support</strong> (Wheat, Rice, Cotton, Soybean) have a guaranteed floor price.</p></div>
              <div className="flex gap-2"><span className="text-amber-500 shrink-0">→</span><p>Use <strong>eNAM portal</strong> (enam.gov.in) for online trading and better price discovery across mandis.</p></div>
            </div>
          </div>

          <p className="text-xs text-gray-400 text-center">
            Prices are indicative. Verify at your local APMC mandi or eNAM before selling.
          </p>
        </motion.div>
      </main>
    </div>
  );
}
