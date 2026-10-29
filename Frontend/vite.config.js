import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],

  server: {
    proxy: {
      '/mock-irctc': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/hello': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },

  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        booking: resolve(__dirname, 'booking.html'),
        confirm: resolve(__dirname, 'confirm.html'),
        dashboard: resolve(__dirname, 'dashboard.html'),
        passenger: resolve(__dirname, 'passenger.html'),
        payment: resolve(__dirname, 'payment.html'),
        preferences: resolve(__dirname, 'preferences.html'),
        status: resolve(__dirname, 'status.html'),
        ticket: resolve(__dirname, 'ticket.html'),
      },
    },
  },
})
