/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        charcoal: {
          950: '#0d0e12',
          900: '#13141a',
          850: '#181a22',
          800: '#20232e',
          700: '#2c3140',
          600: '#3c4357',
          500: '#525b74',
          400: '#7e879f',
          300: '#a7b0c7',
          200: '#d0d6e5',
          100: '#eef1f8',
        },
        gold: {
          light: '#e0c282',
          DEFAULT: '#c5a059',
          dark: '#a27e38',
          subtle: 'rgba(197, 160, 89, 0.12)',
          border: 'rgba(197, 160, 89, 0.3)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
