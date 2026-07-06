"use client";
import { useState, useRef, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send, ImagePlus, X, Loader2, Microscope,
  CloudSun, TrendingUp, Zap, Shield, Globe,
} from "lucide-react";

interface Props {
  onSend: (message: string, imageFile?: File) => void;
  isLoading: boolean;
}

const QUICK_PROMPTS = [
  { icon: Microscope,  label: "Identify disease",         prompt: "Please analyze this plant image for disease" },
  { icon: CloudSun,    label: "Weather advisory",         prompt: "What's the weather advisory for my crop today?" },
  { icon: TrendingUp,  label: "Market prices",            prompt: "What are the current market prices for my crop?" },
  { icon: Zap,         label: "What-If simulation",       prompt: "What if rainfall doubles next week for my crop?" },
  { icon: Shield,      label: "Check crop risks",         prompt: "Assess the current risks for my farm" },
  { icon: Globe,       label: "Government schemes",       prompt: "What government schemes am I eligible for?" },
];

export default function ChatInput({ onSend, isLoading }: Props) {
  const [text, setText] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const onDrop = useCallback((accepted: File[]) => {
    const file = accepted[0];
    if (!file) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = e => setImagePreview(e.target?.result as string);
    reader.readAsDataURL(file);
    setText(prev => prev || "Please analyze this plant image for disease");
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "image/*": [] }, multiple: false, noClick: true,
  });

  const handleSend = () => {
    const msg = text.trim();
    if (!msg && !imageFile) return;
    onSend(msg || "Analyze this plant image", imageFile || undefined);
    setText("");
    setImageFile(null);
    setImagePreview(null);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }
  };

  const canSend = !isLoading && (text.trim().length > 0 || imageFile !== null);

  return (
    <div className="space-y-4">
      {/* Quick prompt chips */}
      <div className="flex flex-wrap gap-2.5 pb-1">
        {QUICK_PROMPTS.map((p) => {
          const Icon = p.icon;
          return (
            <button
              key={p.label}
              onClick={() => { setText(p.prompt); textareaRef.current?.focus(); }}
              className="shrink-0 flex items-center gap-1.5 text-xs font-semibold px-4 py-2 rounded-full transition-all whitespace-nowrap bg-white text-slate-600 border border-slate-200 shadow-sm hover:shadow-md hover:border-emerald-200 hover:text-emerald-700 hover:bg-emerald-50/50"
            >
              <Icon size={12} strokeWidth={2} />
              {p.label}
            </button>
          );
        })}
      </div>

      {/* Main input container */}
      <div
        {...getRootProps()}
        className="relative rounded-[28px] transition-all bg-white shadow-sm"
        style={{
          border: isDragActive ? "2px solid var(--emerald)" : "1px solid rgba(0,0,0,0.06)",
          boxShadow: isDragActive ? "0 0 0 4px rgba(34,197,94,0.1), 0 4px 20px rgba(0,0,0,0.05)" : "0 4px 20px rgba(0,0,0,0.03)",
        }}
      >
        <input {...getInputProps()} />

        {/* Image preview */}
        <AnimatePresence>
          {imagePreview && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="px-4 pt-4"
            >
              <div className="relative inline-flex items-center gap-3 p-2.5 rounded-2xl bg-emerald-50 border border-emerald-100 shadow-sm">
                <img src={imagePreview} alt="Upload" className="h-16 w-16 rounded-xl object-cover shadow-sm" />
                <div className="pr-4">
                  <p className="text-sm font-bold text-emerald-800">Disease Scan Ready</p>
                  <p className="text-xs font-medium text-emerald-600 mt-0.5">
                    {imageFile?.name ?? "image.jpg"}
                  </p>
                </div>
                <button
                  onClick={() => { setImageFile(null); setImagePreview(null); }}
                  className="absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center bg-rose-500 shadow-sm border-2 border-white hover:scale-110 transition-transform"
                >
                  <X size={12} className="text-white" strokeWidth={2.5} />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Textarea + controls */}
        <div className="flex items-end gap-3 px-4 py-3 min-h-[64px]">
          {/* Image upload */}
          <label className="p-2.5 rounded-xl cursor-pointer transition-all shrink-0 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 mb-0.5">
            <ImagePlus size={20} strokeWidth={2} />
            <input type="file" accept="image/*" className="hidden"
              onChange={e => { if (e.target.files?.[0]) onDrop([e.target.files[0]]); }} />
          </label>

          {/* Textarea */}
          <textarea
            ref={textareaRef}
            value={text}
            onChange={handleTextareaChange}
            onKeyDown={handleKey}
            placeholder={
              isDragActive ? "Drop your plant image here…" :
              "Ask about crops, diseases, weather, markets…"
            }
            rows={1}
            disabled={isLoading}
            className="flex-1 resize-none bg-transparent text-base font-medium leading-relaxed py-2 min-h-[40px] max-h-[120px] focus:outline-none text-slate-800 placeholder:text-slate-400"
          />

          {/* Send button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={!canSend}
            className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0 transition-all mb-0.5"
            style={{
              background: canSend ? "linear-gradient(135deg, var(--emerald), var(--primary-green))" : "#f1f5f9",
              boxShadow: canSend ? "0 8px 16px -4px rgba(34,197,94,0.3)" : "none",
              cursor: canSend ? "pointer" : "not-allowed",
            }}
          >
            {isLoading
              ? <Loader2 size={20} className="animate-spin text-slate-400" />
              : <Send size={20} style={{ color: canSend ? "white" : "#94a3b8" }} strokeWidth={2.5} className="ml-1" />
            }
          </motion.button>
        </div>

        {/* Drag overlay */}
        {isDragActive && (
          <div className="absolute inset-0 rounded-[28px] flex items-center justify-center bg-emerald-50/90 backdrop-blur-sm border-2 border-dashed border-emerald-400 z-10">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-white flex items-center justify-center mx-auto mb-3 shadow-sm text-emerald-500">
                <ImagePlus size={32} strokeWidth={2} />
              </div>
              <p className="text-lg font-bold text-emerald-800">Drop plant image for disease scan</p>
            </div>
          </div>
        )}
      </div>

      <p className="text-center text-xs font-semibold text-slate-400 mt-2">
        FarmSphere Intelligence can make mistakes. Check important information.
      </p>
    </div>
  );
}
