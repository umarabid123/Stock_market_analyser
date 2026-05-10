module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0f172a',
        'dark-card': '#1e293b',
        'bullish': '#00ff88',
        'bearish': '#ff3333',
        'gold': '#fbbf24',
        'neutral': '#64748b',
      },
      backdropFilter: {
        'glass': 'backdrop-filter: blur(10px)',
      },
    },
  },
  plugins: [],
}
