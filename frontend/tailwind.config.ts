import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#09111f",
          900: "#0f172a",
          800: "#1e293b",
          700: "#334155"
        },
        desk: {
          teal: "#0f766e",
          gold: "#b7791f",
          red: "#b91c1c"
        }
      },
      boxShadow: {
        panel: "0 18px 50px rgba(2, 6, 23, 0.24)"
      }
    }
  },
  plugins: []
};

export default config;

