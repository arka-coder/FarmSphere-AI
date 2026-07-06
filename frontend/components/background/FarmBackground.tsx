"use client";

import { useRef, useEffect, useState, useMemo } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";


// ── Seeded deterministic pseudo-random (SSR-safe) ──────────────────────
const sr = (n: number) => Math.abs(Math.sin(n * 9301 + 49297) * 233280) % 1;

// ── Time phase ──────────────────────────────────────────────────────────
type Phase = "dawn" | "day" | "dusk" | "night";
const getPhase = (): Phase => {
  if (typeof window === "undefined") return "day";
  const h = new Date().getHours();
  if (h >= 5 && h < 7)  return "dawn";
  if (h >= 7 && h < 18) return "day";
  if (h >= 18 && h < 21) return "dusk";
  return "night";
};

// ── Sky configs ─────────────────────────────────────────────────────────
const SKY: Record<Phase, {
  gradient: string; sunBg: string; sunLeft: number; sunTop: number;
  sunSize: number; isNight: boolean; glowColor: string;
  landColor: string; farHillColor: string; nearHillColor: string;
}> = {
  dawn: {
    gradient:    "linear-gradient(180deg,#0d0220 0%,#5c1a82 13%,#a83040 33%,#e06028 54%,#f5b040 72%,#fde4a0 86%,#c5eca0 100%)",
    sunBg:       "radial-gradient(circle,#fff8d0 0%,#ffe060 35%,#ff8c00 65%,rgba(255,140,0,0) 100%)",
    sunLeft: 12, sunTop: 72, sunSize: 80, isNight: false,
    glowColor:   "rgba(255,160,40,0.28)",
    landColor:   "rgba(22,52,14,0.92)",
    farHillColor:"rgba(18,44,10,0.85)",
    nearHillColor:"rgba(14,36,8,0.96)",
  },
  day: {
    gradient:    "linear-gradient(180deg,#0a1c38 0%,#174080 13%,#2868b8 42%,#55aad5 67%,#a0d8f0 85%,#c2f0a8 100%)",
    sunBg:       "radial-gradient(circle,#ffffff 0%,#fffff5 30%,#ffff90 60%,rgba(255,255,128,0) 100%)",
    sunLeft: 62, sunTop: 14, sunSize: 68, isNight: false,
    glowColor:   "rgba(255,255,180,0.15)",
    landColor:   "rgba(24,68,16,0.85)",
    farHillColor:"rgba(20,58,12,0.75)",
    nearHillColor:"rgba(16,46,10,0.92)",
  },
  dusk: {
    gradient:    "linear-gradient(180deg,#0a0318 0%,#3a0c50 20%,#7a1848 42%,#c83a08 62%,#f09000 80%,#f8d050 93%,#f0e090 100%)",
    sunBg:       "radial-gradient(circle,#ffd0a0 0%,#ff8020 40%,#c83010 68%,rgba(200,48,16,0) 100%)",
    sunLeft: 85, sunTop: 66, sunSize: 90, isNight: false,
    glowColor:   "rgba(255,100,20,0.25)",
    landColor:   "rgba(16,36,8,0.95)",
    farHillColor:"rgba(12,30,6,0.88)",
    nearHillColor:"rgba(10,22,6,0.98)",
  },
  night: {
    gradient:    "linear-gradient(180deg,#010205 0%,#030810 30%,#040c18 60%,#061020 82%,#0a1628 100%)",
    sunBg:       "radial-gradient(circle,#e8ecf8 0%,#c5d0f0 40%,#a0b0e0 70%,rgba(160,176,224,0) 100%)",
    sunLeft: 75, sunTop: 12, sunSize: 42, isNight: true,
    glowColor:   "rgba(140,170,240,0.14)",
    landColor:   "rgba(10,22,6,0.97)",
    farHillColor:"rgba(8,18,4,0.92)",
    nearHillColor:"rgba(6,14,3,0.99)",
  },
};

// ── Cloud definitions ───────────────────────────────────────────────────
const CLOUDS = [
  { x:  4, y:  5, w: 230, h: 60, spd: 130, dly: -20,  op: 0.18, blur:  9, anim: "cloudDriftSlow" },
  { x: 48, y: 11, w: 170, h: 44, spd: 100, dly: -65,  op: 0.13, blur:  7, anim: "cloudDriftMed"  },
  { x: 82, y:  7, w: 195, h: 52, spd: 115, dly: -45,  op: 0.15, blur:  8, anim: "cloudDriftSlow" },
  { x: 22, y: 17, w: 140, h: 36, spd:  80, dly: -30,  op: 0.20, blur:  6, anim: "cloudDriftMed"  },
  { x: 63, y: 21, w: 122, h: 30, spd:  72, dly: -58,  op: 0.18, blur:  5, anim: "cloudDriftFast" },
  { x: 90, y: 14, w: 150, h: 38, spd:  85, dly: -12,  op: 0.16, blur:  6, anim: "cloudDriftMed"  },
  { x: 37, y: 26, w: 102, h: 26, spd:  58, dly: -48,  op: 0.22, blur:  4, anim: "cloudDriftFast" },
  { x: 72, y: 28, w:  92, h: 24, spd:  52, dly: -73,  op: 0.20, blur:  3, anim: "cloudDriftFast" },
];

// ── AI network nodes (expressed as % of 1440×900 viewport) ─────────────
const AI_NODES = [
  { x: 14,  y: 60, r: 5, color: "#3b82f6" },
  { x: 34,  y: 74, r: 4, color: "#8b5cf6" },
  { x: 52,  y: 58, r: 6, color: "#10b981" },
  { x: 70,  y: 70, r: 4, color: "#0ea5e9" },
  { x: 86,  y: 63, r: 5, color: "#6366f1" },
  { x: 24,  y: 85, r: 4, color: "#34d399" },
  { x: 60,  y: 84, r: 5, color: "#60a5fa" },
  { x: 44,  y: 91, r: 4, color: "#a78bfa" },
];

const CONNECTIONS = [
  [0,2],[2,4],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[1,5],[3,6],
];

// ── Sensor positions ────────────────────────────────────────────────────
const SENSORS = [
  { x: 19, y: 66, color: "#10b981", dly: 0.0  },
  { x: 41, y: 78, color: "#3b82f6", dly: 1.2  },
  { x: 62, y: 63, color: "#f59e0b", dly: 0.6  },
  { x: 77, y: 74, color: "#10b981", dly: 1.8  },
  { x: 29, y: 87, color: "#8b5cf6", dly: 0.3  },
  { x: 55, y: 89, color: "#3b82f6", dly: 2.1  },
  { x: 71, y: 82, color: "#10b981", dly: 0.9  },
];

// ── Leaves ──────────────────────────────────────────────────────────────
const LEAF_COLORS = ["#22c55e","#16a34a","#4ade80","#86efac","#15803d","#bbf7d0"];
const LEAVES = Array.from({ length: 16 }, (_, i) => ({
  id:  i,
  x:   sr(i * 7 + 1) * 100,
  sz:  sr(i * 7 + 2) * 10 + 7,
  dur: sr(i * 7 + 3) * 22 + 26,
  dly: -(sr(i * 7 + 4) * 35),
  col: LEAF_COLORS[Math.floor(sr(i * 7 + 5) * LEAF_COLORS.length)],
  ldx: (sr(i * 7 + 6) - 0.4) * 140,
  rot: Math.floor(sr(i * 7 + 7) * 900 + 360),
  op:  sr(i * 7 + 8) * 0.5 + 0.35,
}));

// ── Bird flocks ─────────────────────────────────────────────────────────
const BIRD_FLOCKS = [
  { y:  14, scale: 0.6, dly:   0, dur: 38, count: 5, spread: 18 },
  { y:  22, scale: 0.8, dly: -15, dur: 45, count: 4, spread: 14 },
  { y:  10, scale: 0.5, dly: -28, dur: 56, count: 6, spread: 22 },
];

// ── Helpers ─────────────────────────────────────────────────────────────
function BirdSvg({ scale }: { scale: number }) {
  return (
    <svg width={Math.round(14 * scale)} height={Math.round(7 * scale)} viewBox="0 0 14 7" fill="none">
      <path d="M0 3.5 C2 1.5 4 0.5 6 2.5 C8 0.5 10 1.5 12 3.5 C10 2.5 8 3.5 7 2.5 C6 3.5 4 2.5 2 3.5Z"
        fill="rgba(10,20,40,0.5)" />
    </svg>
  );
}

// ── Main Component ──────────────────────────────────────────────────────
export default function FarmBackground() {
  // Skip SSR entirely — this component is purely decorative (aria-hidden)
  // and uses seeded-random values that differ between server/client floats.
  const [mounted, setMounted] = useState(false);
  const [phase, setPhase] = useState<Phase>("day");

  // ── Mouse parallax via Framer Motion springs ─────────────────────────
  // All hooks must be declared unconditionally (before any early returns)
  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);
  const mx   = useSpring(rawX, { stiffness: 18, damping: 35 });
  const my   = useSpring(rawY, { stiffness: 18, damping: 35 });

  // Parallax transforms for each depth layer
  const cldX = useTransform(mx, [-1,1], [-18, 18]);
  const cldY = useTransform(my, [-1,1], [-8,  8 ]);
  const terX = useTransform(mx, [-1,1], [-10, 10]);
  const terY = useTransform(my, [-1,1], [-5,  5 ]);
  const fldX = useTransform(mx, [-1,1], [-6,  6 ]);
  const fldY = useTransform(my, [-1,1], [-3,  3 ]);
  const aiX  = useTransform(mx, [-1,1], [-5,  5 ]);
  const aiY  = useTransform(my, [-1,1], [-3,  3 ]);
  const grX  = useTransform(mx, [-1,1], [-3,  3 ]);
  const grY  = useTransform(my, [-1,1], [-2,  2 ]);

  // Stars — memoized for performance
  const STARS = useMemo(() => Array.from({ length: 90 }, (_, i) => ({
    id:   i,
    cx:   sr(i * 3 + 100) * 100,
    cy:   sr(i * 3 + 101) * 58,
    r:    sr(i * 3 + 102) * 1.5 + 0.4,
    smin: (sr(i * 3 + 103) * 0.25 + 0.1).toFixed(2),
    smax: (sr(i * 3 + 104) * 0.65 + 0.35).toFixed(2),
    dur:  sr(i * 3 + 105) * 4 + 2,
    dly:  sr(i * 3 + 106) * 7,
  })), []);

  // Crop rows
  const CROP_ROWS = useMemo(() => Array.from({ length: 16 }, (_, i) => {
    const t   = i / 15;
    const y   = 8 + t * 248;
    const spd = 16 + i * 1.2;
    const op  = 0.06 + t * 0.22;
    const sw  = 0.8 + t * 2.8;
    return { i, y, spd, op, sw, even: i % 2 === 0 };
  }), []);

  useEffect(() => {
    setMounted(true);
    setPhase(getPhase());
  }, []);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      rawX.set((e.clientX / window.innerWidth  - 0.5) * 2);
      rawY.set((e.clientY / window.innerHeight - 0.5) * 2);
    };
    window.addEventListener("mousemove", onMove, { passive: true });
    return () => window.removeEventListener("mousemove", onMove);
  }, [rawX, rawY]);

  const sky = SKY[phase];

  // Return an invisible placeholder during SSR / before hydration.
  // The div keeps layout space so there's no layout shift on mount.
  if (!mounted) {
    return <div className="farm-bg-root" aria-hidden="true" />;
  }

  return (
    <div className="farm-bg-root" aria-hidden="true">

      {/* ─────────────── 1. SKY ─────────────────────────────────────── */}
      <div className="absolute inset-0" style={{ background: sky.gradient }} />

      {/* ─────────────── 2. STARS (night) ───────────────────────────── */}
      {phase === "night" && (
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100"
          preserveAspectRatio="xMidYMid slice">
          {STARS.map(s => (
            <circle key={s.id}
              cx={`${s.cx}%`} cy={`${s.cy}%`}
              r="0.2"
              fill="white"
              style={{
                animation: `starTwinkle ${s.dur}s ease-in-out ${s.dly}s infinite`,
                "--smin": s.smin, "--smax": s.smax,
                r: `${s.r * 0.15}%`,
              } as React.CSSProperties}
            />
          ))}
        </svg>
      )}

      {/* ─────────────── 3. SUN / MOON ──────────────────────────────── */}
      <div className="absolute rounded-full"
        style={{
          left:      `${sky.sunLeft}%`,
          top:       `${sky.sunTop}%`,
          width:     sky.sunSize,
          height:    sky.sunSize,
          background: sky.sunBg,
          transform: "translate(-50%,-50%)",
          animation: sky.isNight
            ? "moonGlow 8s ease-in-out infinite"
            : "sunGlow 10s ease-in-out infinite",
          "--sg": sky.glowColor,
        } as React.CSSProperties}
      />

      {/* ─────────────── 4. SUN RAYS ────────────────────────────────── */}
      {!sky.isNight && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none"
          style={{ animation: "rayPulse 14s ease-in-out infinite" }}>
          {[0,22,44,66,88,110,132,154].map((angle, i) => (
            <div key={i}
              className="absolute"
              style={{
                left: `${sky.sunLeft}%`,
                top:  `${sky.sunTop}%`,
                width: 1,
                height: "90vh",
                background: `linear-gradient(180deg, ${sky.glowColor} 0%, transparent 100%)`,
                transformOrigin: "top center",
                transform: `translate(-50%, 0) rotate(${angle}deg)`,
              }}
            />
          ))}
        </div>
      )}

      {/* ─────────────── 5. CLOUDS ──────────────────────────────────── */}
      <motion.div className="absolute inset-0" style={{ x: cldX, y: cldY }}>
        {CLOUDS.map((c, i) => (
          <div key={i}
            className="absolute rounded-full"
            style={{
              left:     `${c.x}%`,
              top:      `${c.y}%`,
              width:    c.w,
              height:   c.h,
              background: phase === "night"
                ? `rgba(50,70,110,${c.op * 0.5})`
                : `rgba(255,255,255,${c.op})`,
              filter:   `blur(${c.blur}px)`,
              animation: `${c.anim} ${c.spd}s linear ${c.dly}s infinite`,
            }}
          />
        ))}
      </motion.div>

      {/* ─────────────── 6. HORIZON GLOW ────────────────────────────── */}
      <div className="absolute left-0 right-0"
        style={{
          bottom: "34%",
          height: 90,
          background: phase === "dawn"
            ? "radial-gradient(ellipse 90% 100% at 50% 100%, rgba(255,220,80,0.2) 0%, transparent 100%)"
            : phase === "dusk"
            ? "radial-gradient(ellipse 90% 100% at 50% 100%, rgba(240,120,40,0.22) 0%, transparent 100%)"
            : phase === "night"
            ? "radial-gradient(ellipse 90% 100% at 50% 100%, rgba(20,60,120,0.07) 0%, transparent 100%)"
            : "radial-gradient(ellipse 90% 100% at 50% 100%, rgba(180,240,140,0.14) 0%, transparent 100%)",
          animation: "horizonShimmer 20s ease-in-out infinite",
        }}
      />

      {/* ─────────────── 7. FAR TERRAIN ─────────────────────────────── */}
      <motion.div className="absolute left-0 right-0" style={{ bottom: "32%", x: terX, y: terY }}>
        <svg viewBox="0 0 1440 90" className="w-full" preserveAspectRatio="none" style={{ height: 90 }}>
          <defs>
            <linearGradient id="farHill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={sky.farHillColor} />
              <stop offset="100%" stopColor={sky.nearHillColor} />
            </linearGradient>
          </defs>
          {/* Distant hills silhouette */}
          <path
            d="M-10 90 L-10 52 C80 34 160 24 240 32 C320 40 400 28 480 22 C560 16 640 26 720 32 C800 38 880 28 960 22 C1040 16 1120 28 1200 36 C1280 44 1360 38 1450 30 L1450 90Z"
            fill="url(#farHill)"
          />
          {/* Second layer */}
          <path
            d="M-10 90 L-10 62 C120 50 240 42 360 48 C480 54 600 44 720 50 C840 56 960 46 1080 50 C1200 54 1320 48 1450 42 L1450 90Z"
            fill={sky.nearHillColor}
          />
        </svg>
      </motion.div>

      {/* ─────────────── 8. MIST LAYERS ─────────────────────────────── */}
      {[{ bt:"37%", h:50, op:0.25, dur:22, dly:0  },
        { bt:"40%", h:35, op:0.18, dur:28, dly:-6 },
        { bt:"43%", h:25, op:0.12, dur:34, dly:-12}].map((m,i) => (
        <div key={i}
          className="absolute left-0 right-0"
          style={{
            bottom: m.bt,
            height: m.h,
            background: phase === "dawn"
              ? `radial-gradient(ellipse 130% 100% at 50% 100%, rgba(255,230,180,${m.op}) 0%, transparent 100%)`
              : phase === "night"
              ? `radial-gradient(ellipse 130% 100% at 50% 100%, rgba(30,70,140,${m.op * 0.4}) 0%, transparent 100%)`
              : `radial-gradient(ellipse 130% 100% at 50% 100%, rgba(200,230,200,${m.op}) 0%, transparent 100%)`,
            "--mop": `${m.op}`,
            animation: `mistDrift ${m.dur}s ease-in-out ${m.dly}s infinite`,
          } as React.CSSProperties}
        />
      ))}

      {/* ─────────────── 9. FARMLAND BASE ───────────────────────────── */}
      <motion.div className="absolute left-0 right-0" style={{ top: "36%", bottom: 0, x: fldX }}>
        <div className="w-full h-full"
          style={{
            background: phase === "night"
              ? "linear-gradient(180deg,#0a1a06 0%,#0c2008 40%,#0e1a0a 100%)"
              : phase === "dawn"
              ? "linear-gradient(180deg,#1a3a10 0%,#2a5820 40%,#1e4014 100%)"
              : phase === "dusk"
              ? "linear-gradient(180deg,#162808 0%,#1e3c10 40%,#1a3010 100%)"
              : "linear-gradient(180deg,#1c4010 0%,#2e6018 40%,#245018 100%)",
          }}
        />
      </motion.div>

      {/* ─────────────── 10. PERSPECTIVE CROP ROWS ──────────────────── */}
      <motion.div className="absolute left-0 right-0" style={{ top:"40%", bottom:"14%", x:fldX, y:fldY }}>
        <svg viewBox="0 0 1440 260" className="w-full h-full" preserveAspectRatio="none">
          {CROP_ROWS.map(({ i, y, spd, op, sw, even }) => {
            const t = i / 15;
            const xOff = t * 120;
            const sc = phase === "night"
              ? `rgba(12,38,8,${op})`
              : `rgba(28,90,18,${op})`;
            return (
              <g key={i}
                className={even ? "crop-row-a" : "crop-row-b"}
                style={{ animationDelay: `${-i * 1.3}s`, animationDuration: `${spd}s` }}>
                <path
                  d={`M${-20+xOff} ${y} Q720 ${y + (even ? -4:4)} ${1460-xOff} ${y}`}
                  stroke={sc} strokeWidth={sw} fill="none" />
                <path
                  d={`M${-20+xOff} ${y+sw*0.8} Q720 ${y + (even ? -2:2) + sw*0.8} ${1460-xOff} ${y+sw*0.8}`}
                  stroke={sc} strokeWidth={sw * 0.5} strokeOpacity={0.4} fill="none" />
              </g>
            );
          })}
          {/* Vanishing perspective vertical furrows */}
          {Array.from({ length: 10 }, (_, i) => {
            const x1 = 720 + (i / 9 - 0.5) * 60;
            const x2 = 100 + (i / 9) * 1240;
            return (
              <line key={`v${i}`}
                x1={x1} y1={0}
                x2={x2} y2={260}
                stroke={phase === "night" ? "rgba(10,30,6,0.04)" : "rgba(22,75,12,0.05)"}
                strokeWidth={0.7}
              />
            );
          })}
        </svg>
      </motion.div>

      {/* ─────────────── 11. DIGITAL GRID OVERLAY ───────────────────── */}
      <div className="absolute left-0 right-0" style={{ top:"42%", bottom:0, animation:"gridPulse 22s ease-in-out infinite" }}>
        <svg width="100%" height="100%">
          <defs>
            <pattern id="farmgrid" width="80" height="55" patternUnits="userSpaceOnUse">
              <path d="M 80 0 L 0 0 0 55" fill="none"
                stroke="rgba(59,130,246,0.05)" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#farmgrid)" />
        </svg>
      </div>

      {/* ─────────────── 12. AI NETWORK (absolute % positioning) ────── */}
      <motion.div className="absolute inset-0" style={{ x: aiX, y: aiY }}>
        {/* Connection lines (absolute divs avoid SVG scaling issues) */}
        {CONNECTIONS.map(([a, b], ci) => {
          const na = AI_NODES[a];
          const nb = AI_NODES[b];
          // Use CSS lines via a thin div rotated between two points
          // Use window dimensions — safe here because mounted guard ensures client-only.
          const dx = (nb.x - na.x) * (window.innerWidth  / 100);
          const dy = (nb.y - na.y) * (window.innerHeight / 100);
          const len   = Math.hypot(dx, dy);
          const angle = Math.atan2(dy, dx) * (180 / Math.PI);
          return (
            <div key={`c-${ci}`}
              className="absolute"
              style={{
                left:  `${na.x}%`,
                top:   `${na.y}%`,
                width: `${Math.hypot(nb.x - na.x, nb.y - na.y) * 1.42}%`,
                height: 1,
                background: `linear-gradient(90deg, ${na.color}55, ${nb.color}55)`,
                transform: `rotate(${Math.atan2(nb.y - na.y, (nb.x - na.x) * 1.78) * 180 / Math.PI}deg)`,
                transformOrigin: "left center",
                opacity: 0.35,
              }}
            />
          );
        })}

        {/* AI Nodes */}
        {AI_NODES.map((n, i) => (
          <div key={`n-${i}`}
            className="absolute"
            style={{ left: `${n.x}%`, top: `${n.y}%`, transform: "translate(-50%,-50%)" }}>
            {/* Outer glow ring */}
            <div className="absolute rounded-full"
              style={{
                width: n.r * 6, height: n.r * 6,
                background: `radial-gradient(circle, ${n.color}20 0%, transparent 70%)`,
                top: "50%", left: "50%",
                transform: "translate(-50%,-50%)",
              }}
            />
            {/* Middle ring */}
            <div className="absolute rounded-full"
              style={{
                width: n.r * 3.5, height: n.r * 3.5,
                border: `1px solid ${n.color}60`,
                top: "50%", left: "50%",
                transform: "translate(-50%,-50%)",
              }}
            />
            {/* Core dot */}
            <div className="rounded-full"
              style={{
                width: n.r * 1.8, height: n.r * 1.8,
                background: n.color,
                boxShadow: `0 0 ${n.r * 3}px ${n.r}px ${n.color}80`,
              }}
            />
          </div>
        ))}

        {/* Data packet flow — animated thin lines */}
        {CONNECTIONS.map(([a, b], ci) => {
          const na = AI_NODES[a];
          const nb = AI_NODES[b];
          return (
            <div key={`dp-${ci}`}
              className="absolute"
              style={{
                left:   `${na.x}%`,
                top:    `${na.y}%`,
                width:  `${Math.hypot(nb.x - na.x, nb.y - na.y) * 1.42}%`,
                height: 2,
                background: na.color,
                transform: `rotate(${Math.atan2(nb.y - na.y, (nb.x - na.x) * 1.78) * 180 / Math.PI}deg)`,
                transformOrigin: "left center",
                animation: `dataPacketFlow ${11 + ci * 1.7}s linear ${-ci * 2.3}s infinite`,
              }}
            />
          );
        })}
      </motion.div>

      {/* ─────────────── 13. SENSOR INDICATORS ──────────────────────── */}
      <div className="absolute inset-0">
        {SENSORS.map((s, i) => (
          <div key={i}
            className="absolute"
            style={{ left: `${s.x}%`, top: `${s.y}%`, transform: "translate(-50%,-50%)" }}>
            {/* Outer expanding ring */}
            <div className="absolute rounded-full"
              style={{
                width: 14, height: 14,
                background: s.color,
                top: "50%", left: "50%",
                transform: "translate(-50%,-50%)",
                animation: `sensorPingOuter 3.2s ease-out ${s.dly}s infinite`,
              }}
            />
            {/* Inner ring */}
            <div className="absolute rounded-full"
              style={{
                width: 9, height: 9,
                background: s.color,
                top: "50%", left: "50%",
                transform: "translate(-50%,-50%)",
                animation: `sensorPing 3.2s ease-out ${s.dly + 0.2}s infinite`,
              }}
            />
            {/* Core */}
            <div className="absolute rounded-full"
              style={{
                width: 4, height: 4,
                background: s.color,
                top: "50%", left: "50%",
                transform: "translate(-50%,-50%)",
                boxShadow: `0 0 8px 2px ${s.color}90`,
              }}
            />
          </div>
        ))}
      </div>

      {/* ─────────────── 14. GRASS (foreground) ─────────────────────── */}
      <motion.div className="absolute left-0 right-0 bottom-0" style={{ height:"17%", x: grX, y: grY }}>
        <svg viewBox="0 0 1440 120" className="w-full h-full" preserveAspectRatio="none">
          {Array.from({ length: 75 }, (_, i) => {
            const x    = (i / 74) * 1440 + (sr(i * 4) - 0.5) * 18;
            const h    = sr(i * 4 + 1) * 55 + 32;
            const lean = (sr(i * 4 + 2) - 0.5) * 22;
            const tx   = x + lean;
            const cls  = i % 2 === 0 ? "grass-blade-l" : "grass-blade-r";
            const d    = `M${x} 120 C${x + lean*0.3} ${120-h*0.38} ${tx-1.2} ${120-h*0.72} ${tx} ${120-h}`;
            const green = 60 + Math.floor(sr(i * 4 + 3) * 55);
            const col  = phase === "night"
              ? `rgba(8,${20+Math.floor(sr(i*4+3)*18)},6,0.75)`
              : `rgba(16,${green},10,0.72)`;
            return (
              <path key={i} d={d}
                stroke={col}
                strokeWidth={1.0 + sr(i) * 1.4}
                fill="none"
                className={cls}
                style={{
                  animationDelay:    `${-sr(i*4+4) * 7}s`,
                  animationDuration: `${5 + sr(i*4+5) * 4}s`,
                }}
              />
            );
          })}
          {/* Ground fill strip */}
          <path d="M0 106 Q360 100 720 102 Q1080 100 1440 106 L1440 120 L0 120Z"
            fill={phase === "night" ? "rgba(6,12,4,0.98)" : "rgba(14,32,8,0.96)"} />
        </svg>
      </motion.div>

      {/* ─────────────── 15. DRIFTING LEAVES ────────────────────────── */}
      {LEAVES.map(l => (
        <div key={l.id}
          className="absolute"
          style={{
            left: `${l.x}%`,
            top:  "-3%",
            "--ldx":  `${l.ldx}px`,
            "--lrot": `${l.rot}deg`,
            animation: `leafDrift ${l.dur}s ease-in-out ${l.dly}s infinite`,
            opacity: l.op,
          } as React.CSSProperties}
        >
          <svg width={l.sz} height={l.sz} viewBox="0 0 12 12" fill="none">
            <ellipse cx="6" cy="4" rx="5" ry="3" fill={l.col} fillOpacity="0.85"
              transform="rotate(-20 6 4)" />
            <line x1="6" y1="7" x2="6" y2="1"
              stroke={l.col} strokeWidth="0.5" strokeOpacity="0.5" />
          </svg>
        </div>
      ))}

      {/* ─────────────── 16. BIRD FLOCKS ────────────────────────────── */}
      {BIRD_FLOCKS.map((flock, fi) =>
        Array.from({ length: flock.count }, (_, bi) => (
          <div key={`${fi}-${bi}`}
            className="absolute"
            style={{
              top:       `${flock.y}%`,
              left:      0,
              transform: `translateY(${(sr(fi*10+bi) - 0.5) * flock.spread}px)`,
              animation: `birdFly ${flock.dur + sr(fi*10+bi+3)*8}s ease-in-out ${flock.dly + bi*1.5}s infinite`,
            }}>
            <BirdSvg scale={flock.scale * (0.8 + sr(fi*5+bi) * 0.4)} />
          </div>
        ))
      )}

      {/* ─────────────── 17. DARK OVERLAY (readability) ─────────────── */}
      <div className="absolute inset-0"
        style={{
          background: `
            radial-gradient(ellipse 80% 60% at 50% 40%, transparent 20%, rgba(0,0,0,0.38) 100%),
            linear-gradient(180deg, rgba(0,0,0,0.48) 0%, rgba(0,0,0,0.08) 38%, rgba(0,0,0,0.22) 100%)
          `,
        }}
      />
    </div>
  );
}
