"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import { streamChat, type ChatResponse } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import ReasoningChain from "./ReasoningChain";
import { AlertCircle, RefreshCw } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  data?: ChatResponse;
  timestamp: Date;
  isLoading?: boolean;
  loadingStage?: string;
  isError?: boolean;
}

interface Props {
  farmerName?: string;
  farmerId?: string;
  cropType?: string;
  location?: string;
  onAgentUpdate?: (agent?: string, isLoading?: boolean) => void;
}

const STAGES = [
  "Building field context",
  "Routing to specialist agents",
  "Retrieving agronomy evidence",
  "Assessing weather and seasonal risk",
  "Synthesizing recommendation",
  "Preparing explainability",
];

const WELCOME_MSG: Message = {
  id: "welcome",
  role: "assistant",
  content: `# FarmSphere AI is ready

I can reason across crop health, satellite signals, weather, market movement, and farm memory.

Try one of these:

- *My tomato leaves have brown spots with yellow halos. What should I do?*
- *Should I irrigate before tomorrow's rain?*
- *Upload a leaf image and ask for a diagnosis.*`,
  timestamp: new Date(),
};

export default function ChatWindow({ farmerName = "Farmer", farmerId, cropType, location, onAgentUpdate }: Props) {

  const [messages, setMessages] = useState<Message[]>([WELCOME_MSG]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState<string | undefined>();
  const [stageIndex, setStageIndex] = useState(0);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const bottomRef = useRef<HTMLDivElement>(null);
  const stageIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  // Cycle through loading stages
  const startStageAnimation = (msgId: string) => {
    setStageIndex(0);
    setElapsedSeconds(0);
    stageIntervalRef.current = setInterval(() => {
      setStageIndex(prev => Math.min(prev + 1, STAGES.length - 1));
    }, 2200);
    timerRef.current = setInterval(() => {
      setElapsedSeconds(prev => prev + 1);
    }, 1000);
  };

  const stopStageAnimation = () => {
    if (stageIntervalRef.current) clearInterval(stageIntervalRef.current);
    if (timerRef.current) clearInterval(timerRef.current);
    stageIntervalRef.current = null;
    timerRef.current = null;
  };

  const handleRetry = async (originalText: string) => {
    setMessages(prev => prev.filter(m => !m.isError));
    handleSend(originalText);
  };

  const handleSend = async (text: string, imageFile?: File) => {
    if (isLoading) return;

    let image_b64: string | undefined;
    if (imageFile) {
      const buffer = await imageFile.arrayBuffer();
      image_b64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
    }

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setActiveAgent(undefined);
    onAgentUpdate?.(undefined, true);

    const lId = Date.now().toString() + "_loading";
    setLoadingId(lId);
    setMessages(prev => [...prev, {
      id: lId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
      isLoading: true,
      loadingStage: STAGES[0],
    }]);
    startStageAnimation(lId);

    try {
      let resultData: ChatResponse | null = null;

      await streamChat(
        {
          message: text,
          farmer_id: farmerId,
          farmer_name: farmerName,
          crop_type: cropType,
          location,
          image_base64: image_b64,
        },
        (agent, agentMessage) => {
          setActiveAgent(agent);
          onAgentUpdate?.(agent, true);
          setMessages(prev => prev.map(m =>
            m.id === lId ? { ...m, loadingStage: agentMessage } : m
          ));
        },
        (data) => { resultData = data; },
        (error) => { toast.error("Agent error: " + error); },
      );

      stopStageAnimation();

      if (resultData) {
        const r = resultData as ChatResponse;
        setMessages(prev => prev.map(m =>
          m.id === lId ? {
            id: lId, role: "assistant" as const,
            content: r.response, data: r,
            timestamp: new Date(), isLoading: false,
          } : m
        ));
        if (r.active_alerts?.length) {
          const ca = r.active_alerts.find(a => a.severity === "critical" || a.severity === "high");
          if (ca) toast(ca.title, { icon: "⚠️", duration: 5000 });
        }
      }
    } catch (err: any) {
      stopStageAnimation();
      try {
        const { sendChat } = await import("@/lib/api");
        const data = await sendChat({
          message: text, farmer_id: farmerId, farmer_name: farmerName,
          crop_type: cropType, location,
          image_base64: image_b64,
        });
        setMessages(prev => prev.map(m =>
          m.id === lId ? {
            id: lId, role: "assistant" as const,
            content: data.response, data,
            timestamp: new Date(), isLoading: false,
          } : m
        ));
      } catch {
        setMessages(prev => prev.map(m =>
          m.id === lId ? {
            ...m, isLoading: false, isError: true,
            content: "Unable to connect to the FarmSphere AI backend. Please ensure the backend is running at port 8000.",
          } : m
        ));
        toast.error("Backend connection failed");
      }
    } finally {
      setIsLoading(false);
      setActiveAgent(undefined);
      setLoadingId(null);
      onAgentUpdate?.(undefined, false);
    }
  };

  useEffect(() => {
    if (loadingId) {
      setMessages(prev => prev.map(m =>
        m.id === loadingId ? { ...m, loadingStage: STAGES[stageIndex] } : m
      ));
    }
  }, [stageIndex, loadingId]);

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-[32px] border border-white/80 bg-white/76 shadow-[0_28px_100px_rgba(15,23,42,0.10)] backdrop-blur-3xl">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-4 scrollbar-hide md:px-8 md:py-8">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              elapsedSeconds={msg.isLoading ? elapsedSeconds : undefined}
              onRetry={msg.isError ? () => handleRetry(
                messages.find(m => m.role === "user" && messages.indexOf(m) < messages.indexOf(msg))?.content ?? ""
              ) : undefined}
            />
          ))}
        </AnimatePresence>

        {/* Active agent indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.98 }}
            className="px-4 py-2 max-w-sm"
          >
            <ReasoningChain activeAgent={activeAgent} />
          </motion.div>
        )}
        <div ref={bottomRef} />

      </div>

      {/* Input area */}
      <div className="shrink-0 border-t border-slate-100 bg-white/65 px-5 pb-5 pt-4 backdrop-blur-md md:px-8 md:pb-6">
        <ChatInput
          onSend={handleSend}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
