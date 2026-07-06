"use client";
import { motion } from "framer-motion";

interface Props {
  confidence: number;
  label?: string;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
  alternatives?: { name: string; confidence: number }[];
}

function getColor(c: number): string {
  if (c >= 0.75) return "#10b981";
  if (c >= 0.50) return "#f59e0b";
  return "#f43f5e";
}

function getGlow(c: number): string {
  if (c >= 0.75) return "rgba(16,185,129,0.3)";
  if (c >= 0.50) return "rgba(245,158,11,0.3)";
  return "rgba(244,63,94,0.3)";
}

export default function ConfidenceGauge({ confidence, label, showLabel = true, size = "md", alternatives }: Props) {
  const pct = Math.round(confidence * 100);
  const color = getColor(confidence);
  const glow  = getGlow(confidence);
  const barH = size === "sm" ? 4 : size === "lg" ? 10 : 6;

  return (
    <div className="space-y-3">
      {/* Main block */}
      <div className="flex items-center gap-3 rounded-xl p-3"
        style={{ background: `${color}10`, border: `1px solid ${color}30` }}>
        {/* Circle */}
        <div className="relative w-11 h-11 shrink-0">
          <svg viewBox="0 0 36 36" className="w-11 h-11 -rotate-90">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="2.5" />
            <motion.circle
              cx="18" cy="18" r="15.9" fill="none"
              stroke={color} strokeWidth="2.5" strokeLinecap="round"
              strokeDasharray="100"
              initial={{ strokeDashoffset: 100 }}
              animate={{ strokeDashoffset: 100 - pct }}
              transition={{ duration: 1.2, ease: [0.34, 1.56, 0.64, 1] }}
              style={{ filter: `drop-shadow(0 0 4px ${glow})` }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-bold" style={{ color }}>{pct}%</span>
          </div>
        </div>

        {/* Text */}
        <div className="flex-1 min-w-0">
          {showLabel && label && (
            <p className="font-semibold text-sm truncate leading-tight" style={{ color: "#0f172a" }}>{label}</p>
          )}
          <p className="text-xs mt-0.5 leading-relaxed" style={{ color: "#64748b" }}>
            {pct >= 75 ? "High confidence — reliable diagnosis" :
             pct >= 50 ? "Medium confidence — additional images recommended" :
             "Low confidence — human expert review needed"}
          </p>
        </div>
      </div>

      {/* Bar */}
      <div className="rounded-full overflow-hidden" style={{ height: barH, background: "rgba(255,255,255,0.06)" }}>
        <motion.div
          className="h-full rounded-full"
          style={{ background: `linear-gradient(90deg, ${color}aa, ${color})`, boxShadow: `0 0 8px ${glow}` }}
          initial={{ width: "0%" }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1.2, ease: [0.34, 1.56, 0.64, 1] }}
        />
      </div>

      {/* Alternatives */}
      {alternatives && alternatives.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: "#475569" }}>
            Other Possibilities
          </p>
          {alternatives.map((alt, i) => {
            const ac = alt.confidence;
            const aColor = getColor(ac);
            return (
              <div key={i} className="flex items-center gap-2.5">
                <span className="text-xs truncate" style={{ color: "#64748b", width: "140px", flexShrink: 0 }}>{alt.name}</span>
                <div className="flex-1 rounded-full overflow-hidden" style={{ height: 4, background: "rgba(255,255,255,0.06)" }}>
                  <motion.div
                    className="h-full rounded-full opacity-60"
                    style={{ background: aColor }}
                    initial={{ width: "0%" }}
                    animate={{ width: `${Math.round(ac * 100)}%` }}
                    transition={{ duration: 1, delay: 0.3 + i * 0.1 }}
                  />
                </div>
                <span className="text-xs font-mono w-8 text-right shrink-0" style={{ color: "#475569" }}>
                  {Math.round(ac * 100)}%
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
