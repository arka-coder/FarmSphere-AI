"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import { streamChat, type ChatResponse } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  data?: ChatResponse;
  timestamp: Date;
}

interface Props {
  farmerName?: string;
  farmerId?: string;
  cropType?: string;
  location?: string;
}

const WELCOME_MSG: Message = {
  id: "welcome",
  role: "assistant",
  content: `# 🌾 Welcome to FarmSphere AI

I'm your intelligent agricultural companion powered by **17 specialized AI agents**.

**I can help you with:**
• 🔬 **Disease Detection** — Upload a leaf image for instant diagnosis
• 🌤️ **Weather Advice** — Real-time weather-aware crop recommendations
• 📚 **Knowledge Base** — ICAR-certified farming guidance
• ⚠️ **Risk Assessment** — Predictive disease and pest risk scores
• 📈 **Market Intelligence** — Live crop prices and selling recommendations
• 🔮 **Scenario Simulation** — "What if rainfall doubles next week?"
• 🏛️ **Government Schemes** — PM-KISAN, PMFBY eligibility

**Try asking:** *"My tomato leaves have brown spots with yellow halos"* or drag a plant image here.`,
  timestamp: new Date(),
};

export default function ChatWindow({ farmerName = "Farmer", farmerId, cropType, location }: Props) {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MSG]);
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState("en");
  const [activeAgent, setActiveAgent] = useState<string | undefined>();
  const [streamingTimeline, setStreamingTimeline] = useState<any[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  const handleSend = async (text: string, imageFile?: File) => {
    if (isLoading) return;

    // Convert image to base64 if provided
    let image_b64: string | undefined;
    if (imageFile) {
      const buffer = await imageFile.arrayBuffer();
      image_b64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
    }

    // Add user message
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setStreamingTimeline([]);
    setActiveAgent(undefined);

    // Add loading placeholder
    const loadingId = Date.now().toString() + "_loading";
    setMessages(prev => [...prev, {
      id: loadingId,
      role: "assistant",
      content: "Analyzing with 17 AI agents...",
      timestamp: new Date(),
    }]);

    try {
      let resultData: ChatResponse | null = null;

      await streamChat(
        {
          message: text,
          farmer_id: farmerId,
          farmer_name: farmerName,
          crop_type: cropType,
          location,
          language: language as "en" | "hi" | "bn",
          image_base64: image_b64,
        },
        (agent, agentMessage) => {
          setActiveAgent(agent);
          // Update loading message text
          setMessages(prev => prev.map(m =>
            m.id === loadingId ? { ...m, content: agentMessage } : m
          ));
        },
        (data) => {
          resultData = data;
        },
        (error) => {
          toast.error("Agent error: " + error);
        },
      );

      if (resultData) {
        const r = resultData as ChatResponse;
        setMessages(prev => prev.map(m =>
          m.id === loadingId ? {
            id: loadingId,
            role: "assistant" as const,
            content: r.response,
            data: r,
            timestamp: new Date(),
          } : m
        ));
        if (r.active_alerts?.length) {
          const criticalAlert = r.active_alerts.find(a => a.severity === "critical" || a.severity === "high");
          if (criticalAlert) {
            toast(criticalAlert.title, { icon: "⚠️", duration: 5000 });
          }
        }
      }
    } catch (err: any) {
      // Fallback to non-streaming
      try {
        const { sendChat } = await import("@/lib/api");
        const data = await sendChat({
          message: text,
          farmer_id: farmerId,
          farmer_name: farmerName,
          crop_type: cropType,
          location,
          language: language as "en" | "hi" | "bn",
          image_base64: image_b64,
        });
        setMessages(prev => prev.map(m =>
          m.id === loadingId ? {
            id: loadingId,
            role: "assistant" as const,
            content: data.response,
            data,
            timestamp: new Date(),
          } : m
        ));
      } catch (e2: any) {
        setMessages(prev => prev.map(m =>
          m.id === loadingId ? {
            ...m,
            content: "⚠️ I'm unable to connect to the FarmSphere AI backend. Please ensure the backend is running at port 8000.",
          } : m
        ));
        toast.error("Backend connection failed");
      }
    } finally {
      setIsLoading(false);
      setActiveAgent(undefined);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
        </AnimatePresence>

        {/* Active agent indicator */}
        {isLoading && activeAgent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 px-2"
          >
            <div className="flex gap-1">
              {[0, 1, 2].map(n => (
                <motion.div key={n}
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ repeat: Infinity, duration: 0.9, delay: n * 0.15 }}
                  className="w-1.5 h-1.5 bg-farm-500 rounded-full"
                />
              ))}
            </div>
            <p className="text-xs text-gray-400">
              {activeAgent.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())} is working...
            </p>
          </motion.div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-100 dark:border-farm-900 p-4 bg-white/80 dark:bg-gray-900/80 backdrop-blur">
        <ChatInput
          onSend={handleSend}
          isLoading={isLoading}
          language={language}
          onLanguageChange={setLanguage}
        />
      </div>
    </div>
  );
}
