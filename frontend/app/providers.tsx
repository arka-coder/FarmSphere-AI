"use client";

import { ThemeProvider } from "next-themes";
import { Toaster } from "react-hot-toast";
import { FarmProvider } from "@/contexts/FarmContext";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
      <FarmProvider>
        {children}
      </FarmProvider>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#161d2d",
            color: "#f1f5f9",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: "12px",
            fontSize: "13px",
            boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
            padding: "12px 16px",
          },
          success: {
            iconTheme: { primary: "#10b981", secondary: "#161d2d" },
          },
          error: {
            iconTheme: { primary: "#f43f5e", secondary: "#161d2d" },
          },
        }}
      />
    </ThemeProvider>
  );
}
