import { defineConfig } from "vite"

export default defineConfig({
  base: "/",
  plugins: [],
  server: {
    port: 5175,
    host: "0.0.0.0",
    proxy: {
      "/api": { target: "http://47.91.170.222:8080", changeOrigin: true },
      "/wap": { target: "http://47.91.170.222", changeOrigin: true },
      "/www": { target: "http://47.91.170.222", changeOrigin: true }
    }
  }
})
