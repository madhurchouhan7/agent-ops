/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#030303',
        foreground: '#ededed',
        card: '#0a0a0a',
        'card-foreground': '#ededed',
        popover: '#0a0a0a',
        'popover-foreground': '#ededed',
        primary: '#ffffff',
        'primary-foreground': '#030303',
        secondary: '#18181b',
        'secondary-foreground': '#fafafa',
        muted: '#18181b',
        'muted-foreground': '#a1a1aa',
        accent: '#27272a',
        'accent-foreground': '#fafafa',
        border: 'rgba(255, 255, 255, 0.1)',
        ring: '#71717a',
      },
      fontFamily: {
        sans: ['Geist', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['Geist Mono', 'SF Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'marquee': 'marquee 30s linear infinite',
        'marquee-reverse': 'marquee-reverse 30s linear infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        'marquee-reverse': {
          '0%': { transform: 'translateX(-50%)' },
          '100%': { transform: 'translateX(0%)' },
        },
      },
    },
  },
  plugins: [],
}
