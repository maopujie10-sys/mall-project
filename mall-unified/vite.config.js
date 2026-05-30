import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  base: '/',
  plugins: [vue()],
  css: {
    preprocessorOptions: {
      scss: { additionalData: '$primary-color: #1552F0; $border-color: #eeeeee; $background-color: #f5f6fa; $text-color-dark: #1e293b; $text-color-default: #64748b; $text-color-light: #94a3b8;' }
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': { target: 'http://localhost:8080', changeOrigin: true },
      '/admin': { target: 'http://localhost:8080', changeOrigin: true },
      '/merchant': { target: 'http://localhost:8080', changeOrigin: true }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      // merchant-h5 老引用兼容
      '~': path.resolve(__dirname),
      '@/components': path.resolve(__dirname, 'src/views/merchant-h5/components'),
      '@/views': path.resolve(__dirname, 'src/views'),
      'vue-i18n': 'vue-i18n/dist/vue-i18n.esm-bundler.js',
    }
  },
  build: {
    target: 'es2015',
    outDir: 'dist',
    assetsDir: 'static',
    rollupOptions: {
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]',
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-ui': ['element-plus'],
          'vendor-vant': ['vant'],
          'vendor-charts': ['echarts'],
        }
      }
    }
  }
})
