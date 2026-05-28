import { defineConfig } from "vite"
import { VitePWA } from "vite-plugin-pwa"

export default defineConfig({
  base: "/",
  plugins: [
    VitePWA({
      registerType: "autoUpdate",
      srcDir: "public",
      filename: "service-worker.js",
      includeAssets: ["icons/*.svg", "icons/*.png"],
      manifest: {
        name: "TikTokMall 商城",
        short_name: "TikTokMall",
        description: "TikTokMall 跨境电商 - 手机商城与商家管理",
        theme_color: "#1989fa",
        background_color: "#ffffff",
        display: "standalone",
        scope: "/",
        start_url: "/",
        orientation: "portrait-primary",
        categories: ["shopping", "business"],
        icons: [
          { src: "icons/icon-192.svg", sizes: "192x192", type: "image/svg+xml" },
          { src: "icons/icon-512.svg", sizes: "512x512", type: "image/svg+xml" },
          { src: "icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any maskable" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any maskable" }
        ]
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,svg,png,ico}"],
        runtimeCaching: [
          {
            urlPattern: /^https?:\/\/.*\/api\/.*/i,
            handler: "NetworkFirst",
            options: { cacheName: "api-cache", expiration: { maxEntries: 100, maxAgeSeconds: 86400 } }
          },
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
            handler: "CacheFirst",
            options: { cacheName: "images", expiration: { maxEntries: 200, maxAgeSeconds: 2592000 } }
          }
        ]
      }
    })
  ],
  server: {
    port: 5175,
    host: "0.0.0.0",
    proxy: {
      "/api": { target: "http://45.192.97.37:8080", changeOrigin: true },
      "/wap": { target: "http://45.192.97.37", changeOrigin: true },
      "/www": { target: "http://45.192.97.37", changeOrigin: true }
    }
  }
})
