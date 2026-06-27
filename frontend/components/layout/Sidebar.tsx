"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard, MessageSquare, Leaf, CloudSun, TrendingUp,
  FileText, Calendar, Satellite, Bell, Zap, Settings, ChevronRight,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "AI Assistant", icon: MessageSquare },
  { href: "/disease", label: "Disease Detection", icon: Leaf },
  { href: "/weather", label: "Weather", icon: CloudSun },
  { href: "/market", label: "Market Prices", icon: TrendingUp },
  { href: "/schemes", label: "Govt. Schemes", icon: FileText },
  { href: "/calendar", label: "Crop Calendar", icon: Calendar },
  { href: "/satellite", label: "Satellite View", icon: Satellite },
  { href: "/alerts", label: "Alerts", icon: Bell, badge: 3 },
  { href: "/simulation", label: "What-If Simulator", icon: Zap, highlight: true },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 min-h-screen bg-farm-gradient flex flex-col relative overflow-hidden">
      {/* Decorative circles */}
      <div className="absolute -top-16 -right-16 w-48 h-48 rounded-full bg-white/5" />
      <div className="absolute -bottom-8 -left-8 w-32 h-32 rounded-full bg-white/5" />

      {/* Logo */}
      <div className="p-6 pb-4 relative">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/15 backdrop-blur flex items-center justify-center text-2xl shadow-lg">
            🌾
          </div>
          <div>
            <p className="font-display font-bold text-white text-lg leading-none">FarmSphere</p>
            <p className="text-farm-300 text-xs mt-0.5 font-medium">AI Platform</p>
          </div>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-2 space-y-0.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                whileHover={{ x: 3 }}
                whileTap={{ scale: 0.98 }}
                className={`sidebar-item group ${isActive ? "active" : ""} ${item.highlight ? "border border-harvest-400/40 bg-harvest-400/10 hover:bg-harvest-400/20" : ""}`}
              >
                <Icon size={17} className={item.highlight ? "text-harvest-400" : ""} />
                <span className={item.highlight ? "text-harvest-300" : ""}>{item.label}</span>
                {item.badge && (
                  <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[18px] text-center">
                    {item.badge}
                  </span>
                )}
                {item.highlight && (
                  <span className="ml-auto text-harvest-400 text-xs font-bold">⭐</span>
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="p-4 border-t border-white/10">
        <div className="glass-card-dark p-3 rounded-xl">
          <p className="text-xs text-farm-300 font-medium mb-1">Powered by</p>
          <p className="text-white text-sm font-semibold">Gemini 2.0 Flash</p>
          <p className="text-farm-400 text-xs">17 AI Agents Active</p>
          <div className="mt-2 flex gap-1">
            {["LangGraph", "ChromaDB", "GEE"].map((tag) => (
              <span key={tag} className="text-xs bg-white/10 text-white px-1.5 py-0.5 rounded-md">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}
