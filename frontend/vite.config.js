import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  base: process.env.ELECTRON_BUILD === 'true' ? './' : '/ai/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      // Agent backend — /ai/api/* → :9000 (strip /ai/api prefix, matches Nginx)
      '/ai/api': {
        target: 'http://localhost:9000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai\/api/, '')
      },
      // Java backend — /api/* → :8080 (keep /api prefix, Java expects it)
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
      // Java merchant — /merchant/* → :8080
      '/merchant': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
,
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-ui': ['element-plus'],
          'vendor-3d': ['three'],
          'vendor-charts': ['echarts'],
        }
      }
    }
  }
})