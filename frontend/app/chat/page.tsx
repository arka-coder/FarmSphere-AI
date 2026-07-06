"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import ChatWindow from "@/components/chat/ChatWindow";
import { useFarm } from "@/contexts/FarmContext";
import { motion } from "framer-motion";

export default function ChatPage() {
  const { cropType, location } = useFarm();
  const [activeAgent, setActiveAgent] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="relative flex h-screen overflow-hidden bg-base">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,#f8fbf9_0%,#eef8f2_48%,#f7faff_100%)]" />
      <div className="absolute inset-x-0 top-0 h-80 bg-[radial-gradient(circle_at_50%_0%,rgba(16,185,129,0.16),transparent_48%)]" />
      <Sidebar />

      <main className="relative flex flex-1 flex-col overflow-hidden">
        <TopNav />

        <div className="flex-1 overflow-hidden px-5 pb-6 pt-24 md:px-8">
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
              className="mx-auto flex h-full max-w-4xl flex-col"
            >
              <div className="min-h-0 flex-1">
                <ChatWindow 
                  farmerName="Farmer" 
                  cropType={cropType} 
                  location={location} 
                  onAgentUpdate={(agent, loading) => {
                    setActiveAgent(agent);
                    if (loading !== undefined) setIsLoading(loading);
                  }}
                />
              </div>
            </motion.div>
        </div>
      </main>
    </div>
  );
}

