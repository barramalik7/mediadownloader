import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import tsConfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '')
    const backendTarget = env.VITE_BACKEND_TARGET || 'http://127.0.0.1:8000'

    return {
        plugins: [
            tsConfigPaths(),
            tanstackStart(),
            // React's vite plugin must come after TanStack Start's plugin
            react(),
        ],
        server: {
            port: 5173,
            proxy: {
                '/api': {
                    target: backendTarget,
                    changeOrigin: true,
                }
            }
        }
    }
})
