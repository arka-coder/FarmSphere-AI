"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

export default function DigitalClock() {
  const [time, setTime] = useState<Date | null>(null);

  useEffect(() => {
    setTime(new Date());
    const interval = setInterval(() => {
      setTime(new Date());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  if (!time) return null;

  const timeString = time.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });

  const [timePart, amPm] = timeString.split(" ");
  const [hours, minutes] = timePart.split(":");

  return (
    <div className="group relative flex items-center rounded-full border border-white/60 bg-white/40 px-6 py-2.5 shadow-[0_8px_32px_rgba(0,0,0,0.06)] backdrop-blur-xl transition-all duration-300 hover:bg-white/60 hover:shadow-[0_8px_32px_rgba(0,0,0,0.1)] overflow-hidden">
      {/* Animated subtle gradient background */}
      <div className="absolute inset-0 bg-gradient-to-r from-emerald-400/10 via-transparent to-blue-400/10 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
      
      <div className="relative flex items-center gap-2 leading-none">
        <span className="font-mono text-[17px] font-bold tracking-tight text-slate-800 tabular-nums">
          {hours}
        </span>
        
        {/* Pulsing colon */}
        <div className="flex flex-col items-center justify-center gap-[4px]">
          <motion.div
            animate={{ opacity: [1, 0.2, 1] }}
            transition={{ repeat: Infinity, duration: 1, ease: "easeInOut" }}
            className="h-[4px] w-[4px] rounded-full bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.5)]"
          />
          <motion.div
            animate={{ opacity: [1, 0.2, 1] }}
            transition={{ repeat: Infinity, duration: 1, ease: "easeInOut" }}
            className="h-[4px] w-[4px] rounded-full bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.5)]"
          />
        </div>
        
        <span className="font-mono text-[17px] font-bold tracking-tight text-slate-800 tabular-nums">
          {minutes}
        </span>
        
        <span className="ml-1 text-[12px] font-black uppercase tracking-widest text-emerald-700/80 mt-[2px]">
          {amPm}
        </span>
      </div>
    </div>
  );
}
