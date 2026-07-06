"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  Bell,
  BookOpen,
  CalendarDays,
  Command,
  LineChart,
  MessageCircle,
  Microscope,
  Satellite,
  Sparkles,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Home", icon: Command },
  { href: "/chat", label: "AI Assistant", icon: MessageCircle },
  { href: "/disease", label: "Crop Health", icon: Microscope },
  { href: "/satellite", label: "Satellite", icon: Satellite },
  { href: "/market", label: "Market", icon: LineChart },
  { href: "/calendar", label: "Planner", icon: CalendarDays },
  { href: "/schemes", label: "Knowledge", icon: BookOpen },
  { href: "/alerts", label: "Alerts", icon: Bell },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <motion.aside
      initial={{ y: -18, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
      className="pointer-events-none fixed inset-x-0 top-5 z-50 flex justify-center px-4"
    >
      <div className="pointer-events-auto flex w-fit max-w-[1080px] items-center gap-2 rounded-[28px] border border-white/75 bg-white/72 pl-3 pr-5 py-2 shadow-[0_18px_70px_rgba(15,23,42,0.10),inset_0_1px_0_rgba(255,255,255,0.92)] backdrop-blur-2xl">
        <Link
          href="/dashboard"
          className="mr-[28px] flex h-[34px] shrink-0 items-center gap-2 rounded-[14px] border border-white/[0.08] bg-gradient-to-b from-[#101418] via-[#0B1512] to-[#07100D] pl-1.5 pr-3 text-white shadow-[0_2px_10px_rgba(0,0,0,0.1),0_8px_30px_rgba(0,0,0,0.05)] transition hover:brightness-110"
          aria-label="FarmSphere AI home"
        >
          <motion.div
            initial={{ filter: "drop-shadow(0 0 10px rgba(52,211,153,0.7))" }}
            animate={{ filter: "drop-shadow(0 0 0px rgba(52,211,153,0))" }}
            transition={{ duration: 3, ease: "easeOut" }}
            className="flex h-6 w-6 items-center justify-center rounded-[8px] bg-white/[0.03] shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]"
          >
            <Sparkles size={15} className="text-emerald-400" strokeWidth={1.5} />
          </motion.div>
          <span className="hidden font-serif text-[13.5px] font-normal tracking-[0.03em] text-slate-100 sm:inline">
            FarmSphere AI
          </span>
        </Link>

        <nav className="flex items-center gap-1" aria-label="Primary">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));

            return (
              <Link key={item.href} href={item.href} className="shrink-0">
                <motion.div
                  whileTap={{ scale: 0.98 }}
                  className={`group relative flex h-10 items-center gap-2 rounded-[14px] px-3 text-[13px] transition-all duration-200 ease-out hover:-translate-y-[1px] ${
                    isActive
                      ? "text-emerald-800 opacity-100 font-bold"
                      : "text-slate-500 opacity-80 font-semibold hover:bg-slate-50/80 hover:text-slate-800 hover:opacity-100"
                  }`}
                >
                  <Icon
                    size={17}
                    strokeWidth={1.8}
                    className={isActive ? "text-emerald-700" : "text-slate-400 group-hover:text-emerald-700"}
                  />
                  <span className="hidden whitespace-nowrap lg:inline">{item.label}</span>
                </motion.div>
              </Link>
            );
          })}
        </nav>
      </div>
    </motion.aside>
  );
}
