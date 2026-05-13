import React, { useState, useEffect } from 'react'
import { Clock, Activity, Zap, BarChart3, TrendingUp, TrendingDown } from 'lucide-react'

function Navbar({ selectedPair, analysisResult, loading }) {
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

  const isLoading = loading && !analysisResult

  return (
    <nav className="glass-lg border-b border-gray-700/50 px-4 sm:px-6 lg:px-8 py-3 flex flex-col gap-3 sm:gap-4 backdrop-blur-md">
      {/* Left: Logo & App Title */}
      <div className="flex items-center justify-between gap-3 w-full">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-bullish to-gold flex items-center justify-center hover-glow cursor-pointer">
            <BarChart3 size={24} className="text-dark-bg" />
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-bold text-white tracking-tight whitespace-nowrap">
              AI FX Trading
            </h1>
            <p className="text-xs text-gray-400">Real-time Market Analysis</p>
          </div>
        </div>

        <div className="text-[10px] text-gray-400 uppercase tracking-widest font-semibold">Market Terminal</div>
      </div>

      {/* Center: Current Asset & Price Info */}
      <div className="nav-row nav-scroll scrollbar-hide lg:justify-center lg:overflow-visible">
          {/* Selected Pair */}
          <div className="glass nav-card border border-gray-600/50 px-4 py-2 rounded-lg min-w-[140px] sm:min-w-[150px]">
            <p className="text-[10px] text-gray-400 uppercase tracking-widest font-medium">Trading Pair</p>
            <p className="text-base sm:text-lg font-semibold text-white">{selectedPair}</p>
          </div>

          {/* Live Price */}
          {isLoading && (
            <div className="glass nav-card border border-gray-600/50 px-4 py-2 rounded-lg min-w-[160px] sm:min-w-[170px]">
              <div className="skeleton h-3 w-20 mb-2"></div>
              <div className="skeleton h-6 w-28"></div>
            </div>
          )}

          {analysisResult && (
            <div className="glass nav-card border border-gray-600/50 px-4 py-2 rounded-lg min-w-[160px] sm:min-w-[170px]">
              <p className="text-[10px] text-gray-400 uppercase tracking-widest font-medium">Live Price</p>
              <div className="flex items-center gap-2">
                <p className={`text-base sm:text-lg font-semibold ${analysisResult.latest_price > 1.1 ? 'text-bullish' : 'text-bearish'}`}>
                  {analysisResult.latest_price?.toFixed(5)}
                </p>
                <div className={`flex items-center gap-0.5 ${priceChange > 0 ? 'text-bullish' : 'text-bearish'}`}>
                  {priceChange > 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                  <span className="text-[11px] font-semibold">{Math.abs(priceChange).toFixed(2)}%</span>
                </div>
              </div>
            </div>
          )}

          {/* Active Session */}
          {isLoading && (
            <div className="glass nav-card border border-gold/30 px-4 py-2 rounded-lg glow-gold min-w-[150px] sm:min-w-[160px]">
              <div className="skeleton h-3 w-16 mb-2"></div>
              <div className="skeleton h-6 w-32"></div>
            </div>
          )}

          {analysisResult?.session && (
            <div className="glass nav-card border border-gold/30 px-4 py-2 rounded-lg glow-gold min-w-[150px] sm:min-w-[160px]">
              <p className="text-[10px] text-gray-400 uppercase tracking-widest font-medium">Session</p>
              <p className="text-sm sm:text-base font-semibold text-gold">{analysisResult.session.active_session}</p>
            </div>
          )}

          {/* Market Bias */}
          {isLoading && (
            <div className="glass nav-card border px-4 py-2 rounded-lg min-w-[130px] sm:min-w-[140px] border-yellow-400/30">
              <div className="skeleton h-3 w-14 mb-2"></div>
              <div className="skeleton h-6 w-20"></div>
            </div>
          )}

          {analysisResult && (
            <div className={`glass nav-card border px-4 py-2 rounded-lg min-w-[130px] sm:min-w-[140px] ${signal === 'BUY' ? 'border-bullish/30 glow-bullish' : signal === 'SELL' ? 'border-bearish/30 glow-bearish' : 'border-yellow-400/30'}`}>
              <p className="text-[10px] text-gray-400 uppercase tracking-widest font-medium">Signal</p>
              <p className={`text-sm sm:text-base font-semibold signal-${signal.toLowerCase()}`}>{signal}</p>
            </div>
          )}
      </div>

      {/* Right: Status Indicators */}
      <div className="nav-row nav-scroll scrollbar-hide lg:justify-end lg:overflow-visible">
        {/* LIVE Badge */}
        <div className="nav-chip flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-bearish live-pulse"></div>
          <span className="text-[10px] font-bold text-bearish uppercase tracking-widest">Live</span>
        </div>

        {/* UTC Time */}
        <div className="nav-chip glass border border-gray-600/50 px-3 py-1.5 rounded-lg flex items-center gap-2">
          <Clock size={14} className="text-accent" />
          <span className="text-xs font-mono font-medium text-gray-300">{utcTime}</span>
        </div>

        {/* Peak Hours Indicator */}
        {isPeakHours && (
          <div className="nav-chip glass border border-bullish/30 px-3 py-1.5 rounded-lg flex items-center gap-2 glow-bullish">
            <Zap size={14} className="text-bullish" />
            <span className="text-[10px] font-bold text-bullish uppercase">Peak Hours</span>
          </div>
        )}

        {/* Data Provider */}
        <div className="nav-chip glass border border-gray-600/50 px-3 py-1.5 rounded-lg">
          <p className="text-[10px] font-mono text-gray-400">
            <Activity size={12} className="inline mr-1" />
            Real-time
          </p>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
