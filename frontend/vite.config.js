import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Get API base URL from environment variable or default to backend
  // In production with Nginx, this should be undefined to use relative paths
  const apiBaseUrl = process.env.VITE_API_BASE_URL || 'http://127.0.0.1:5001';
  
  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0', // Bind to all interfaces to accept connections from host IP
      port: 3000,
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true,
          rewrite: (path) => path, // Keep /api prefix
        },
      },
    },
  };
});

