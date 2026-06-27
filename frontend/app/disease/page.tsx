"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useDropzone } from "react-dropzone";
import { Upload, X, Loader2, AlertTriangle, CheckCircle } from "lucide-react";
import toast from "react-hot-toast";
import Sidebar from "@/components/layout/Sidebar";
import ConfidenceGauge from "@/components/chat/ConfidenceGauge";
import SourceCards from "@/components/chat/SourceCards";
import AgentTimeline from "@/components/chat/AgentTimeline";
import { uploadImage, type ChatResponse } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const CROPS = ["Tomato", "Wheat", "Rice", "Potato", "Cotton", "Maize", "Sugarcane", "Onion", "Soybean"];

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
    reader.onload = e => setPreview(e.target?.result as string);
    reader.readAsDataURL(f);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "image/*": [] }, multiple: false,
  });

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const data = await uploadImage(file, crop.toLowerCase());
      setResult(data);
      if (data.disease?.hitl_required) {
        toast("Additional images needed for confident diagnosis", { icon: "⚠️", duration: 5000 });
      }
    } catch (e: any) {
      toast.error("Analysis failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-6">
          <div>
            <h1 className="font-display text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              🔬 Disease Detection
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
              Upload a plant image for AI-powered disease diagnosis using Gemini Vision + ChromaDB RAG
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upload panel */}
            <div className="space-y-4">
              {/* Crop selector */}
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-200 block mb-2">Select Crop</label>
                <div className="flex flex-wrap gap-2">
                  {CROPS.map(c => (
                    <button key={c} onClick={() => setCrop(c)}
                      className={`text-sm px-3 py-1.5 rounded-full border transition-all ${
                        crop === c
                          ? "bg-farm-600 text-white border-farm-600 shadow-farm"
                          : "bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:border-farm-400"
                      }`}>
                      {c}
                    </button>
                  ))}
                </div>
              </div>

              {/* Drop zone */}
              <div {...getRootProps()} className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
                isDragActive ? "border-farm-500 bg-farm-50 dark:bg-farm-950/30" :
                preview ? "border-farm-400 bg-farm-50/50 dark:bg-farm-950/20" :
                "border-gray-200 dark:border-gray-700 hover:border-farm-400 bg-white dark:bg-gray-900"
              }`}>
                <input {...getInputProps()} />
                <AnimatePresence mode="wait">
                  {preview ? (
                    <motion.div key="preview" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                      <img src={preview} alt="Plant" className="max-h-48 rounded-xl mx-auto object-contain shadow" />
                      <button onClick={e => { e.stopPropagation(); setFile(null); setPreview(null); setResult(null); }}
                        className="mt-3 text-xs text-red-500 hover:text-red-700 flex items-center gap-1 mx-auto">
                        <X size={12} /> Remove image
                      </button>
                    </motion.div>
                  ) : (
                    <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                      <Upload size={32} className="mx-auto text-gray-300 dark:text-gray-600 mb-3" />
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Drop your plant image here
                      </p>
                      <p className="text-xs text-gray-400 mt-1">or click to browse · JPG, PNG, WEBP</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Analyze button */}
              <motion.button
                whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                onClick={handleAnalyze}
                disabled={!file || loading}
                className="btn-farm w-full py-3 rounded-xl flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <><Loader2 size={18} className="animate-spin" /> Analyzing with Gemini Vision...</>
                ) : (
                  <><span>🔬</span> Analyze for Disease</>
                )}
              </motion.button>

              {/* HITL note */}
              <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-3">
                <p className="text-xs text-amber-700 dark:text-amber-300 font-medium flex items-center gap-1.5">
                  <AlertTriangle size={12} /> Human-in-the-Loop Safety
                </p>
                <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                  If confidence is below 75%, FarmSphere will ask for additional images and recommend expert consultation.
                </p>
              </div>
            </div>

            {/* Results panel */}
            <AnimatePresence>
              {result && result.disease && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-4"
                >
                  {/* Severity badge */}
                  <div className={`flex items-center gap-2 p-3 rounded-xl ${
                    result.disease.hitl_required ? "alert-medium" :
                    result.disease.severity === "severe" ? "alert-critical" :
                    result.disease.severity === "moderate" ? "alert-high" : "alert-low"
                  }`}>
                    {result.disease.hitl_required ? <AlertTriangle size={16} /> : <CheckCircle size={16} />}
                    <div>
                      <p className="text-sm font-bold">{result.disease.name}</p>
                      <p className="text-xs capitalize">{result.disease.severity} severity · {result.disease.hitl_required ? "Review needed" : "Confident diagnosis"}</p>
                    </div>
                  </div>

                  {/* Confidence gauge */}
                  <div className="glass-card bg-white dark:bg-gray-900 p-4">
                    <ConfidenceGauge
                      confidence={result.disease.confidence}
                      label={result.disease.name}
                      alternatives={result.disease.alternatives}
                      size="md"
                    />
                  </div>

                  {/* Response */}
                  {result.response && (
                    <div className="glass-card bg-white dark:bg-gray-900 p-4">
                      <div className="prose-farm text-sm">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.response}</ReactMarkdown>
                      </div>
                    </div>
                  )}

                  {/* Timeline */}
                  {result.execution_timeline?.length > 0 && (
                    <div className="glass-card bg-white dark:bg-gray-900 p-4">
                      <AgentTimeline timeline={result.execution_timeline} />
                    </div>
                  )}

                  {/* Sources */}
                  {result.source_documents?.length > 0 && (
                    <div className="glass-card bg-white dark:bg-gray-900 p-4">
                      <p className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">📌 Sources</p>
                      <SourceCards sources={result.source_documents} />
                    </div>
                  )}
                </motion.div>
              )}

              {!result && !loading && (
                <div className="flex flex-col items-center justify-center h-full text-center p-8">
                  <span className="text-5xl mb-4">🌿</span>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Upload a plant image to see AI diagnosis, confidence scores, and treatment recommendations here.
                  </p>
                </div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
