"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AnimatePresence,
  motion,
  useReducedMotion,
} from "framer-motion";
import {
  ArrowRight,
  Bot,
  BrainCircuit,
  CalendarDays,
  CheckCircle2,
  CloudSun,
  Database,
  FileText,
  Github,
  Microscope,
  PlayCircle,
  Satellite,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  Zap,
  Linkedin,
  Instagram,
} from "lucide-react";

const navItems = [
  { label: "Platform", href: "#platform" },
  { label: "AI Workflow", href: "#ai-workflow" },
  { label: "Technology", href: "#technology" },
  { label: "Launch App", href: "#launch" },
];

const thinkingSteps = [
  {
    label: "Farmer uploads crop image",
    icon: UploadCloud,
    purpose: "Begins the diagnosis with field context.",
    input: "Crop photo, location, crop type",
    output: "Structured case file",
    role: "Creates the shared field case for every downstream agent.",
  },
  {
    label: "Gemini Vision analyzes image",
    icon: BrainCircuit,
    purpose: "Reads visual symptoms and converts pixels into evidence.",
    input: "Image and crop metadata",
    output: "Detected lesions, stress signs, confidence",
    role: "Turns raw imagery into machine-readable agronomic evidence.",
  },
  {
    label: "Disease Detection Agent",
    icon: Microscope,
    purpose: "Matches visual evidence against likely crop diseases.",
    input: "Vision evidence",
    output: "Candidate diagnoses",
    role: "Narrows symptoms into probable disease paths.",
  },
  {
    label: "Weather Agent",
    icon: CloudSun,
    purpose: "Checks whether local conditions increase spread risk.",
    input: "Forecast, humidity, rainfall, temperature",
    output: "Weather-linked disease risk",
    role: "Adds environmental context a chatbot would usually miss.",
  },
  {
    label: "Knowledge Agent",
    icon: Database,
    purpose: "Retrieves verified agronomy guidance and treatment context.",
    input: "Disease candidates and crop stage",
    output: "Ranked sources and treatment notes",
    role: "Grounds recommendations in retrieved agricultural knowledge.",
  },
  {
    label: "Seasonal Intelligence Agent",
    icon: CalendarDays,
    purpose: "Aligns recommendations with the crop calendar.",
    input: "Crop stage, planting date, season",
    output: "Timing-aware intervention plan",
    role: "Prevents advice from ignoring seasonal timing.",
  },
  {
    label: "Risk Assessment Agent",
    icon: ShieldCheck,
    purpose: "Scores urgency, uncertainty, and potential field impact.",
    input: "Disease, weather, season, evidence strength",
    output: "Risk score and escalation level",
    role: "Separates urgent action from low-confidence noise.",
  },
  {
    label: "Recommendation Agent",
    icon: Bot,
    purpose: "Turns agent findings into a practical next action.",
    input: "All agent outputs",
    output: "Farmer-ready action plan",
    role: "Synthesizes expert signals into a single decision.",
  },
  {
    label: "Explainability Agent",
    icon: FileText,
    purpose: "Makes the reasoning transparent and auditable.",
    input: "Agent traces and source evidence",
    output: "Why this answer, confidence, sources",
    role: "Shows the farmer how FarmSphere reached its answer.",
  },
  {
    label: "Final Recommendation",
    icon: CheckCircle2,
    purpose: "Delivers the decision in clear language.",
    input: "Reasoned recommendation package",
    output: "Diagnosis, action, risk, explanation",
    role: "Returns the complete, explainable field response.",
  },
];

const technology = [
  { name: "Gemini 2.5 Flash", what: "Low-latency reasoning model", why: "Used for fast agent decisions.", how: "Coordinates synthesis, planning, and final response tone." },
  { name: "Gemini Vision", what: "Multimodal image intelligence", why: "Used to inspect crop symptoms.", how: "Extracts visible disease evidence from uploaded images." },
  { name: "LangGraph", what: "Agent workflow runtime", why: "Used for controlled reasoning paths.", how: "Routes state between specialist agricultural agents." },
  { name: "ChromaDB", what: "Vector knowledge memory", why: "Used for retrieval grounding.", how: "Finds relevant agronomy documents and treatment context." },
  { name: "Google Earth Engine", what: "Geospatial intelligence platform", why: "Used for satellite signals.", how: "Adds NDVI and vegetation health to field decisions." },
  { name: "FastAPI", what: "Python API framework", why: "Used for reliable agent services.", how: "Serves orchestration, analysis, and data endpoints." },
  { name: "Next.js", what: "React application framework", why: "Used for the product surface.", how: "Delivers routing, rendering, and app-level performance." },
  { name: "Tailwind CSS", what: "Utility design system", why: "Used for precise UI craft.", how: "Keeps spacing, typography, and responsive polish consistent." },
  { name: "PostgreSQL", what: "Relational data layer", why: "Used for durable farm context.", how: "Stores user, field, crop, and workflow data." },
  { name: "Docker", what: "Container runtime", why: "Used for portable deployment.", how: "Packages services consistently across environments." },
];

function FarmLogo({
  dark = false,
  compact = false,
}: {
  dark?: boolean;
  compact?: boolean;
}) {
  return (
    <div className="flex items-center">
      {!compact && (
        <span
          className={`font-display text-2xl font-semibold tracking-[-0.02em] md:text-[1.7rem] ${dark ? "text-slate-950" : "text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]"
            }`}
        >
          FarmSphere AI
        </span>
      )}
    </div>
  );
}

function PremiumButton({
  href,
  children,
  variant = "light",
  icon = true,
}: {
  href: string;
  children: React.ReactNode;
  variant?: "light" | "dark" | "ghost";
  icon?: boolean;
}) {
  const classes = {
    light:
      "border border-white/70 bg-[linear-gradient(135deg,#ffffff,#eefbf4)] text-emerald-950 shadow-[0_24px_80px_rgba(255,255,255,0.22),inset_0_1px_0_rgba(255,255,255,0.95)] hover:bg-emerald-50 hover:text-emerald-950 hover:shadow-[0_30px_100px_rgba(255,255,255,0.30),0_10px_34px_rgba(14,79,54,0.16),inset_0_1px_0_rgba(255,255,255,1)] active:translate-y-0 active:scale-[0.985]",
    dark:
      "border border-emerald-950 bg-[#0E4F36] text-white shadow-[0_18px_55px_rgba(14,79,54,0.24)] hover:bg-[#123f30] hover:text-white hover:shadow-[0_26px_70px_rgba(14,79,54,0.30)] active:translate-y-0 active:scale-[0.985]",
    ghost:
      "border border-white/40 bg-white/[0.09] text-white shadow-[0_18px_55px_rgba(0,0,0,0.18),inset_0_1px_0_rgba(255,255,255,0.12)] backdrop-blur-xl hover:border-emerald-100/70 hover:bg-white/[0.15] hover:text-white hover:shadow-[0_24px_70px_rgba(0,0,0,0.22),inset_0_1px_0_rgba(255,255,255,0.18)] active:translate-y-0 active:scale-[0.985]",
  };

  return (
    <Link
      href={href}
      className={`group inline-flex min-h-12 items-center justify-center gap-2 rounded-full px-6 py-3.5 text-base font-semibold transition duration-300 ease-out hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-emerald-300 focus:ring-offset-2 focus:ring-offset-transparent ${classes[variant]}`}
    >
      <span className="inline-flex items-center gap-2 leading-none text-current">
        {children}
      </span>
      {icon && <ArrowRight className="h-5 w-5 shrink-0 text-current transition group-hover:translate-x-0.5" />}
    </Link>
  );
}



function PlatformSection() {
  return (
    <section id="platform" className="relative overflow-hidden bg-[#f7f5ef] px-6 py-24 md:py-32">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_18%,rgba(14,79,54,0.10),transparent_30%),radial-gradient(circle_at_10%_80%,rgba(245,185,78,0.14),transparent_28%)]" />
      <div className="relative mx-auto grid max-w-6xl gap-14 lg:grid-cols-[0.86fr_1.14fr] lg:items-center">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-15%" }}
          transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-800/60">
            Platform
          </p>
          <h2 className="mt-5 text-balance text-4xl font-semibold leading-[1.02] tracking-tight text-slate-950 md:text-6xl">
            The Future of Agricultural Intelligence
          </h2>
          <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-600">
            FarmSphere AI is an explainable multi-agent agricultural intelligence platform that
            combines computer vision, satellite intelligence, weather forecasting, market analysis,
            and AI reasoning into a single intelligent companion for farmers.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 36, scale: 0.96 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true, margin: "-15%" }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          className="relative overflow-hidden rounded-[2rem] border border-emerald-950/[0.10] bg-slate-950 p-3 shadow-[0_36px_120px_rgba(14,79,54,0.22)] md:p-5"
        >
          <div className="rounded-[1.55rem] bg-[#fbfcf8] p-5 md:p-6">
            <div className="flex items-center justify-between border-b border-slate-200 pb-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#0E4F36] text-white">
                  <BrainCircuit className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-800/50">
                    FarmSphere OS
                  </p>
                  <p className="font-semibold tracking-tight text-slate-950">Field intelligence console</p>
                </div>
              </div>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-900">
                <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-emerald-600 align-middle shadow-[0_0_14px_rgba(5,150,105,0.85)]" />
                Live
              </span>
            </div>
            <div className="grid gap-5 pt-5 lg:grid-cols-[1.12fr_0.88fr]">
              <div className="min-h-[350px] overflow-hidden rounded-[1.35rem] bg-[linear-gradient(145deg,#0e4f36,#173d31_48%,#d8efe4)] p-5 text-white">
                <div className="flex items-center justify-between">
                  <span className="rounded-full bg-white/[0.14] px-3 py-1 text-xs font-semibold">
                    Field A-17
                  </span>
                  <Satellite className="h-5 w-5 text-emerald-100" />
                </div>
                <div className="mt-16 grid gap-4 sm:grid-cols-3">
                  {[72, 88, 54].map((height, index) => (
                    <div key={height} className="flex h-40 items-end rounded-2xl bg-white/[0.10] p-3">
                      <motion.div
                        initial={{ height: "18%" }}
                        whileInView={{ height: [`18%`, `${height}%`, `${height - 8}%`, `${height}%`] }}
                        viewport={{ once: true }}
                        transition={{ delay: index * 0.12, duration: 1.8, ease: [0.16, 1, 0.3, 1] }}
                        className="w-full rounded-xl bg-gradient-to-t from-emerald-200 to-amber-100"
                      />
                    </div>
                  ))}
                </div>
                <motion.div
                  initial={{ opacity: 0, x: 18, y: 10 }}
                  whileInView={{ opacity: 1, x: 0, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.55, duration: 0.65, ease: [0.16, 1, 0.3, 1] }}
                  className="mt-6 rounded-2xl border border-white/[0.12] bg-white/[0.12] p-3 text-sm leading-6 text-white/82 backdrop-blur-md"
                >
                  AI reasoning: moisture stress low, fungal risk rising before rainfall.
                </motion.div>
                <p className="mt-10 max-w-lg text-sm leading-7 text-white/[0.72]">
                  Satellite health, disease risk, weather windows, and market signals converge into
                  one explainable decision surface.
                </p>
              </div>
              <div className="space-y-3">
                {[
                  ["Crop health", "Stable", "text-emerald-800"],
                  ["Risk index", "Moderate", "text-amber-700"],
                  ["Next action", "Inspect leaves", "text-slate-950"],
                  ["Sources", "5 verified", "text-emerald-800"],
                ].map(([label, value, color]) => (
                  <motion.div
                    key={label}
                    whileHover={{ y: -3 }}
                    transition={{ type: "spring", stiffness: 260, damping: 22 }}
                    className="rounded-2xl border border-emerald-950/[0.08] bg-white p-4 shadow-[0_14px_40px_rgba(14,79,54,0.06)]"
                  >
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-800/45">
                      {label}
                    </p>
                    <p className={`mt-1 text-lg font-semibold ${color}`}>{value}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function AIWorkflowSection() {
  const [active, setActive] = useState(0);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    if (reduceMotion) return;

    const timer = window.setInterval(() => {
      setActive((step) => (step + 1) % thinkingSteps.length);
    }, 1350);
    return () => window.clearInterval(timer);
  }, [reduceMotion]);

  const activeStep = thinkingSteps[active];
  const ActiveIcon = activeStep.icon;

  return (
    <section id="ai-workflow" className="relative overflow-hidden bg-[#061911] px-6 py-24 text-white md:py-32">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(16,185,129,0.18),transparent_34%),radial-gradient(circle_at_82%_74%,rgba(245,185,78,0.10),transparent_30%)]" />
      <div className="relative mx-auto max-w-6xl">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-200/60">
            AI Workflow
          </p>
          <h2 className="mt-5 text-balance text-4xl font-semibold leading-[1.02] tracking-tight md:text-6xl">
            The reasoning process, made visible.
          </h2>
          <p className="mt-6 text-lg leading-8 text-white/[0.66]">
            FarmSphere AI does not hide behind a single answer. It routes every field signal through
            specialist agents, then returns a recommendation with evidence, confidence, and traceable logic.
          </p>
        </div>

        <div className="mt-16 grid gap-8 lg:grid-cols-[0.76fr_1.24fr]">
          <motion.div
            layout
            className="rounded-[2rem] border border-white/[0.12] bg-white/[0.08] p-5 shadow-[0_32px_120px_rgba(0,0,0,0.28)] backdrop-blur-2xl lg:sticky lg:top-28 lg:self-start"
          >
            <div className="rounded-[1.45rem] bg-black/18 p-5">
              <div className="flex items-center gap-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-300/14 text-emerald-100">
                  <ActiveIcon className="h-7 w-7" />
                </div>
                <div>
                  <p className="text-sm text-white/[0.54]">Currently executing</p>
                  <AnimatePresence mode="wait">
                    <motion.p
                      key={activeStep.label}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className="text-xl font-semibold tracking-tight"
                    >
                      {activeStep.label}
                    </motion.p>
                  </AnimatePresence>
                </div>
              </div>
              <p className="mt-8 min-h-16 text-lg leading-8 text-white/[0.68]">{activeStep.purpose}</p>
              <div className="mt-7 grid gap-3">
                {[
                  ["Input", activeStep.input],
                  ["Output", activeStep.output],
                  ["Trace", `${active + 1} / ${thinkingSteps.length}`],
                  ["Role", activeStep.role],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between rounded-2xl border border-white/[0.10] bg-white/[0.08] px-4 py-3">
                    <span className="text-sm text-white/[0.58]">{label}</span>
                    <span className="max-w-[62%] text-right text-sm font-semibold">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          <div className="relative">
            <div className="absolute left-6 top-8 hidden h-[calc(100%-4rem)] w-px overflow-hidden bg-gradient-to-b from-emerald-200/0 via-emerald-200/35 to-emerald-200/0 md:block">
              {!reduceMotion && (
                <motion.span
                  className="absolute left-0 top-0 h-16 w-px rounded-full bg-gradient-to-b from-transparent via-emerald-100 to-transparent shadow-[0_0_22px_rgba(167,243,208,0.95)]"
                  animate={{ y: ["-20%", "720%"] }}
                  transition={{ duration: 3.4, repeat: Infinity, ease: "linear" }}
                />
              )}
            </div>
            <div className="space-y-4">
              {thinkingSteps.map((step, index) => {
                const Icon = step.icon;
                const isActive = active === index;

                return (
                  <motion.button
                    key={step.label}
                    type="button"
                    initial={{ opacity: 0, x: 18 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, margin: "-10%" }}
                    transition={{ delay: index * 0.045, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    onMouseEnter={() => setActive(index)}
                    onFocus={() => setActive(index)}
                    className={`group relative flex w-full items-start gap-4 rounded-2xl border p-4 text-left transition duration-300 hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-emerald-300 ${isActive
                        ? "border-emerald-200/40 bg-emerald-200/[0.13] shadow-[0_18px_50px_rgba(16,185,129,0.16)]"
                        : "border-white/[0.09] bg-white/[0.055] hover:bg-white/[0.09]"
                      }`}
                  >
                    <span
                      className={`absolute -left-[1.15rem] top-8 hidden h-2.5 w-2.5 rounded-full transition md:block ${isActive
                          ? "bg-emerald-200 shadow-[0_0_24px_rgba(167,243,208,0.95)]"
                          : "bg-emerald-200/35"
                        }`}
                    />
                    <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${isActive ? "bg-emerald-200 text-emerald-950" : "bg-white/[0.10] text-emerald-200"}`}>
                      <Icon className="h-5 w-5" />
                    </span>
                    <span>
                      <span className="block font-semibold text-white">{step.label}</span>
                      <span className="mt-1 block text-sm leading-6 text-white/[0.56]">{step.purpose}</span>
                      <span className={`mt-3 grid gap-2 text-xs leading-5 transition md:grid-cols-2 ${isActive ? "opacity-100" : "opacity-0 group-hover:opacity-100 group-focus:opacity-100"}`}>
                        <span className="rounded-xl bg-white/[0.07] px-3 py-2 text-white/[0.62]">
                          Input: <span className="text-white/[0.86]">{step.input}</span>
                        </span>
                        <span className="rounded-xl bg-white/[0.07] px-3 py-2 text-white/[0.62]">
                          Output: <span className="text-white/[0.86]">{step.output}</span>
                        </span>
                        <span className="rounded-xl bg-white/[0.07] px-3 py-2 text-white/[0.62] md:col-span-2">
                          Role: <span className="text-white/[0.86]">{step.role}</span>
                        </span>
                      </span>
                    </span>
                  </motion.button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function TechnologySection() {
  return (
    <section id="technology" className="relative z-10 overflow-hidden bg-[#f7f5ef] px-6 py-24 md:py-32">
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-800/60">
            Technology
          </p>
          <h2 className="mt-5 text-balance text-4xl font-semibold leading-[1.02] tracking-tight text-slate-950 md:text-6xl">
            A modern AI stack for field-grade reasoning.
          </h2>
          <p className="mt-6 text-lg leading-8 text-slate-600">
            Each layer has a clear job: perception, orchestration, retrieval, intelligence, interface,
            and deployment.
          </p>
        </div>

        <div className="mt-16">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            {technology.map((tool, index) => (
              <motion.div
                key={tool.name}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.04, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                whileHover={{ y: -6, scale: 1.01 }}
                className="group relative min-h-[250px] overflow-hidden rounded-[1.35rem] border border-slate-950/[0.08] bg-white/76 p-5 text-slate-950 shadow-[0_18px_60px_rgba(14,79,54,0.06)] backdrop-blur-xl transition-colors duration-300 hover:border-emerald-950/20 hover:bg-white hover:shadow-[0_26px_80px_rgba(14,79,54,0.12)]"
              >
                <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-700/30 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  {String(index + 1).padStart(2, "0")}
                </p>
                <p className="mt-4 text-lg font-semibold tracking-tight">{tool.name}</p>
                <p className="mt-3 text-sm font-medium leading-6 text-slate-700">{tool.what}</p>
                <div className="mt-5 space-y-3 text-sm leading-6 text-slate-600">
                  <p><span className="font-semibold text-emerald-800">Why:</span> {tool.why}</p>
                  <p><span className="font-semibold text-emerald-800">How:</span> {tool.how}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export default function HomePage() {
  const [activeSection, setActiveSection] = useState("hero");
  const navOnLightSection = activeSection === "platform" || activeSection === "technology";

  useEffect(() => {
    const sections = [{ href: "#hero" }, ...navItems]
      .map((item) => document.querySelector(item.href))
      .filter((section): section is Element => Boolean(section));

    let frame = 0;

    const updateActiveSection = () => {
      const marker = window.innerHeight * 0.34;
      const current =
        sections.find((section) => {
          const rect = section.getBoundingClientRect();
          return rect.top <= marker && rect.bottom > marker;
        }) ?? sections[0];

      if (current?.id) {
        setActiveSection(current.id);
      }
    };

    const onScroll = () => {
      window.cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(updateActiveSection);
    };

    updateActiveSection();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);

    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <main className="min-h-screen overflow-x-hidden bg-[#f7f5ef] text-slate-950">
      <section id="hero" className="relative min-h-screen overflow-hidden bg-[#10130f] text-white">
        <motion.video
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          initial={{ opacity: 1, scale: 1.01 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.1, ease: "easeOut" }}
          className="absolute inset-0 h-full w-full object-cover will-change-transform"
        >
          <source src="/hero-bg.mp4" type="video/mp4" />
        </motion.video>
        <div className="absolute inset-0 bg-gradient-to-b from-[#052015]/68 via-[#0E4F36]/48 to-[#06120d]/82" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_30%,rgba(0,0,0,0.62)_100%)]" />
        <div className="absolute inset-0 bg-black/[0.10] mix-blend-multiply" />
        <div className="absolute inset-x-0 bottom-0 h-52 bg-gradient-to-t from-[#f7f5ef] to-transparent" />

        <motion.nav
          initial={{ y: -34, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.15, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className={`fixed inset-x-0 top-6 z-50 flex w-full items-center justify-between px-7 py-3 transition-colors duration-500 sm:px-10 lg:px-16 ${navOnLightSection ? "text-slate-950" : "text-white"
            }`}
        >
          <Link href="/" aria-label="FarmSphere AI home">
            <FarmLogo dark={navOnLightSection} />
          </Link>
          <div className="hidden items-center gap-10 text-[15px] font-semibold tracking-[-0.01em] md:flex lg:gap-14">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className={`group relative py-1.5 transition duration-300 hover:-translate-y-0.5 ${activeSection === item.href.slice(1)
                    ? navOnLightSection
                      ? "text-emerald-800"
                      : "text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.55)]"
                    : navOnLightSection
                      ? "text-slate-700 hover:text-emerald-800"
                      : "text-white/86 [text-shadow:0_1px_18px_rgba(0,0,0,0.55)] hover:text-white"
                  }`}
              >
                {item.label}
                <span className={`absolute bottom-0 left-0 h-px w-0 transition-all duration-300 group-hover:w-full group-focus-visible:w-full ${navOnLightSection ? "bg-emerald-700" : "bg-emerald-200"}`} />
                {activeSection === item.href.slice(1) && (
                  <motion.span
                    layoutId="nav-active-underline"
                    className={`absolute bottom-0 left-0 h-px w-full ${navOnLightSection ? "bg-emerald-700" : "bg-emerald-200"}`}
                    transition={{ type: "spring", stiffness: 280, damping: 30, mass: 0.7 }}
                  />
                )}
              </a>
            ))}
          </div>
        </motion.nav>

        <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-7xl flex-col items-center justify-center px-6 pb-24 pt-36 text-center">
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.42, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="mb-8"
          >
            <FarmLogo />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.58, duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
            className="mb-8 inline-flex items-center gap-2 rounded-full border border-emerald-200/[0.22] bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-emerald-100 shadow-[0_18px_60px_rgba(0,0,0,0.18)] backdrop-blur-xl"
          >
            <Sparkles className="h-4 w-4 text-amber-200" />
            Powered by Gemini AI
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.72, duration: 0.95, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-6xl text-balance text-6xl font-semibold leading-[0.88] tracking-[-0.035em] text-white [text-shadow:0_18px_80px_rgba(0,0,0,0.42)] sm:text-7xl md:text-8xl lg:text-[7.8rem]"
          >
            Where AI Meets Every Harvest
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
            className="mt-9 max-w-3xl text-pretty text-base leading-8 text-white/[0.78] sm:text-lg md:text-xl"
          >
            An explainable multi-agent agricultural intelligence platform combining computer
            vision, satellite intelligence, weather forecasting, market insights, and autonomous AI
            agents to help farmers make smarter decisions.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.08, duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
            className="mt-12 flex w-full flex-col items-center justify-center gap-3 sm:w-auto sm:flex-row"
          >
            <PremiumButton href="/dashboard" variant="light">Launch FarmSphere AI</PremiumButton>
            <PremiumButton href="#ai-workflow" variant="ghost" icon={false}>
              <PlayCircle className="h-5 w-5" />
              Watch Demo
            </PremiumButton>
          </motion.div>

        </div>
      </section>

      <PlatformSection />
      <AIWorkflowSection />
      <TechnologySection />

      <section id="launch" className="relative overflow-hidden bg-[#071b13] px-6 py-28 text-white md:py-36">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(16,185,129,0.18),transparent_36%)]" />
        <div className="relative mx-auto flex max-w-5xl flex-col items-center text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-200/60">
            Launch App
          </p>
          <h2 className="mt-5 text-balance text-4xl font-semibold leading-[1.02] tracking-tight md:text-6xl">
            Ready to experience AI-powered agriculture?
          </h2>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-white/[0.66]">
            Move from scattered agricultural data to a calm, explainable AI operating system.
          </p>
          <div className="mt-12">
            <PremiumButton href="/dashboard" variant="light">Launch FarmSphere AI</PremiumButton>
          </div>
        </div>
      </section>

      <footer className="bg-[#061911] px-6 py-16 text-white">
        <div className="mx-auto grid max-w-6xl gap-10 md:grid-cols-[1.2fr_0.8fr_0.8fr_0.8fr]">
          <div>
            <FarmLogo />
            <p className="mt-5 max-w-sm text-sm leading-7 text-white/[0.58]">
              Explainable agricultural intelligence for farmers, built with premium AI systems and
              a field-first product experience.
            </p>
          </div>
          <div>
            <p className="font-semibold">Quick Links</p>
            <div className="mt-4 space-y-3 text-sm text-white/[0.58]">
              <a href="#platform" className="block hover:text-white">Platform</a>
              <a href="#ai-workflow" className="block hover:text-white">AI Workflow</a>
              <a href="#technology" className="block hover:text-white">Technology</a>
            </div>
          </div>
          <div>
            <p className="font-semibold">Technology Stack</p>
            <div className="mt-4 space-y-3 text-sm text-white/[0.58]">
              <p>Gemini 2.5 Flash</p>
              <p>LangGraph</p>
              <p>FastAPI + Next.js</p>
            </div>
          </div>
          <div>
            <p className="font-semibold">GitHub</p>
            <a
              href="https://github.com/arka-coder/FarmSphere-AI"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex items-center gap-2 rounded-full border border-white/[0.12] bg-white/[0.08] px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/[0.14]"
            >
              <Github className="h-4 w-4" />
              Repository
            </a>
            <div className="mt-8 border-t border-white/[0.1] pt-6">
              <p className="flex items-center gap-2 text-sm font-medium text-white/[0.78]">
                Made by Arka Roy
              </p>
              <div className="mt-4 flex items-center gap-3">
                <a
                  href="https://github.com/arka-coder"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-white/[0.08] text-white/[0.68] transition hover:bg-white/[0.16] hover:text-white"
                  aria-label="GitHub"
                >
                  <Github className="h-4 w-4" />
                </a>
                <a
                  href="https://www.linkedin.com/in/arka-roy-76b1561b2"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-white/[0.08] text-white/[0.68] transition hover:bg-[#0077b5] hover:text-white"
                  aria-label="LinkedIn"
                >
                  <Linkedin className="h-4 w-4" />
                </a>
                <a
                  href="https://www.instagram.com/i_am_a.roy/?hl=en"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-white/[0.08] text-white/[0.68] transition hover:bg-gradient-to-tr hover:from-yellow-500 hover:via-pink-500 hover:to-purple-500 hover:text-white"
                  aria-label="Instagram"
                >
                  <Instagram className="h-4 w-4" />
                </a>
              </div>
            </div>
            <p className="mt-5 flex items-center gap-2 text-xs text-white/[0.48]">
              <Zap className="h-3.5 w-3.5 text-amber-200" />
              Made with Gemini AI
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}
