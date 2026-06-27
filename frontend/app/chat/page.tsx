"use client";
import Sidebar from "@/components/layout/Sidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import { motion } from "framer-motion";

export default function ChatPage() {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-white dark:bg-gray-900 border-b border-gray-100 dark:border-farm-900 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-farm-gradient flex items-center justify-center text-xl shadow-farm">
              🌾
            </div>
            <div>
              <h1 className="font-display font-bold text-gray-900 dark:text-white">FarmSphere AI Assistant</h1>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="w-2 h-2 bg-farm-500 rounded-full animate-pulse" />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  17 agents active · Gemini 2.0 Flash · ChromaDB RAG · LangGraph
                </p>
              </div>
            </div>
            <div className="ml-auto flex gap-2">
              {["Disease", "Weather", "Market", "Simulation"].map((tag) => (
                <span key={tag} className="hidden md:block text-xs bg-farm-50 dark:bg-farm-950/50 text-farm-700 dark:text-farm-300 border border-farm-200 dark:border-farm-800 px-2.5 py-1 rounded-full font-medium">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Chat window */}
        <div className="flex-1 overflow-hidden">
          <ChatWindow
            farmerName="Farmer"
            cropType="tomato"
            location="Nashik, Maharashtra"
          />
        </div>
      </main>
    </div>
  );
}
