"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import toast from "react-hot-toast";
import {
  AlertTriangle,
  CheckCircle2,
  ImagePlus,
  Loader2,
  Microscope,
  ScanLine,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  X,
} from "lucide-react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import AgentTimeline from "@/components/chat/AgentTimeline";
import ConfidenceGauge from "@/components/chat/ConfidenceGauge";
import SourceCards from "@/components/chat/SourceCards";
import { uploadImage, type ChatResponse } from "@/lib/api";

const CROPS = ["Tomato", "Wheat", "Rice", "Potato", "Cotton", "Maize", "Sugarcane", "Onion", "Soybean"];
const scanSteps = ["Gemini Vision", "Disease Agent", "Weather Agent", "Knowledge Retrieval", "Risk Assessment", "Explainability"];

export default function DiseasePage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [crop, setCrop] = useState("Tomato");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ChatResponse | null>(null);

  const onDrop = (files: File[]) => {
    const f = files[0];
    if (!f) return;
    setFile(f);
    setResult(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(f);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [] },
    multiple: false,
  });

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const data = await uploadImage(file, crop.toLowerCase());
      setResult(data);
      if (data.disease?.hitl_required) {
        toast("Additional images needed for confident diagnosis", { duration: 5000 });
      }
    } catch (e: any) {
      toast.error("Analysis failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const disease = result?.disease;

  return (
    <div className="relative flex h-screen overflow-hidden bg-base">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,#f8fbf9_0%,#f1f7f3_42%,#fbf8ff_100%)]" />
      <div className="absolute inset-x-0 top-0 h-80 bg-[radial-gradient(circle_at_50%_0%,rgba(124,58,237,0.12),transparent_48%)]" />
      <Sidebar />

      <main className="relative flex flex-1 flex-col overflow-hidden">
        <TopNav />

        <div className="flex-1 overflow-y-auto px-5 pb-10 pt-32 scrollbar-hide md:px-8">
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
            className="mx-auto max-w-7xl"
          >
            <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="inline-flex items-center gap-2 rounded-full bg-violet-50 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.18em] text-violet-700">
                  <Stethoscope size={14} />
                  Crop Health Diagnosis
                </p>
                <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 md:text-5xl">
                  Upload a leaf. Watch FarmSphere localize the risk.
                </h1>
              </div>
              <div className="rounded-full border border-white/80 bg-white/74 px-4 py-2 text-sm font-semibold text-slate-600 shadow-[0_12px_40px_rgba(15,23,42,0.07)] backdrop-blur-2xl">
                Human review triggered below 75% confidence
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
              <section className="rounded-[32px] border border-white/80 bg-white/76 p-5 shadow-[0_28px_100px_rgba(15,23,42,0.10)] backdrop-blur-3xl md:p-7">
                <div className="mb-5 flex flex-wrap gap-2">
                  {CROPS.map((c) => (
                    <button
                      key={c}
                      onClick={() => setCrop(c)}
                      className={`rounded-full border px-4 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-violet-300 ${
                        crop === c
                          ? "border-violet-600 bg-violet-600 text-white shadow-[0_10px_26px_rgba(124,58,237,0.18)]"
                          : "border-slate-200 bg-white text-slate-600 hover:border-violet-300 hover:text-violet-700"
                      }`}
                    >
                      {c}
                    </button>
                  ))}
                </div>

                <div
                  {...getRootProps()}
                  className={`relative min-h-[460px] cursor-pointer overflow-hidden rounded-[30px] border-2 border-dashed transition ${
                    isDragActive
                      ? "border-violet-500 bg-violet-50"
                      : preview
                        ? "border-emerald-300 bg-slate-950"
                        : "border-slate-300 bg-white/70 hover:border-violet-400"
                  }`}
                >
                  <input {...getInputProps()} />
                  {preview ? (
                    <div className="relative h-[460px]">
                      <img src={preview} alt="Uploaded crop sample" className="h-full w-full object-contain" />
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-950/55 via-transparent to-slate-950/20" />
                      {(loading || result) && (
                        <>
                          <motion.div
                            className="absolute left-[18%] top-[22%] h-32 w-40 rounded-[46%] border-2 border-emerald-300/90 bg-emerald-300/10 shadow-[0_0_42px_rgba(110,231,183,0.45)]"
                            animate={{ scale: [1, 1.05, 1], opacity: [0.72, 1, 0.72] }}
                            transition={{ repeat: Infinity, duration: 1.8 }}
                          />
                          <motion.div
                            className="absolute left-0 right-0 top-0 h-20 bg-gradient-to-b from-emerald-300/0 via-emerald-300/45 to-emerald-300/0"
                            animate={{ y: [0, 410, 0] }}
                            transition={{ repeat: Infinity, duration: 3.1, ease: "easeInOut" }}
                          />
                        </>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setFile(null);
                          setPreview(null);
                          setResult(null);
                        }}
                        className="absolute right-4 top-4 flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-slate-700 shadow-lg transition hover:bg-white"
                        aria-label="Remove image"
                      >
                        <X size={18} />
                      </button>
                      <div className="absolute bottom-5 left-5 right-5 flex flex-wrap items-center justify-between gap-3 text-white">
                        <div>
                          <p className="text-sm font-semibold text-white/70">Sample loaded</p>
                          <p className="text-2xl font-semibold">{crop} leaf scan</p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAnalyze();
                          }}
                          disabled={!file || loading}
                          className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-violet-50 disabled:opacity-60"
                        >
                          {loading ? <Loader2 size={18} className="animate-spin" /> : <ScanLine size={18} />}
                          {loading ? "Scanning image" : "Run diagnosis"}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex h-[460px] flex-col items-center justify-center p-8 text-center">
                      <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-violet-50 text-violet-600">
                        <ImagePlus size={30} strokeWidth={1.7} />
                      </div>
                      <p className="mt-6 text-2xl font-semibold tracking-tight text-slate-950">
                        Drop a clear crop image here
                      </p>
                      <p className="mt-3 max-w-md text-sm leading-6 text-slate-500">
                        FarmSphere will scan symptoms, compare alternative diagnoses, and explain the recommended treatment path.
                      </p>
                    </div>
                  )}
                </div>
              </section>

              <aside className="space-y-4">
                <div className="rounded-[32px] border border-white/80 bg-white/76 p-5 shadow-[0_28px_100px_rgba(15,23,42,0.10)] backdrop-blur-3xl">
                  <p className="flex items-center gap-2 text-sm font-bold text-slate-950">
                    <Sparkles size={17} className="text-violet-600" />
                    Diagnosis Intelligence
                  </p>

                  {loading && (
                    <div className="mt-5 space-y-3">
                      {scanSteps.map((step, index) => (
                        <motion.div
                          key={step}
                          initial={{ opacity: 0, x: 12 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.08 }}
                          className="flex items-center gap-3 rounded-2xl border border-violet-100 bg-violet-50/70 px-4 py-3"
                        >
                          <span className="h-2.5 w-2.5 rounded-full bg-violet-500 shadow-[0_0_16px_rgba(124,58,237,0.7)]" />
                          <span className="text-sm font-semibold text-violet-900">{step}</span>
                        </motion.div>
                      ))}
                    </div>
                  )}

                  {!loading && !result && (
                    <div className="mt-5 rounded-3xl border border-dashed border-slate-200 bg-white/70 p-6 text-center">
                      <Microscope size={32} className="mx-auto text-slate-300" />
                      <p className="mt-3 text-sm font-semibold text-slate-700">Awaiting image analysis</p>
                      <p className="mt-2 text-sm leading-6 text-slate-500">
                        Results will include severity, confidence, reasoning, treatment timeline, and source evidence.
                      </p>
                    </div>
                  )}

                  <AnimatePresence>
                    {disease && (
                      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mt-5 space-y-4">
                        <div className={`rounded-3xl border p-4 ${disease.hitl_required ? "border-amber-200 bg-amber-50" : "border-emerald-200 bg-emerald-50"}`}>
                          <p className="flex items-center gap-2 text-sm font-bold text-slate-950">
                            {disease.hitl_required ? <AlertTriangle size={17} className="text-amber-600" /> : <CheckCircle2 size={17} className="text-emerald-700" />}
                            {disease.name}
                          </p>
                          <p className="mt-1 text-sm capitalize text-slate-600">
                            {disease.severity} severity · {disease.hitl_required ? "expert review advised" : "confident diagnosis"}
                          </p>
                        </div>

                        <ConfidenceGauge confidence={disease.confidence} label={disease.name} alternatives={disease.alternatives} size="md" />

                        <div className="rounded-3xl border border-slate-200 bg-white/70 p-4">
                          <p className="mb-3 flex items-center gap-2 text-sm font-bold text-slate-950">
                            <ShieldCheck size={17} className="text-emerald-700" />
                            Treatment Timeline
                          </p>
                          {["Today: isolate affected leaves and photograph underside", "24-48h: apply recommended treatment after rain clears", "7 days: re-scan and compare symptom spread"].map((item) => (
                            <p key={item} className="border-t border-slate-100 py-3 text-sm leading-6 text-slate-600 first:border-t-0 first:pt-0">
                              {item}
                            </p>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {result?.response && (
                  <div className="rounded-[28px] border border-white/80 bg-white/76 p-5 shadow-[0_22px_80px_rgba(15,23,42,0.08)] backdrop-blur-2xl">
                    <div className="prose-farm text-sm">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.response}</ReactMarkdown>
                    </div>
                  </div>
                )}

                {result?.execution_timeline?.length ? (
                  <div className="rounded-[28px] border border-white/80 bg-white/76 p-5 shadow-[0_22px_80px_rgba(15,23,42,0.08)] backdrop-blur-2xl">
                    <AgentTimeline timeline={result.execution_timeline} />
                  </div>
                ) : null}

                {result?.source_documents?.length ? (
                  <div className="rounded-[28px] border border-white/80 bg-white/76 p-5 shadow-[0_22px_80px_rgba(15,23,42,0.08)] backdrop-blur-2xl">
                    <p className="mb-3 text-xs font-bold uppercase tracking-[0.18em] text-slate-400">Knowledge Sources</p>
                    <SourceCards sources={result.source_documents} />
                  </div>
                ) : null}
              </aside>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
