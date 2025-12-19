import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Get API base URL from environment variable or default
  const apiBaseUrl = process.env.VITE_API_BASE_URL || 'http://localhost:5000';
  
  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0', // Bind to all interfaces to accept connections from host IP
      port: 3000,
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true,
        },
      },
    },
  };
});

