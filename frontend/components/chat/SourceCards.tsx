"use client";
import { motion } from "framer-motion";
import type { SourceDocument } from "@/lib/api";
import { ExternalLink } from "lucide-react";

export default function SourceCards({ sources }: { sources: SourceDocument[] }) {
  const unique = sources.filter((s, i, arr) =>
    arr.findIndex(x => x.source === s.source) === i
  );

  return (
    <div className="space-y-2">
      {unique.map((src, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.08 }}
          className="source-card group cursor-default"
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-farm-700 dark:text-farm-400 truncate">
                {src.title}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{src.source}</p>
              {src.excerpt && (
                <p className="text-xs text-gray-400 mt-1 line-clamp-2 leading-relaxed">
                  {src.excerpt}
                </p>
              )}
            </div>
            <div className="flex items-center gap-1 shrink-0">
              <div className="text-xs font-semibold text-farm-600 dark:text-farm-400 bg-farm-50 dark:bg-farm-950/50 px-1.5 py-0.5 rounded-full">
                {Math.round(src.relevance_score * 100)}%
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
