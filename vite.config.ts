import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const isVercel = process.env.VERCEL === '1';

export default defineConfig(({ command }) => ({
  // Local development and Vercel run at the origin root. GitHub Pages builds
  // retain the repository subpath.
  base: command === 'serve' || isVercel ? '/' : '/MirrorME/',
  server: {
    port: 3000,
    host: '0.0.0.0',
  },
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
}));
