import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],

  // Use relative paths for Electron
  base: './',

  // Build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
      output: {
        manualChunks: {
          'monaco-editor': ['monaco-editor'],
        },
      },
    },
    // Ensure Monaco Editor is bundled locally
    commonjsOptions: {
      include: [/monaco-editor/, /node_modules/],
    },
  },

  // Optimize Monaco Editor for local use
  optimizeDeps: {
    include: ['monaco-editor'],
  },

  // Development server
  server: {
    port: 5173,
    strictPort: true,
    host: 'localhost',
  },

  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@services': resolve(__dirname, 'src/services'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@assets': resolve(__dirname, 'src/assets'),
    },
  },

  // CSS configuration
  css: {
    modules: {
      localsConvention: 'camelCase',
    },
  },

  // Define environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
});
