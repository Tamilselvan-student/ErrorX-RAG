/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Developer-focused dark theme palette.
        bg: {
          950: "#0a0e1a",
          900: "#0f1524",
          850: "#121a2e",
          800: "#172031",
          700: "#1e293b",
        },
        accent: {
          400: "#22d3ee",
          500: "#06b6d4",
          600: "#0891b2",
        },
        success: "#34d399",
        warn: "#fbbf24",
        danger: "#f87171",
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "'Fira Code'", "Consolas", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 24px rgba(6, 182, 212, 0.18)",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};