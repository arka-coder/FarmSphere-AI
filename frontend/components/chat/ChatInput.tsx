"use client";
import { useState, useRef, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Mic, Image, X, Globe, Loader2 } from "lucide-react";

interface Props {
  onSend: (message: string, imageFile?: File) => void;
  isLoading: boolean;
  language: string;
  onLanguageChange: (lang: string) => void;
}

const LANGUAGES = [
  { code: "en", label: "English", flag: "🇬🇧" },
  { code: "hi", label: "हिंदी", flag: "🇮🇳" },
  { code: "bn", label: "বাংলা", flag: "🇧🇩" },
];

const QUICK_PROMPTS = [
  "🔬 Identify this plant disease",
  "🌤️ Weather advisory for my crop",
  "📈 Current tomato prices",
  "🔮 What if rainfall doubles?",
  "📋 PM-KISAN eligibility",
  "⚠️ Check my crop risks",
];

export default function ChatInput({ onSend, isLoading, language, onLanguageChange }: Props) {
  const [text, setText] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [showLangPicker, setShowLangPicker] = useState(false);
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
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    // Auto-resize
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }
  };

  return (
    <div className="space-y-3">
      {/* Quick prompts */}
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
        {QUICK_PROMPTS.map((p) => (
          <button
            key={p}
            onClick={() => { setText(p.slice(2).trim()); textareaRef.current?.focus(); }}
            className="shrink-0 text-xs bg-farm-50 dark:bg-farm-950/50 text-farm-700 dark:text-farm-300
                       border border-farm-200 dark:border-farm-800 px-3 py-1.5 rounded-full
                       hover:bg-farm-100 dark:hover:bg-farm-900/50 transition-colors whitespace-nowrap"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Drop zone wrapper */}
      <div
        {...getRootProps()}
        className={`relative rounded-2xl border-2 transition-all ${
          isDragActive
            ? "border-farm-500 bg-farm-50 dark:bg-farm-950/50"
            : "border-gray-200 dark:border-farm-800 bg-white dark:bg-gray-900"
        }`}
      >
        <input {...getInputProps()} />

        {/* Image preview */}
        <AnimatePresence>
          {imagePreview && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="p-3 border-b border-gray-100 dark:border-farm-900"
            >
              <div className="relative inline-block">
                <img src={imagePreview} alt="Upload preview" className="h-24 rounded-xl object-cover shadow" />
                <button
                  onClick={() => { setImageFile(null); setImagePreview(null); }}
                  className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center shadow"
                >
                  <X size={10} />
                </button>
                <span className="absolute -bottom-1.5 left-0 right-0 text-center text-xs bg-farm-600 text-white rounded-full px-2">
                  🔬 Disease Scan Ready
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input row */}
        <div className="flex items-end gap-2 p-3">
          {/* Image upload button */}
          <label className="p-2 rounded-xl text-gray-400 hover:text-farm-600 hover:bg-farm-50 dark:hover:bg-farm-950 cursor-pointer transition-colors">
            <Image size={20} />
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
              isDragActive ? "Drop your plant image here..." :
              language === "hi" ? "अपना प्रश्न यहाँ लिखें..." :
              language === "bn" ? "আপনার প্রশ্ন এখানে লিখুন..." :
              "Ask about your crops, diseases, weather, markets..."
            }
            rows={1}
            className="flex-1 resize-none bg-transparent text-sm text-gray-800 dark:text-white
                       placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none
                       leading-relaxed py-1 min-h-[36px] max-h-[120px]"
          />

          {/* Language picker */}
          <div className="relative">
            <button
              onClick={() => setShowLangPicker(prev => !prev)}
              className="p-2 rounded-xl text-gray-400 hover:text-farm-600 hover:bg-farm-50 dark:hover:bg-farm-950 transition-colors"
            >
              <Globe size={20} />
            </button>
            <AnimatePresence>
              {showLangPicker && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 8, scale: 0.95 }}
                  className="absolute bottom-full right-0 mb-2 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden z-10"
                >
                  {LANGUAGES.map(lang => (
                    <button
                      key={lang.code}
                      onClick={() => { onLanguageChange(lang.code); setShowLangPicker(false); }}
                      className={`flex items-center gap-2 w-full px-4 py-2 text-sm text-left hover:bg-farm-50 dark:hover:bg-farm-950 transition-colors ${
                        language === lang.code ? "text-farm-600 font-semibold bg-farm-50 dark:bg-farm-950" : "text-gray-700 dark:text-gray-200"
                      }`}
                    >
                      <span>{lang.flag}</span>
                      <span>{lang.label}</span>
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Send button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={isLoading || (!text.trim() && !imageFile)}
            className="btn-farm p-2.5 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </motion.button>
        </div>

        {/* Drag overlay */}
        {isDragActive && (
          <div className="absolute inset-0 bg-farm-500/10 border-2 border-farm-500 rounded-2xl flex items-center justify-center">
            <div className="text-center">
              <p className="text-2xl mb-1">🌿</p>
              <p className="text-sm font-semibold text-farm-700">Drop plant image for disease scan</p>
            </div>
          </div>
        )}
      </div>

      <p className="text-center text-xs text-gray-400">
        Drag & drop a leaf/fruit image for instant disease detection · Press Enter to send
      </p>
    </div>
  );
}
