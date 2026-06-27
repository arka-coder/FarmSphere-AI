"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, CloudRain, Bug, TrendingDown, AlertTriangle } from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import { getAlerts, type Alert } from "@/lib/api";

const severityConfig = {
  critical: { bg: "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800", text: "text-red-700 dark:text-red-300", badge: "bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300" },
  high:     { bg: "bg-orange-50 dark:bg-orange-950/30 border-orange-200 dark:border-orange-800", text: "text-orange-700 dark:text-orange-300", badge: "bg-orange-100 dark:bg-orange-900/50 text-orange-700 dark:text-orange-300" },
  medium:   { bg: "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800", text: "text-amber-700 dark:text-amber-300", badge: "bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300" },
  low:      { bg: "bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800", text: "text-blue-700 dark:text-blue-300", badge: "bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300" },
};

const typeIcon: Record<string, React.ReactNode> = {
  weather: <CloudRain size={18} />,
  disease: <Bug size={18} />,
  pest:    <Bug size={18} />,
  market:  <TrendingDown size={18} />,
};

const fallbackAlerts: Alert[] = [
  { type: "weather", severity: "high", title: "🌧️ Heavy Rain Tomorrow", message: "70% chance of rainfall. Avoid pesticide spraying.", action: "Postpone any planned chemical applications" },
  { type: "disease", severity: "medium", title: "🍄 High Humidity Alert", message: "Humidity above 80% — fungal disease risk elevated.", action: "Apply preventive fungicide within 24 hours" },
  { type: "market", severity: "low", title: "📈 Tomato Prices Rising", message: "Tomato prices up 12% this week. Good selling opportunity.", action: "Contact Azadpur Mandi" },
];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    getAlerts()
      .then((d) => setAlerts(d.alerts?.length ? d.alerts : fallbackAlerts))
      .catch(() => setAlerts(fallbackAlerts))
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter === "all" ? alerts : alerts.filter((a) => a.type === filter || a.severity === filter);

  const countBySeverity = (sev: string) => alerts.filter((a) => a.severity === sev).length;

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto space-y-6">
          {/* Header */}
          <div className="bg-gradient-to-r from-rose-600 to-red-700 rounded-2xl p-6 text-white relative overflow-hidden">
            <div className="absolute -right-6 -top-6 text-8xl opacity-20">🔔</div>
            <div className="flex items-center gap-3">
              <Bell size={20} />
              <div>
                <h1 className="text-2xl font-bold">Proactive Alerts</h1>
                <p className="text-rose-200 text-sm mt-0.5">Real-time AI monitoring — {alerts.length} active alerts</p>
              </div>
            </div>
          </div>

          {/* Severity summary */}
          <div className="grid grid-cols-3 gap-3">
            {(["high", "medium", "low"] as const).map((sev) => {
              const cfg = severityConfig[sev];
              const count = countBySeverity(sev);
              return (
                <div key={sev} className={`rounded-xl p-4 border ${cfg.bg} text-center`}>
                  <p className={`text-2xl font-bold ${cfg.text}`}>{count}</p>
                  <p className={`text-xs font-semibold mt-0.5 capitalize ${cfg.text}`}>{sev} priority</p>
                </div>
              );
            })}
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-2">
            {["all", "weather", "disease", "market", "high", "medium"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all capitalize ${
                  filter === f
                    ? "bg-rose-600 text-white shadow"
                    : "bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:border-rose-400"
                }`}
              >
                {f === "all" ? "🔔 All" : f}
              </button>
            ))}
          </div>

          {/* Alerts list */}
          {loading ? (
            <div className="text-center py-12">
              <div className="w-8 h-8 border-2 border-rose-200 border-t-rose-600 rounded-full animate-spin mx-auto" />
              <p className="text-gray-400 text-sm mt-3">Loading alerts...</p>
            </div>
          ) : (
            <div className="space-y-3">
              <AnimatePresence>
                {filtered.map((alert, i) => {
                  const cfg = severityConfig[alert.severity] ?? severityConfig.low;
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 8 }}
                      transition={{ delay: i * 0.05 }}
                      className={`p-4 rounded-xl border ${cfg.bg}`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`mt-0.5 ${cfg.text}`}>{typeIcon[alert.type] ?? <AlertTriangle size={18} />}</div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <p className={`font-semibold text-sm ${cfg.text}`}>{alert.title}</p>
                            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${cfg.badge} uppercase`}>
                              {alert.severity}
                            </span>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.badge} capitalize`}>
                              {alert.type}
                            </span>
                          </div>
                          <p className={`text-sm mt-1.5 ${cfg.text} opacity-80`}>{alert.message}</p>
                          <div className={`mt-2 text-xs font-semibold ${cfg.text} flex items-center gap-1`}>
                            <span>✅ Recommended action:</span>
                            <span className="opacity-90">{alert.action}</span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
              {filtered.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                  <Bell size={32} className="mx-auto mb-3 opacity-40" />
                  <p>No alerts matching this filter</p>
                </div>
              )}
            </div>
          )}
        </motion.div>
      </main>
    </div>
  );
}
