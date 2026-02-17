import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/prompts': 'http://localhost:8000',
      '/templates': 'http://localhost:8000',
      '/hints': 'http://localhost:8000',
      '/scaffold': 'http://localhost:8000',
      '/providers': 'http://localhost:8000',
    },
  },
})
