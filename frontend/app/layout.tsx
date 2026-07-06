import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import { Providers } from "./providers";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair" });

export const metadata: Metadata = {
  title: "FarmSphere AI — Intelligent Agricultural Companion",
  description:
    "Multi-agent agricultural intelligence platform with disease detection, weather advisory, market intelligence, risk assessment, and crop planning powered by Gemini AI.",
  keywords: "agriculture, AI, disease detection, crop management, farming, India",
  openGraph: {
    title: "FarmSphere AI",
    description: "Your intelligent agricultural companion",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${playfair.variable}`}>
      <body className="font-sans">
        <div className="noise-overlay" />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
