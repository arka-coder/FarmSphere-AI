/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Base surfaces (Light aesthetic)
        base: {
          DEFAULT: "#FAFBFA", // Warm White
          surface: "#FFFFFF", // White
          elevated: "#F4F7F5", // Soft Gray
          border: "rgba(0, 0, 0, 0.08)",
        },
        // Premium Greens
        green: {
          50:  "#f0fdf4",
          100: "#dcfce7", // Mint
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e", // Emerald
          600: "#16a34a",
          700: "#1E6F43", // Primary Green
          800: "#166534",
          900: "#14532d",
          950: "#052e16",
        },
        sage: {
          50:  "#f4f9f6",
          100: "#e5f2eb",
          200: "#cce4d8",
          300: "#A8D5BA", // Sage
          400: "#7abf96",
          500: "#55a377",
          600: "#3d825c",
        },
        // Slate (text / neutral)
        slate: {
          50:  "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#4B5563", // Text Secondary
          700: "#374151",
          800: "#1f2937",
          900: "#111827", // Text Primary
          950: "#030712",
        },
        // Keep some colors for alerts
        amber: {
          50:  "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          300: "#fcd34d",
          400: "#fbbf24",
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
        },
        rose: {
          50:  "#fff1f2",
          100: "#ffe4e6",
          200: "#fecdd3",
          300: "#fda4af",
          400: "#fb7185",
          500: "#f43f5e",
          600: "#e11d48",
          700: "#be123c",
        },
        blue: {
          50:  "#eff6ff",
          100: "#dbeafe",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
        }
      },
      fontFamily: {
        sans:    ["var(--font-inter)", "system-ui", "sans-serif"],
        display: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono:    ["Geist Mono", "Fira Code", "monospace"],
      },
      borderRadius: {
        "2xl": "16px",
        "3xl": "20px",
        "4xl": "24px",
      },
      spacing: {
        // Enforcing 8px scale roughly via existing TW defaults, but can add specifics if needed.
        "18": "4.5rem",
        "22": "5.5rem",
      },
      animation: {
        "fade-in":       "fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
        "slide-up":      "slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1)",
        "slide-in-left": "slideInLeft 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
        "pulse-slow":    "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer":       "shimmer 2.5s linear infinite",
        "float":         "float 6s ease-in-out infinite",
        "float-slow":    "float 8s ease-in-out infinite",
        "glow-pulse":    "glowPulse 2s ease-in-out infinite",
        "spin-slow":     "spin 3s linear infinite",
      },
      keyframes: {
        fadeIn:      { "0%": { opacity: "0" },                               "100%": { opacity: "1" } },
        slideUp:     { "0%": { opacity: "0", transform: "translateY(24px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        slideInLeft: { "0%": { opacity: "0", transform: "translateX(-24px)" },"100%": { opacity: "1", transform: "translateX(0)" } },
        shimmer:     { "0%": { backgroundPosition: "200% 0" },               "100%": { backgroundPosition: "-200% 0" } },
        float:       { "0%,100%": { transform: "translateY(0)" },             "50%": { transform: "translateY(-8px)" } },
        glowPulse:   { "0%,100%": { opacity: "0.6", transform: "scale(1)" },  "50%": { opacity: "1", transform: "scale(1.05)" } },
      },
      backgroundImage: {
        "glass-gradient": "linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.4) 100%)",
        "glass-overlay": "linear-gradient(135deg, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.2) 100%)",
        "shimmer-gradient": "linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0) 100%)",
      },
      boxShadow: {
        "glass":       "0 8px 32px 0 rgba(31, 38, 135, 0.07)",
        "glass-hover": "0 12px 40px 0 rgba(31, 38, 135, 0.12)",
        "glass-inset": "inset 0 0 0 1px rgba(255, 255, 255, 0.6)",
        "glass-inset-light": "inset 0 0 0 1px rgba(255, 255, 255, 0.8), 0 2px 8px -2px rgba(0,0,0,0.02)",
        "soft-ui":     "0 2px 8px -2px rgba(0,0,0,0.02), 0 4px 16px -4px rgba(0,0,0,0.03), 0 12px 24px -8px rgba(0,0,0,0.04)",
        "soft-ui-hover": "0 4px 12px -2px rgba(0,0,0,0.03), 0 8px 24px -4px rgba(0,0,0,0.04), 0 16px 32px -8px rgba(0,0,0,0.05)",
        "premium-green": "0 4px 12px -2px rgba(34,197,94,0.1), 0 8px 24px -4px rgba(34,197,94,0.2), 0 16px 32px -8px rgba(34,197,94,0.25)",
        "button-hover": "0 6px 16px -2px rgba(34,197,94,0.15), 0 10px 25px -5px rgba(34,197,94,0.3)",
      },
      backdropBlur: {
        "glass": "24px",
        "glass-heavy": "40px",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
        serif: ["var(--font-playfair)", "serif"],
      }
    },
  },
  plugins: [],
};

