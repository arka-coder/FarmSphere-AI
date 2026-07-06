"use client";

import { useState, useEffect } from "react";
import { Clock } from "lucide-react";

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
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });

  return (
    <div className="flex items-center gap-3 rounded-full border border-white/80 bg-white/70 pl-4 pr-1.5 py-1.5 shadow-[0_12px_40px_rgba(15,23,42,0.08)] backdrop-blur-2xl">
      <div className="flex flex-col items-end leading-tight">
        <span className="font-mono text-[13px] font-bold text-slate-800 tracking-tight">
          {timeString}
        </span>
      </div>
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 text-white shadow-inner shadow-black/20">
        <Clock size={14} className="text-emerald-400" strokeWidth={2.5} />
      </div>
    </div>
  );
}
