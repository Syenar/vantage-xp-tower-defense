import { defineConfig } from 'vite';
import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';

export default defineConfig({
  base: './',
  publicDir: false,
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    target: 'es2022',
  },
  plugins: [{
    name: 'copy-vantage-static-assets',
    closeBundle() {
      const root = process.cwd();
      const dist = resolve(root, 'dist');
      mkdirSync(dist, { recursive: true });
      const assets = resolve(root, 'assets');
      if (existsSync(assets)) cpSync(assets, resolve(dist, 'assets'), { recursive: true });
      for (const file of ['manifest.webmanifest']) {
        const src = resolve(root, file);
        if (existsSync(src)) cpSync(src, resolve(dist, file));
      }
    },
  }],
});
