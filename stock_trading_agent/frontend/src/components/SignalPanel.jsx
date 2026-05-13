import React from 'react'
import { Zap, AlertCircle, TrendingUp, TrendingDown } from 'lucide-react'
import { getSignalColor, formatConfidence } from '../utils/formatters'

function SignalPanel({ result }) {
  const signal = result?.signal || 'HOLD'
  const confidence = formatConfidence(result?.confidence || 0)
  const signalBgGlass = {
    BUY: 'bg-bullish/5 border-bullish/30',
    SELL: 'bg-bearish/5 border-bearish/30',
    HOLD: 'bg-yellow-500/5 border-yellow-500/30',
  }[signal] || 'bg-gray-500/5 border-gray-500/30'

  const signalGlowClass = {
    BUY: 'glow-bullish',
    SELL: 'glow-bearish',
    HOLD: 'glow-gold',
  }[signal] || ''

  return (
    <div className={`glass-lg border border-gray-700/50 rounded-lg sm:rounded-xl p-4 sm:p-6 md:p-8 fade-in ${signalBgGlass}`}>
      <div className="flex flex-col lg:flex-row items-start gap-4 sm:gap-6 md:gap-8">
        <div className="flex-1 w-full">
          <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
            <div className="p-2 sm:p-3 bg-gradient-to-br from-bullish to-gold rounded-lg flex-shrink-0">
              <Zap size={20} className="sm:w-6 sm:h-6 text-dark-bg" />
            </div>
            <div className="min-w-0">
              <h3 className="text-lg sm:text-2xl font-bold text-white">Trading Signal</h3>
              <p className="text-xs text-gray-400">AI-Powered Analysis</p>
            </div>
          </div>

          <div
            className={`inline-block px-4 sm:px-6 md:px-8 py-3 sm:py-4 rounded-lg sm:rounded-xl border-2 mb-4 sm:mb-6 ${
              signal === 'BUY'
                ? 'border-bullish/50 bg-bullish/10 ' + signalGlowClass
                : signal === 'SELL'
                ? 'border-bearish/50 bg-bearish/10 ' + signalGlowClass
                : 'border-yellow-500/50 bg-yellow-500/10 ' + signalGlowClass
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              {signal === 'BUY' && <TrendingUp size={18} className="sm:w-5 sm:h-5 text-bullish" />}
              {signal === 'SELL' && <TrendingDown size={18} className="sm:w-5 sm:h-5 text-bearish" />}
              <span
                className={`text-xs font-bold uppercase tracking-widest ${
                  signal === 'BUY' ? 'text-bullish' : signal === 'SELL' ? 'text-bearish' : 'text-yellow-400'
                }`}
              >
                Signal
              </span>
            </div>
            <p className={`text-4xl sm:text-5xl font-black ${getSignalColor(signal)}`}>{signal}</p>
          </div>

          <div className="mb-4 sm:mb-6 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs sm:text-sm font-semibold text-gray-300">Confidence Score</span>
              <span className={`text-base sm:text-lg font-bold ${getSignalColor(signal)}`}>{confidence}</span>
            </div>
            <div className="w-full h-2 sm:h-3 bg-dark-card-light rounded-full overflow-hidden border border-gray-700/50">
              <div
                className={`h-full transition-all duration-500 ${
                  signal === 'BUY'
                    ? 'bg-gradient-to-r from-bullish to-bullish-dark'
                    : signal === 'SELL'
                    ? 'bg-gradient-to-r from-bearish to-bearish-dark'
                    : 'bg-gradient-to-r from-yellow-500 to-yellow-400'
                }`}
                style={{ width: `${Math.max(0, Math.min(100, parseFloat(confidence) || 0))}%` }}
              />
            </div>
          </div>

          <div className="p-3 sm:p-4 bg-dark-card-light/50 rounded-lg border border-gray-700/50">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">📊 Analysis</p>
            <p className="text-xs sm:text-sm text-gray-200 leading-relaxed font-medium line-clamp-4 sm:line-clamp-none">
              {result?.reason || 'Analyzing market conditions...'}
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:gap-4 w-full lg:w-64 lg:flex-none">
          <div className="p-3 sm:p-4 glass border border-gray-700/50 rounded-lg">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Trend Strength</p>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-300">Strength</span>
                <span className="text-bullish font-bold">Strong</span>
              </div>
              <div className="w-full h-2 bg-dark-card-light rounded-full overflow-hidden">
                <div className="w-3/4 h-full bg-gradient-to-r from-bullish to-bullish-dark"></div>
              </div>
            </div>
          </div>

          <div className="p-3 sm:p-4 bg-yellow-900/20 border border-yellow-700/40 rounded-lg">
            <div className="flex items-start gap-2 mb-2">
              <AlertCircle size={16} className="text-yellow-400 flex-shrink-0 mt-0.5" />
              <p className="text-xs font-bold text-yellow-300 uppercase tracking-wide">⚠️ Notice</p>
            </div>
            <p className="text-xs text-yellow-100 leading-relaxed">
              Educational analysis only. Use risk management. Never risk more than you can afford to lose.
            </p>
          </div>

          <div className="p-3 sm:p-4 glass border border-gray-700/50 rounded-lg">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Market Bias</p>
            <p className={`text-lg sm:text-xl font-bold ${result?.market_bias === 'BULLISH' ? 'text-bullish' : 'text-bearish'}`}>
              {result?.market_bias || '-'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SignalPanel
