import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
// eslint-disable-next-line no-undef
const CORE_API_TARGET = process.env.VITE_CORE_API_TARGET || 'http://127.0.0.1:5001'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    },
    dedupe: ['three', 'react', 'react-dom']
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    allowedHosts: true,
    cors: true,
    hmr: true,
    proxy: {
      '/api': {
        target: CORE_API_TARGET,
        changeOrigin: true,
        timeout: 60000,
        proxyTimeout: 60000,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
