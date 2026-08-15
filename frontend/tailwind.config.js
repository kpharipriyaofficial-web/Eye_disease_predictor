/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        void: "#06090D",
        surface: "#0D1420",
        "surface-raised": "#131C2B",
        "surface-hover": "#182337",
        "accent-cyan": "#4FD8F0",
        "accent-blue": "#3B6FE0",
        "text-hi": "#EAF2F7",
        "text-mid": "#8FA3B3",
        "text-dim": "#5B6B7B",
        "signal-amber": "#F0A64F",
        "signal-red": "#F0604F",
        "signal-green": "#4FF0A0",
        "line": "rgba(79, 216, 240, 0.14)",
      },
      fontFamily: {
        display: ['"Space Grotesk"', "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      boxShadow: {
        glow: "0 0 60px rgba(79, 216, 240, 0.12)",
        "glow-sm": "0 0 24px rgba(79, 216, 240, 0.18)",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(-110%)" },
          "50%": { transform: "translateY(110%)" },
          "100%": { transform: "translateY(-110%)" },
        },
        "pulse-ring": {
          "0%": { transform: "scale(0.85)", opacity: "0.7" },
          "70%": { transform: "scale(1.5)", opacity: "0" },
          "100%": { opacity: "0" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        scan: "scan 3.2s ease-in-out infinite",
        "pulse-ring": "pulse-ring 2.2s cubic-bezier(0.4,0,0.6,1) infinite",
        "fade-up": "fade-up 0.4s ease-out both",
      },
    },
  },
  plugins: [],
};
