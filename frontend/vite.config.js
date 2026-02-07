import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/predict': 'http://localhost:8000',
      '/history': 'http://localhost:8000',
      '/get_chats': 'http://localhost:8000',
      '/delete_chat': 'http://localhost:8000',
      '/get_insights': 'http://localhost:8000',
    }
  }
})
