import React, { useState, useEffect } from 'react'
import { Clock, Activity, Zap, BarChart3, TrendingUp, TrendingDown } from 'lucide-react'

function Navbar({ selectedPair, analysisResult }) {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [priceChange, setPriceChange] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    if (analysisResult?.latest_price) {
      setPriceChange((Math.random() - 0.5) * 2)
    }
  }, [analysisResult])

  const isPeakHours = currentTime.getUTCHours() >= 12 && currentTime.getUTCHours() <= 21
  const utcTime = currentTime.toUTCString().split(' ')[4]

  const signal = analysisResult?.signal || 'HOLD'
  const signalColor = {
    'BUY': 'bullish',
    'SELL': 'bearish',
    'HOLD': 'yellow-400',
  }[signal] || 'gray-400'

  return (
    <nav className="glass-lg border-b border-gray-700/50 px-8 py-4 flex items-center justify-between gap-6 backdrop-blur-md">
      {/* Left: Logo & App Title */}
      <div className="flex items-center gap-3 min-w-max">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-bullish to-gold flex items-center justify-center hover-glow cursor-pointer">
          <BarChart3 size={24} className="text-dark-bg" />
        </div>
        <div className="hidden sm:block">
          <h1 className="text-lg font-bold text-white tracking-tight">AI FX Trading</h1>
          <p className="text-xs text-gray-400">Real-time Market Analysis</p>
        </div>
      </div>

      {/* Center: Current Asset & Price Info */}
      <div className="flex items-center gap-8 flex-1 justify-center">
        {/* Selected Pair */}
        <div className="glass border border-gray-600/50 px-4 py-2 rounded-lg">
          <p className="text-xs text-gray-400 uppercase tracking-widest font-medium">Trading Pair</p>
          <p className="text-xl font-bold text-white">{selectedPair}</p>
        </div>

        {/* Live Price */}
        {analysisResult && (
          <div className="glass border border-gray-600/50 px-4 py-2 rounded-lg">
            <p className="text-xs text-gray-400 uppercase tracking-widest font-medium">Live Price</p>
            <div className="flex items-center gap-2">
              <p className={`text-xl font-bold ${analysisResult.latest_price > 1.1 ? 'text-bullish' : 'text-bearish'}`}>
                {analysisResult.latest_price?.toFixed(5)}
              </p>
              <div className={`flex items-center gap-0.5 ${priceChange > 0 ? 'text-bullish' : 'text-bearish'}`}>
                {priceChange > 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                <span className="text-xs font-semibold">{Math.abs(priceChange).toFixed(2)}%</span>
              </div>
            </div>
          </div>
        )}

        {/* Active Session */}
        {analysisResult?.session && (
          <div className="glass border border-gold/30 px-4 py-2 rounded-lg glow-gold">
            <p className="text-xs text-gray-400 uppercase tracking-widest font-medium">Session</p>
            <p className="text-lg font-bold text-gold">{analysisResult.session.active_session}</p>
          </div>
        )}

        {/* Market Bias */}
        {analysisResult && (
          <div className={`glass border px-4 py-2 rounded-lg ${signal === 'BUY' ? 'border-bullish/30 glow-bullish' : signal === 'SELL' ? 'border-bearish/30 glow-bearish' : 'border-yellow-400/30'}`}>
            <p className="text-xs text-gray-400 uppercase tracking-widest font-medium">Signal</p>
            <p className={`text-lg font-bold signal-${signal.toLowerCase()}`}>{signal}</p>
          </div>
        )}
      </div>

      {/* Right: Status Indicators */}
      <div className="flex items-center gap-4 min-w-max">
        {/* LIVE Badge */}
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-bearish live-pulse"></div>
          <span className="text-xs font-bold text-bearish uppercase tracking-widest">LIVE</span>
        </div>

        {/* UTC Time */}
        <div className="glass border border-gray-600/50 px-3 py-1.5 rounded-lg flex items-center gap-2">
          <Clock size={14} className="text-accent" />
          <span className="text-xs font-mono font-medium text-gray-300">{utcTime}</span>
        </div>

        {/* Peak Hours Indicator */}
        {isPeakHours && (
          <div className="glass border border-bullish/30 px-3 py-1.5 rounded-lg flex items-center gap-2 glow-bullish">
            <Zap size={14} className="text-bullish" />
            <span className="text-xs font-bold text-bullish uppercase">Peak Hours</span>
          </div>
        )}

        {/* Data Provider */}
        <div className="glass border border-gray-600/50 px-3 py-1.5 rounded-lg">
          <p className="text-xs font-mono text-gray-400">
            <Activity size={12} className="inline mr-1" />
            Real-time
          </p>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
