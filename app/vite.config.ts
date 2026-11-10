import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// GitHub Pages subpath: https://sagitakdx.github.io/k5-day03-instructor-slides/
export default defineConfig({
  plugins: [react()],
  base: '/k5-day03-instructor-slides/',
})
