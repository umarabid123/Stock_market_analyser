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
      value: formatPrice(result.latest_price),
      icon: DollarSign,
      color: 'from-blue-600 to-blue-400',
      detail: result.symbol,
    },
    {
      title: 'Signal',
      value: result.signal,
      icon: Target,
      color: 'from-purple-600 to-purple-400',
      className: getSignalColor(result.signal),
      bgColor: getSignalBgColor(result.signal),
      detail: formatConfidence(result.confidence) + ' confidence',
    },
    {
      title: 'Market Bias',
      value: result.market_bias,
      icon: TrendingUp,
      color: 'from-emerald-600 to-emerald-400',
      className: getBiasColor(result.market_bias),
      detail: 'Multi-timeframe',
    },
    {
      title: 'Volatility',
      value: result.session.volatility,
      icon: Zap,
      color: 'from-orange-600 to-orange-400',
      detail: result.session.active_session,
    },
  ]

  return (
    <>
      {cards.map((card, idx) => {
        const Icon = card.icon
        return (
          <div
            key={idx}
            className={`glass border border-gray-700 p-4 rounded-lg hover:border-gray-600 transition ${
              card.bgColor || ''
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                {card.title}
              </span>
              <Icon size={18} className="text-gray-500" />
            </div>

            <p className={`text-2xl font-bold mb-1 ${card.className || 'text-white'}`}>
              {card.value}
            </p>

            <p className="text-xs text-gray-500">{card.detail}</p>
          </div>
        )
      })}
    </>
  )
}

export default MarketCards
