"use client";
import { ExternalLink } from "lucide-react";

interface Source {
  title: string;
  source: string;
  relevance?: number;
}

interface Props {
  sources: Source[];
}

export default function SourceCards({ sources }: Props) {
  return (
    <div className="space-y-2">
      {sources.map((s, i) => (
        <div key={i} className="source-card group flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold leading-tight truncate" style={{ color: "#e2e8f0" }}>
              {s.title}
            </p>
            <p className="text-xs mt-0.5 truncate" style={{ color: "#475569" }}>{s.source}</p>
          </div>
          {s.relevance !== undefined && (
            <span className="text-xs font-mono shrink-0 px-1.5 py-0.5 rounded-md"
              style={{ background: "rgba(59,130,246,0.1)", color: "#60a5fa", border: "1px solid rgba(59,130,246,0.2)" }}>
              {Math.round(s.relevance * 100)}%
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
