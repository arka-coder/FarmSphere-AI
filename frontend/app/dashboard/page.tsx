"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  ChevronDown,
  CloudSun,
  MapPin,
  MessageCircle,
  Radar,
  Satellite,
  ShieldCheck,
  Sparkles,
  Sprout,
} from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import { getAlerts, getSatelliteData, getWeather } from "@/lib/api";
import { useFarm } from "@/contexts/FarmContext";

const actions = [
  {
    title: "Inspect tomato leaves before evening humidity rises",
    detail: "Disease risk climbs after tonight's rain window.",
    href: "/disease",
    priority: "High",
  },
  {
    title: "Delay pesticide application by 24 hours",
    detail: "Rain probability makes spray loss likely tomorrow.",
    href: "/weather",
    priority: "Medium",
  },
  {
    title: "Hold tomato harvest for price confirmation",
    detail: "Market agent sees a short-term upward signal.",
    href: "/market",
    priority: "Low",
  },
];

const agentFlow = [
  "Weather Agent",
  "Satellite Agent",
  "Disease Agent",
  "Risk Agent",
  "Recommendation Agent",
  "Explainability Agent",
];

export default function DashboardPage() {
  const { cropType, setCropType, location: contextLocation, setLocation } = useFarm();
  const [weather, setWeather] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [satellite, setSatellite] = useState<any>(null);
  const [locationStatus, setLocationStatus] = useState<"detecting" | "precise" | "default" | "unavailable">("detecting");

  useEffect(() => {
    const loadDashboardData = (coords?: { lat: number; lon: number }) => {
      Promise.all([
        getWeather(coords).catch(() => null),
        getAlerts(coords).catch(() => ({ alerts: [] })),
        getSatelliteData(cropType).catch(() => null),
      ]).then(([w, a, s]) => {
        setWeather(w);
        setAlerts(a?.alerts || []);
        setSatellite(s);
      });
    };

    if (!navigator.geolocation) {
      setLocationStatus("unavailable");
      loadDashboardData();
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocationStatus("precise");
        loadDashboardData({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        });
      },
      () => {
        setLocationStatus("default");
        loadDashboardData();
      },
      { timeout: 7000, maximumAge: 300000 },
    );
  }, []);

  const today = useMemo(
    () =>
      new Date().toLocaleDateString("en-IN", {
        weekday: "long",
        day: "numeric",
        month: "long",
      }),
    [],
  );

  const temp = weather?.temperature ?? 28;
  const rainChance = weather?.forecast?.[0]?.rain_chance ?? 70;
  const ndvi = satellite?.current_ndvi?.toFixed?.(2) ?? "0.63";
  const alertCount = alerts.length;
  const locationName = weather?.location ?? (
    locationStatus === "detecting" ? "Detecting your location..." : "Default farm location"
  );
  const locationLabel =
    locationStatus === "precise" ? "Precise location" :
    locationStatus === "detecting" ? "Detecting location" :
    locationStatus === "unavailable" ? "Browser location unavailable" :
    "Using default location";

  return (
    <div className="relative flex h-screen overflow-hidden bg-base">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,#f7faf8_0%,#eef7f0_44%,#f8fbff_100%)]" />
      <div className="absolute inset-x-0 top-0 h-72 bg-[radial-gradient(circle_at_50%_0%,rgba(16,185,129,0.16),transparent_46%)]" />
      <Sidebar />

      <main className="relative flex flex-1 flex-col overflow-hidden">
        <TopNav />

        <div className="flex-1 overflow-y-auto px-5 pb-10 pt-32 scrollbar-hide md:px-8">
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
            className="mx-auto grid max-w-7xl gap-6 xl:grid-cols-[1fr_360px]"
          >
            <section className="overflow-hidden rounded-[32px] border border-white/80 bg-white/78 shadow-[0_30px_110px_rgba(15,23,42,0.09)] backdrop-blur-3xl">
              <div className="grid gap-0 lg:grid-cols-[1fr_300px]">
                <div className="p-6 md:p-8 lg:p-10">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.18em] text-emerald-800">
                      <Sparkles size={14} />
                      Today's Farm Intelligence
                    </span>
                    <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-500">
                      {today}
                    </span>
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-100 bg-white px-3 py-1.5 text-xs font-semibold text-emerald-700">
                      <MapPin size={13} />
                      {locationLabel}
                    </span>
                  </div>

                  <h1 className="mt-6 max-w-4xl text-4xl font-semibold leading-[1.04] tracking-tight text-slate-950 md:text-6xl">
                    FarmSphere recommends one action before the next rain window.
                  </h1>
                  <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
                    {locationName} is now the active farm context. The <span className="capitalize">{cropType}</span> crop status is stable, but humidity and rainfall are raising fungal risk.
                    The AI is prioritizing inspection and timing over more field activity.
                  </p>

                  {/* Restored Temperature/Weather Grid */}
                  <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                    {[
                      { icon: CloudSun, label: "Weather", value: `${temp}°C`, sub: `${rainChance}% rain`, tone: "text-amber-600" },
                      { icon: Sprout, label: "Crop Status", value: "Stable", sub: `field A`, tone: "text-emerald-700" },
                      { icon: ShieldCheck, label: "Risk Score", value: "64", sub: "moderate", tone: "text-orange-600" },
                      { icon: Satellite, label: "Satellite", value: ndvi, sub: "NDVI improving", tone: "text-blue-600" },
                    ].map((item, index) => {
                      const Icon = item.icon;
                      return (
                        <motion.div
                          key={item.label}
                          initial={{ opacity: 0, y: 12 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.1 + index * 0.06 }}
                          className="rounded-2xl border border-slate-200/80 bg-white/70 p-4"
                        >
                          <Icon size={18} className={item.tone} strokeWidth={1.8} />
                          <p className="mt-4 text-xs font-bold uppercase tracking-[0.16em] text-slate-400">
                            {item.label}
                          </p>
                          <p className="mt-1 text-3xl font-semibold tracking-tight text-slate-950">
                            {item.value}
                          </p>
                          <p className="text-sm font-medium text-slate-500">{item.sub}</p>
                        </motion.div>
                      );
                    })}
                  </div>

                  <div className="mt-8 rounded-3xl border border-emerald-100 bg-gradient-to-br from-white to-emerald-50/50 p-6 shadow-sm">
                    <div className="flex items-center gap-3 mb-4">
                      <CloudSun className="text-emerald-600" size={20} />
                      <h3 className="text-sm font-bold uppercase tracking-[0.15em] text-emerald-900">Live Field Conditions</h3>
                    </div>
                    <p className="text-[15px] leading-relaxed text-slate-700 font-medium max-w-3xl">
                      Your <strong className="text-emerald-700 capitalize">{cropType} crop</strong> remains structurally stable with an improving NDVI of <strong className="text-blue-600">{ndvi}</strong>. However, an upcoming <strong className="text-amber-600">{rainChance}% chance of rain</strong> at <strong className="text-amber-600">{temp}°C</strong> is actively elevating the fungal disease risk score to <strong className="text-orange-600">64 (moderate)</strong>. Immediate preventative action is recommended.
                    </p>
                  </div>

                  <div className="mt-8 rounded-3xl bg-slate-950 p-5 text-white shadow-[0_24px_70px_rgba(15,23,42,0.16)]">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div>
                        <p className="flex items-center gap-2 text-sm font-semibold text-emerald-200">
                          <BrainCircuit size={17} />
                          AI recommendation
                        </p>
                        <p className="mt-2 text-2xl font-semibold tracking-tight">
                          Inspect lower leaves and postpone spray until rainfall clears.
                        </p>
                      </div>
                      <Link
                        href="/chat"
                        className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-emerald-50 focus:outline-none focus:ring-2 focus:ring-emerald-300"
                      >
                        Ask why
                        <ArrowRight size={16} />
                      </Link>
                    </div>
                    <div className="mt-6 grid gap-2 md:grid-cols-3">
                      {actions.map((action) => (
                        <Link key={action.title} href={action.href} className="group rounded-2xl border border-white/10 bg-white/[0.07] p-4 transition hover:bg-white/[0.12]">
                          <span className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-200">
                            {action.priority}
                          </span>
                          <p className="mt-2 text-sm font-semibold leading-6">{action.title}</p>
                          <p className="mt-1 text-xs leading-5 text-white/55">{action.detail}</p>
                        </Link>
                      ))}
                    </div>
                  </div>
                </div>

                <aside className="border-t border-slate-200/70 bg-slate-50/70 p-6 lg:border-l lg:border-t-0">
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">Live Agent Trace</p>
                  <div className="mt-5 space-y-4">
                    {agentFlow.map((agent, index) => (
                      <motion.div
                        key={agent}
                        initial={{ opacity: 0, x: 12 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.18 + index * 0.08 }}
                        className="flex items-center gap-3"
                      >
                        <span className={`flex h-9 w-9 items-center justify-center rounded-xl ${index < 4 ? "bg-emerald-100 text-emerald-700" : "bg-white text-slate-400"}`}>
                          {index < 4 ? <CheckCircle2 size={17} /> : <Radar size={17} />}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-semibold text-slate-800">{agent}</p>
                          <p className="text-xs text-slate-500">{index < 4 ? "Completed" : "Monitoring"}</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </aside>
              </div>
            </section>

            <aside className="space-y-4">
              <div className="rounded-[28px] border border-white/80 bg-white/72 p-5 shadow-[0_22px_80px_rgba(15,23,42,0.08)] backdrop-blur-2xl">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">Context Panel</p>
                <div className="mt-4 space-y-3">
                  {[
                    ["Current crop", cropType],
                    ["Location", contextLocation],
                    ["Retrieved docs", "5 agronomy sources"],
                    ["Memory", "Irrigation every 3 days"],
                    ["Pending alerts", `${alertCount} active`],
                  ].map(([label, value]) => (
                    <div key={label} className="flex items-center justify-between rounded-2xl bg-white/70 px-4 py-3 text-sm">
                      <span className="text-slate-500">{label}</span>
                      {label === "Current crop" ? (
                        <div className="relative group flex items-center justify-center gap-1.5 rounded-full border border-emerald-200/60 bg-emerald-50/50 py-1 pl-3 pr-2 text-xs font-semibold shadow-sm transition hover:bg-emerald-100/50 cursor-pointer">
                          <Sprout size={13} className="text-emerald-600" />
                          <select
                            value={value}
                            onChange={(e) => setCropType(e.target.value)}
                            className="appearance-none bg-transparent outline-none cursor-pointer capitalize text-left font-bold text-emerald-800 pr-4 z-10 font-sans"
                          >
                            {["tomato", "wheat", "rice", "cotton", "sugarcane"].map((c) => (
                              <option key={c} value={c} className="font-sans text-sm text-slate-800 text-left">{c}</option>
                            ))}
                          </select>
                          <ChevronDown size={13} className="absolute right-2 text-emerald-600/70 pointer-events-none" />
                        </div>
                      ) : label === "Location" ? (
                        <div className="relative flex items-center justify-center gap-1.5 rounded-full border border-blue-200/60 bg-blue-50/50 py-1 pl-3 pr-3 text-xs font-semibold shadow-sm">
                          <MapPin size={13} className="text-blue-600" />
                          <span className="font-sans font-bold text-blue-800 max-w-[140px] truncate">
                            {value}
                          </span>
                        </div>
                      ) : (
                        <span className="max-w-[55%] truncate text-right font-semibold text-slate-900">{value}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className={`rounded-[28px] border p-5 shadow-[0_22px_80px_rgba(15,23,42,0.07)] ${
                alertCount > 0
                  ? "border-amber-200/70 bg-amber-50/80"
                  : "border-emerald-200/70 bg-emerald-50/80"
              }`}>
                <p className={`flex items-center gap-2 text-sm font-bold ${alertCount > 0 ? "text-amber-800" : "text-emerald-800"}`}>
                  <AlertTriangle size={17} />
                  Actual Alerts
                </p>
                {alertCount > 0 ? (
                  <div className="mt-3 space-y-3">
                    {alerts.map((alert, index) => (
                      <div key={`${alert.title}-${index}`} className="rounded-2xl border border-white/70 bg-white/65 px-4 py-3">
                        <div className="flex items-start justify-between gap-3">
                          <p className="text-sm font-bold text-slate-900">{alert.title}</p>
                          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-bold uppercase text-amber-700">
                            {alert.severity}
                          </span>
                        </div>
                        <p className="mt-1 text-sm leading-6 text-slate-600">{alert.message}</p>
                        <p className="mt-2 text-xs font-bold text-emerald-700">{alert.action}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="mt-2 text-sm leading-6 text-emerald-800/75">
                    No active weather, disease, pest, or market alerts for the current farm context.
                  </p>
                )}
              </div>

              <Link
                href="/chat"
                className="flex items-center justify-between rounded-[28px] bg-emerald-950 p-5 text-white shadow-[0_24px_80px_rgba(6,78,59,0.20)] transition hover:-translate-y-0.5"
              >
                <span>
                  <span className="block text-sm font-semibold text-emerald-200">Open workspace</span>
                  <span className="mt-1 block text-xl font-semibold">Talk to FarmSphere</span>
                </span>
                <MessageCircle size={24} />
              </Link>
            </aside>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
