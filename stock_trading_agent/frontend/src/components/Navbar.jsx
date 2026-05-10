import React from 'react'
import { Clock, TrendingUp } from 'lucide-react'
import { formatTime } from '../utils/formatters'

function Navbar({ selectedPair, analysisResult }) {
  const currentTime = new Date()
  const isPeakHours = (currentTime.getUTCHours() >= 12 && currentTime.getUTCHours() <= 21)

  return (
    <nav className="glass border-b border-gray-700 px-6 py-4 flex items-center justify-between">
      {/* Left: Logo & Title */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-bullish to-gold flex items-center justify-center">
          <TrendingUp size={24} className="text-dark-bg" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">AI Forex Assistant</h1>
          <p className="text-xs text-gray-400">AI Forex & Commodity Trading Assistant</p>
        </div>
      </div>

      {/* Center: Selected Pair & Status */}
      <div className="flex items-center gap-8">
        <div className="text-center">
          <p className="text-xs text-gray-400 uppercase tracking-wide">Selected Pair</p>
          <p className="text-lg font-semibold text-white">{selectedPair}</p>
        </div>

        {analysisResult && (
          <div className="text-center">
            <p className="text-xs text-gray-400 uppercase tracking-wide">Market Status</p>
            <p className="text-lg font-semibold">
              <span className={analysisResult.latest_price > 0 ? 'text-bullish' : 'text-bearish'}>
                {analysisResult.latest_price.toFixed(5)}
              </span>
            </p>
          </div>
        )}

        <div className="text-center">
          <p className="text-xs text-gray-400 uppercase tracking-wide">Active Session</p>
          <p className="text-lg font-semibold text-gold">
            {analysisResult?.session?.active_session || 'Loading...'}
          </p>
        </div>
      </div>

      {/* Right: UTC Time */}
      <div className="flex items-center gap-2 text-gray-400">
        <Clock size={16} />
        <span className="text-sm">{formatTime(currentTime, true)} UTC</span>
      </div>
    </nav>
  )
}

export default Navbar
