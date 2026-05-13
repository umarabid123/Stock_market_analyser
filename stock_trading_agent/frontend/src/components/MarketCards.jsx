import React from 'react'
import {
  DollarSign,
  TrendingUp,
  Target,
  Zap,
} from 'lucide-react'
import {
  formatPrice,
  formatConfidence,
  getSignalColor,
  getBiasColor,
  getSignalBgColor,
} from '../utils/formatters'

function MarketCards({ result }) {
  const cards = [
    {
      title: 'Current Price',
      value: formatPrice(result?.latest_price),
      icon: DollarSign,
      color: 'from-blue-600 to-blue-400',
      detail: result?.symbol || '-',
    },
    {
      title: 'Signal',
      value: result?.signal || '-',
      icon: Target,
      color: 'from-purple-600 to-purple-400',
      className: getSignalColor(result?.signal),
      bgColor: getSignalBgColor(result?.signal),
      detail: formatConfidence(result?.confidence) + ' confidence',
    },
    {
      title: 'Market Bias',
      value: result?.market_bias || '-',
      icon: TrendingUp,
      color: 'from-emerald-600 to-emerald-400',
      className: getBiasColor(result?.market_bias),
      detail: 'Multi-timeframe',
    },
    {
      title: 'Volatility',
      value: result?.session?.volatility ?? '-',
      icon: Zap,
      color: 'from-orange-600 to-orange-400',
      detail: result?.session?.active_session || '-',
    },
  ]

  const signal = result?.signal || 'HOLD'
  const signalGlow = {
    'BUY': 'glow-bullish',
    'SELL': 'glow-bearish',
    'HOLD': 'glow-gold',
  }[signal] || 'glow-accent'

  return (
    <>
      {cards.map((card, idx) => {
        const Icon = card.icon
        const cardGlow = card.title === 'Signal' ? signalGlow : ''
        return (
          <div
            key={idx}
            className={`glass-lg border border-gray-700/50 p-3 sm:p-4 md:p-5 rounded-lg sm:rounded-xl hover-glow transition-smooth fade-in ${
              card.bgColor ? `${card.bgColor}` : ''
            } ${cardGlow}`}
            style={{ animationDelay: `${idx * 0.1}s` }}
          >
            <div className="flex items-start justify-between mb-3 sm:mb-4">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-widest line-clamp-2">
                {card.title}
              </span>
              <div className="p-1.5 sm:p-2 bg-gradient-to-br from-bullish to-gold rounded-lg flex-shrink-0">
                <Icon size={14} className="sm:w-4 sm:h-4 text-dark-bg" />
              </div>
            </div>

            <p className={`text-2xl sm:text-3xl font-bold mb-2 break-words ${card.className || 'text-white'}`}>
              {card.value}
            </p>

            <p className="text-xs text-gray-400 font-medium truncate">{card.detail}</p>
          </div>
        )
      })}
    </>
  )
}

export default MarketCards
