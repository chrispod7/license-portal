import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // In dev, forward API calls to FastAPI so the browser sees one origin.
    proxy: { "/api": process.env.VITE_API_PROXY || "http://localhost:8000" },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/setupTests.js",
  },
});
