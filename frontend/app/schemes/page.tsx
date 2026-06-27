"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { getSchemes } from "@/lib/api";
import Sidebar from "@/components/layout/Sidebar";
import { ExternalLink, CheckCircle, ChevronDown, Store, Globe, MapPin } from "lucide-react";

export default function SchemesPage() {
  const [schemes, setSchemes] = useState<any[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "online" | "offline">("all");

  useEffect(() => {
    getSchemes()
      .then(d => setSchemes(d.schemes as any[]))
      .catch(() => {});
  }, []);

  const categoryColors: Record<string, string> = {
    income_support: "bg-farm-100 text-farm-700 dark:bg-farm-950/50 dark:text-farm-300",
    insurance:      "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300",
    credit:         "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300",
    soil:           "bg-orange-100 text-orange-700 dark:bg-orange-950/50 dark:text-orange-300",
    pension:        "bg-purple-100 text-purple-700 dark:bg-purple-950/50 dark:text-purple-300",
    market:         "bg-teal-100 text-teal-700 dark:bg-teal-950/50 dark:text-teal-300",
    organic:        "bg-green-100 text-green-700 dark:bg-green-950/50 dark:text-green-300",
    infrastructure: "bg-slate-100 text-slate-700 dark:bg-slate-950/50 dark:text-slate-300",
  };

  const filtered = schemes.filter(s => {
    if (filter === "online") return !!s.online_apply_url;
    if (filter === "offline") return !s.online_apply_url;
    return true;
  });

  const onlineCount = schemes.filter(s => !!s.online_apply_url).length;
  const offlineCount = schemes.filter(s => !s.online_apply_url).length;

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl mx-auto space-y-6">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-violet-700 rounded-2xl p-6 text-white relative overflow-hidden">
            <div className="absolute -right-6 -top-6 text-8xl opacity-20">🏛️</div>
            <h1 className="text-2xl font-bold">Government Agricultural Schemes</h1>
            <p className="text-indigo-200 text-sm mt-1">{schemes.length} schemes available · Central & State Government</p>
            <div className="flex gap-3 mt-3">
              <div className="bg-white/20 rounded-lg px-3 py-1.5 text-sm flex items-center gap-1.5">
                <Globe size={14} /> {onlineCount} Apply Online
              </div>
              <div className="bg-white/10 rounded-lg px-3 py-1.5 text-sm flex items-center gap-1.5">
                <MapPin size={14} /> {offlineCount} In-Person Only
              </div>
            </div>
          </div>

          {/* Filter tabs */}
          <div className="flex gap-2">
            {(["all", "online", "offline"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
                  filter === f
                    ? "bg-indigo-600 text-white shadow"
                    : "bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:border-indigo-400"
                }`}
              >
                {f === "all" ? "🏛️ All Schemes" : f === "online" ? <><Globe size={14} /> Apply Online</> : <><MapPin size={14} /> In-Person Only</>}
              </button>
            ))}
          </div>

          {/* Scheme cards */}
          <div className="space-y-3">
            {filtered.map((s, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                className="glass-card bg-white dark:bg-gray-900 overflow-hidden"
              >
                <button onClick={() => setExpanded(expanded === s.name ? null : s.name)}
                  className="w-full p-5 flex items-center justify-between text-left">
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${categoryColors[s.category] || "bg-gray-100 text-gray-600"}`}>
                      {s.category?.replace(/_/g, " ").toUpperCase()}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-gray-800 dark:text-white">{s.name}</p>
                        {s.online_apply_url ? (
                          <span className="text-xs flex items-center gap-1 text-green-600 dark:text-green-400 font-medium">
                            <Globe size={10} /> Online
                          </span>
                        ) : (
                          <span className="text-xs flex items-center gap-1 text-gray-400 font-medium">
                            <MapPin size={10} /> In-Person
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{s.full_name}</p>
                    </div>
                  </div>
                  <ChevronDown size={16} className={`text-gray-400 transition-transform ${expanded === s.name ? "rotate-180" : ""}`} />
                </button>

                {expanded === s.name && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="px-5 pb-5 border-t border-gray-100 dark:border-gray-800 space-y-3"
                  >
                    <div className="pt-4 grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-xs text-gray-400 font-medium uppercase">Benefit</p>
                        <p className="text-gray-700 dark:text-gray-200 mt-0.5 font-semibold text-farm-700 dark:text-farm-400">{s.benefit}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-400 font-medium uppercase">Eligibility</p>
                        <p className="text-gray-700 dark:text-gray-200 mt-0.5">{s.eligibility}</p>
                      </div>
                      {s.premium && <div className="col-span-2">
                        <p className="text-xs text-gray-400 font-medium uppercase">Premium</p>
                        <p className="text-gray-700 dark:text-gray-200 mt-0.5">{s.premium}</p>
                      </div>}
                      {s.exclusions && <div className="col-span-2">
                        <p className="text-xs text-gray-400 font-medium uppercase">Who Cannot Apply</p>
                        <p className="text-gray-500 text-xs mt-0.5">{s.exclusions}</p>
                      </div>}
                      {s.note && <div className="col-span-2">
                        <p className="text-xs bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-300 border border-amber-100 dark:border-amber-800 rounded-lg px-3 py-2">
                          ℹ️ {s.note}
                        </p>
                      </div>}
                    </div>

                    {s.documents && (
                      <div>
                        <p className="text-xs text-gray-400 font-medium uppercase mb-1.5">Required Documents</p>
                        <div className="flex flex-wrap gap-1.5">
                          {s.documents.map((d: string, j: number) => (
                            <span key={j} className="flex items-center gap-1 text-xs bg-farm-50 dark:bg-farm-950/50 text-farm-700 dark:text-farm-300 px-2 py-0.5 rounded-full">
                              <CheckCircle size={10} /> {d}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-800">
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        {s.online_apply_url ? (
                          <><Globe size={12} className="text-green-500" /> <span>Apply online: <span className="font-medium text-gray-700 dark:text-gray-200">{s.apply}</span></span></>
                        ) : (
                          <><MapPin size={12} className="text-amber-500" /> <span>Apply at: <span className="font-medium text-gray-700 dark:text-gray-200">{s.apply}</span></span></>
                        )}
                      </div>

                      {s.online_apply_url ? (
                        <a
                          href={s.online_apply_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-lg transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Apply Now <ExternalLink size={11} />
                        </a>
                      ) : null}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            ))}

            {filtered.length === 0 && (
              <div className="text-center py-12 text-gray-400">
                <p>No schemes match this filter</p>
              </div>
            )}
          </div>
        </motion.div>
      </main>
    </div>
  );
}
