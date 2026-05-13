module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0a0e27',
        'dark-card': '#1a1f3a',
        'dark-card-light': '#252e48',
        'bullish': '#00ff88',
        'bullish-dark': '#00cc6a',
        'bearish': '#ff3333',
        'bearish-dark': '#cc2626',
        'gold': '#fbbf24',
        'gold-dark': '#d99f1a',
        'neutral': '#64748b',
        'accent': '#60a5fa',
        'accent-dark': '#3b82f6',
      },
      backgroundColor: {
        'glass': 'rgba(30, 41, 59, 0.4)',
        'glass-dark': 'rgba(10, 14, 39, 0.6)',
      },
      backdropFilter: {
        'glass': 'blur(10px)',
        'glass-md': 'blur(15px)',
        'glass-lg': 'blur(20px)',
      },
      boxShadow: {
        'glow-bullish': '0 0 20px rgba(0, 255, 136, 0.3)',
        'glow-bearish': '0 0 20px rgba(255, 51, 51, 0.3)',
        'glow-gold': '0 0 20px rgba(251, 191, 36, 0.3)',
        'glow-accent': '0 0 20px rgba(96, 165, 250, 0.3)',
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-soft': 'pulse-soft 3s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 255, 136, 0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(0, 255, 136, 0.6)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '0.8' },
          '50%': { opacity: '1' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        'glow-pulse': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.7', transform: 'scale(1.05)' },
        },
      },
      gradients: {
        'dark-card': 'linear-gradient(135deg, #1a1f3a 0%, #252e48 100%)',
        'bullish-grad': 'linear-gradient(135deg, #00ff88 0%, #00cc6a 100%)',
        'bearish-grad': 'linear-gradient(135deg, #ff3333 0%, #cc2626 100%)',
      },
      fontFamily: {
        sans: ['Space Grotesk', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
