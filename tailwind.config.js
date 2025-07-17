/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Liberation System Dark Neon Theme
        primary: {
          50: '#e6ffff',
          100: '#b3ffff',
          200: '#80ffff',
          300: '#4dffff',
          400: '#1affff',
          500: '#00ffff', // Main cyan
          600: '#00cccc',
          700: '#009999',
          800: '#006666',
          900: '#003333',
        },
        secondary: {
          50: '#ffe6ff',
          100: '#ffb3ff',
          200: '#ff80ff',
          300: '#ff4dff',
          400: '#ff1aff',
          500: '#ff00ff', // Main magenta
          600: '#cc00cc',
          700: '#990099',
          800: '#660066',
          900: '#330033',
        },
        accent: {
          50: '#fffff0',
          100: '#ffffcc',
          200: '#ffff99',
          300: '#ffff66',
          400: '#ffff33',
          500: '#ffff00', // Main yellow
          600: '#cccc00',
          700: '#999900',
          800: '#666600',
          900: '#333300',
        },
        dark: {
          50: '#1a1a1a',
          100: '#0d0d0d',
          200: '#000000', // Main black
          300: '#000000',
          400: '#000000',
          500: '#000000',
          600: '#000000',
          700: '#000000',
          800: '#000000',
          900: '#000000',
        },
        surface: {
          50: '#333333',
          100: '#2a2a2a',
          200: '#1a1a1a', // Main surface
          300: '#0d0d0d',
          400: '#000000',
          500: '#000000',
          600: '#000000',
          700: '#000000',
          800: '#000000',
          900: '#000000',
        },
        success: '#00ff00',
        warning: '#ff8800',
        error: '#ff0000',
      },
      backgroundImage: {
        'gradient-neon': 'linear-gradient(45deg, #00ffff, #ff00ff)',
        'gradient-dark': 'linear-gradient(135deg, #000000, #1a1a1a)',
        'gradient-surface': 'linear-gradient(180deg, #1a1a1a, #0d0d0d)',
      },
      fontFamily: {
        mono: ['Courier New', 'monospace'],
        system: ['system-ui', 'sans-serif'],
      },
      boxShadow: {
        'neon': '0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff',
        'neon-pink': '0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 30px #ff00ff',
        'neon-yellow': '0 0 10px #ffff00, 0 0 20px #ffff00, 0 0 30px #ffff00',
      },
      animation: {
        'pulse-neon': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
      },
      keyframes: {
        glow: {
          '0%': { textShadow: '0 0 20px #00ffff' },
          '100%': { textShadow: '0 0 30px #00ffff, 0 0 40px #00ffff' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
