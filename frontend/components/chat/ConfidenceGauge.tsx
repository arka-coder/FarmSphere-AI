"use client";
import { motion } from "framer-motion";

interface Props {
  confidence: number;          // 0.0 - 1.0
  label?: string;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
  alternatives?: { name: string; confidence: number }[];
}

function getConfidenceColor(c: number) {
  if (c >= 0.75) return "confidence-bar-high";
  if (c >= 0.50) return "confidence-bar-medium";
  return "confidence-bar-low";
}

function getConfidenceBg(c: number) {
  if (c >= 0.75) return "text-farm-600 dark:text-farm-400 bg-farm-50 dark:bg-farm-950/50";
  if (c >= 0.50) return "text-harvest-600 dark:text-harvest-400 bg-harvest-50 dark:bg-harvest-900/30";
  return "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20";
}

export default function ConfidenceGauge({
  confidence,
  label,
  showLabel = true,
  size = "md",
  alternatives,
}: Props) {
  const pct = Math.round(confidence * 100);
  const colorClass = getConfidenceColor(confidence);
  const bgClass = getConfidenceBg(confidence);
  const barHeight = size === "sm" ? "h-1.5" : size === "lg" ? "h-3" : "h-2";
  const textSize = size === "sm" ? "text-lg" : size === "lg" ? "text-4xl" : "text-2xl";

  return (
    <div className="space-y-3">
      {/* Main gauge */}
      <div className={`rounded-xl p-3 ${bgClass} flex items-center gap-3`}>
        {/* Circular indicator */}
        <div className="relative w-12 h-12 shrink-0">
          <svg viewBox="0 0 36 36" className="w-12 h-12 -rotate-90">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="currentColor"
              strokeWidth="2.5" className="opacity-20" />
            <motion.circle
              cx="18" cy="18" r="15.9" fill="none" stroke="currentColor"
              strokeWidth="2.5" strokeLinecap="round"
              strokeDasharray="100"
              initial={{ strokeDashoffset: 100 }}
              animate={{ strokeDashoffset: 100 - pct }}
              transition={{ duration: 1.2, ease: [0.34, 1.56, 0.64, 1] }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-bold">{pct}%</span>
          </div>
        </div>

        {/* Text */}
        <div className="flex-1">
          {showLabel && label && (
            <p className="font-display font-bold text-sm leading-tight">{label}</p>
          )}
          <p className="text-xs font-medium mt-0.5 opacity-80">
            {pct >= 75 ? "High confidence — reliable diagnosis" :
             pct >= 50 ? "Medium confidence — additional images recommended" :
             "Low confidence — human expert review needed"}
          </p>
        </div>
      </div>

      {/* Bar */}
      <div>
        <div className={`confidence-bar-track ${barHeight}`}>
          <motion.div
            className={`confidence-bar-fill ${colorClass} ${barHeight}`}
            initial={{ width: "0%" }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 1.2, ease: [0.34, 1.56, 0.64, 1] }}
          />
        </div>
      </div>

      {/* Alternatives */}
      {alternatives && alternatives.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-semibold text-gray-500 dark:text-farm-400 uppercase tracking-wide">
            Alternative Possibilities
          </p>
          {alternatives.map((alt, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="text-xs text-gray-600 dark:text-gray-300 w-36 truncate">{alt.name}</span>
              <div className="flex-1 confidence-bar-track h-1.5">
                <motion.div
                  className="confidence-bar-fill h-1.5 opacity-50"
                  initial={{ width: "0%" }}
                  animate={{ width: `${Math.round(alt.confidence * 100)}%` }}
                  transition={{ duration: 1, delay: 0.3 + i * 0.1 }}
                />
              </div>
              <span className="text-xs text-gray-500 w-8 text-right">
                {Math.round(alt.confidence * 100)}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
