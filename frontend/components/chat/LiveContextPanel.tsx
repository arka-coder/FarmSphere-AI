"use client";

import { motion } from "framer-motion";
import {
  BrainCircuit,
  ChevronDown,
  CloudSun,
  Database,
  GitBranch,
  MapPin,
  MemoryStick,
  Radar,
  Satellite,
  ShieldCheck,
  Sprout,
  ThermometerSun,
  Droplets,
  AlertTriangle,
} from "lucide-react";
import { useFarm } from "@/contexts/FarmContext";

interface AgentTrace {
  name: string;
  icon: any;
  status: "waiting" | "retrieving" | "running" | "completed";
}

interface LiveContextPanelProps {
  activeAgent?: string;
  isProcessing?: boolean;
}

export default function LiveContextPanel({ activeAgent, isProcessing }: LiveContextPanelProps) {
  const { cropType, setCropType, location, setLocation } = useFarm();
  
  // Map internal agent names to display names and statuses based on activeAgent
  const agents: AgentTrace[] = [
    { name: "Orchestrator", icon: GitBranch, status: !isProcessing ? "completed" : (activeAgent === "orchestrator" ? "running" : "completed") },
    { name: "Vision Agent", icon: Radar, status: !isProcessing ? "waiting" : (activeAgent === "vision_agent" ? "running" : (activeAgent ? "completed" : "waiting")) },
    { name: "Weather Agent", icon: CloudSun, status: !isProcessing ? "waiting" : (activeAgent === "weather_agent" ? "retrieving" : (activeAgent ? "completed" : "waiting")) },
    { name: "Satellite Agent", icon: Satellite, status: !isProcessing ? "waiting" : (activeAgent === "satellite_agent" ? "retrieving" : (activeAgent ? "completed" : "waiting")) },
    { name: "Knowledge Agent", icon: Database, status: !isProcessing ? "waiting" : (activeAgent === "knowledge_agent" ? "retrieving" : (activeAgent ? "completed" : "waiting")) },
    { name: "Risk Agent", icon: ShieldCheck, status: !isProcessing ? "waiting" : (activeAgent === "risk_agent" ? "running" : (activeAgent ? "completed" : "waiting")) },
    { name: "Recommendation", icon: BrainCircuit, status: !isProcessing ? "waiting" : (activeAgent === "recommendation_agent" ? "running" : (activeAgent ? "completed" : "waiting")) },
  ];

  return (
    <div className="flex h-full flex-col gap-4 overflow-y-auto pb-6 scrollbar-hide pr-2">
      
      {/* Active Farm Context */}
      <div className="rounded-[24px] border border-white/80 bg-white/70 p-5 shadow-[0_8px_30px_rgba(15,23,42,0.04)] backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-4">
          <MapPin size={16} className="text-emerald-600" />
          <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-slate-500">Active Farm</h3>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl bg-white/60 p-3">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Crop</p>
            <div className="mt-1 flex items-center gap-1.5 relative">
              <Sprout size={14} className="text-emerald-500" />
              <select
                value={cropType}
                onChange={(e) => setCropType(e.target.value)}
                className="appearance-none text-sm font-semibold text-slate-900 capitalize bg-transparent outline-none cursor-pointer w-full pr-4 z-10 font-sans"
              >
                {["tomato", "wheat", "rice", "cotton", "sugarcane"].map((c) => (
                  <option key={c} value={c} className="font-sans text-left">{c}</option>
                ))}
              </select>
              <ChevronDown size={14} className="absolute right-0 text-slate-400 pointer-events-none" />
            </div>
          </div>
          <div className="rounded-xl bg-white/60 p-3">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Location</p>
            <div className="mt-1 flex items-center gap-1.5 relative">
              <MapPin size={14} className="text-blue-500" />
              <span className="text-sm font-semibold text-slate-900 bg-transparent truncate">
                {location}
              </span>
            </div>
          </div>
          <div className="rounded-xl bg-white/60 p-3">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Stage</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">Flowering</p>
          </div>
          <div className="rounded-xl bg-white/60 p-3">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Season</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">Kharif</p>
          </div>
        </div>
      </div>

      {/* Live Conditions */}
      <div className="rounded-[24px] border border-white/80 bg-white/70 p-5 shadow-[0_8px_30px_rgba(15,23,42,0.04)] backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-4">
          <Radar size={16} className="text-blue-600" />
          <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-slate-500">Live Conditions</h3>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-xl bg-white/60 px-3 py-2">
            <div className="flex items-center gap-2 text-slate-600">
              <ThermometerSun size={14} />
              <span className="text-xs font-medium">Weather</span>
            </div>
            <span className="text-sm font-semibold text-slate-900">28°C, Rain Likely</span>
          </div>
          <div className="flex items-center justify-between rounded-xl bg-white/60 px-3 py-2">
            <div className="flex items-center gap-2 text-slate-600">
              <Satellite size={14} />
              <span className="text-xs font-medium">NDVI</span>
            </div>
            <span className="text-sm font-semibold text-slate-900">0.63 (Improving)</span>
          </div>
          <div className="flex items-center justify-between rounded-xl bg-white/60 px-3 py-2">
            <div className="flex items-center gap-2 text-slate-600">
              <Droplets size={14} />
              <span className="text-xs font-medium">Soil Moisture</span>
            </div>
            <span className="text-sm font-semibold text-slate-900">42%</span>
          </div>
        </div>
      </div>

      {/* AI Memory & Knowledge */}
      <div className="rounded-[24px] border border-white/80 bg-white/70 p-5 shadow-[0_8px_30px_rgba(15,23,42,0.04)] backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-3">
          <MemoryStick size={16} className="text-purple-600" />
          <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-slate-500">Knowledge & Memory</h3>
        </div>
        <div className="space-y-2">
          <div className="rounded-xl border border-purple-100/50 bg-purple-50/50 px-3 py-2">
            <p className="text-[10px] font-bold uppercase tracking-wider text-purple-600/70">User Preference</p>
            <p className="mt-0.5 text-xs font-medium text-slate-700">Prefers organic treatments</p>
          </div>
          <div className="rounded-xl border border-slate-100 bg-white/50 px-3 py-2">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Retrieved Docs</p>
            <p className="mt-0.5 text-xs font-medium text-slate-700">5 sources (ICAR, KVK, Agmarknet)</p>
          </div>
        </div>
      </div>

      {/* Active Alerts */}
      <div className="rounded-[24px] border border-amber-200/50 bg-amber-50/50 p-5 shadow-[0_8px_30px_rgba(251,191,36,0.1)] backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle size={16} className="text-amber-600" />
          <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-amber-800/70">Active Alerts</h3>
        </div>
        <div className="space-y-2">
          <div className="flex items-start gap-2 rounded-xl bg-white/60 px-3 py-2">
            <div className="mt-0.5 h-1.5 w-1.5 rounded-full bg-amber-500" />
            <div>
              <p className="text-xs font-semibold text-slate-900">Heavy Rain Window</p>
              <p className="text-[10px] text-slate-500">Expected in 14 hours</p>
            </div>
          </div>
          <div className="flex items-start gap-2 rounded-xl bg-white/60 px-3 py-2">
            <div className="mt-0.5 h-1.5 w-1.5 rounded-full bg-orange-500" />
            <div>
              <p className="text-xs font-semibold text-slate-900">Disease Risk</p>
              <p className="text-[10px] text-slate-500">Elevated fungal pressure</p>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Activity */}
      <div className="rounded-[24px] border border-white/5 bg-slate-950 p-5 text-white shadow-[0_16px_40px_rgba(15,23,42,0.2)]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BrainCircuit size={16} className="text-emerald-300" />
            <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-slate-300">Agent Activity</h3>
          </div>
          {isProcessing && (
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          )}
        </div>
        
        <div className="space-y-3">
          {agents.map((agent) => {
            const Icon = agent.icon;
            return (
              <div key={agent.name} className="flex items-center justify-between group">
                <div className="flex items-center gap-3">
                  <span className={`flex h-8 w-8 items-center justify-center rounded-lg transition-colors ${
                    agent.status === "running" || agent.status === "retrieving" 
                      ? "bg-emerald-500/20 text-emerald-300" 
                      : agent.status === "completed"
                        ? "bg-white/10 text-white/70"
                        : "bg-transparent text-white/30"
                  }`}>
                    <Icon size={14} />
                  </span>
                  <span className={`text-xs font-medium transition-colors ${
                    agent.status === "waiting" ? "text-slate-500" : "text-slate-200"
                  }`}>
                    {agent.name}
                  </span>
                </div>
                <span className={`text-[10px] font-bold uppercase tracking-wider transition-colors ${
                  agent.status === "running" ? "text-emerald-400" :
                  agent.status === "retrieving" ? "text-blue-400" :
                  agent.status === "completed" ? "text-slate-500" :
                  "text-slate-700"
                }`}>
                  {agent.status}
                </span>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
