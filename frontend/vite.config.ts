import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    fs: {
      allow: [resolve(dirname(fileURLToPath(import.meta.url)), '..')]
    }
  }
});
