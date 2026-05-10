import React from 'react'
import { Shield, Target, TrendingUp } from 'lucide-react'
import { formatPrice } from '../utils/formatters'

function RiskPanel({ result }) {
  const { entry_price, stop_loss, take_profit, risk_reward_ratio } = result.risk

  return (
    <div className="glass border border-gray-700 rounded-lg p-6 space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Shield size={20} className="text-gold" />
        <h3 className="text-lg font-semibold">Risk Management</h3>
      </div>

      {/* Entry Price */}
      <div className="p-3 bg-dark-card rounded-lg border border-gray-700">
        <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Entry Price</p>
        <p className="text-xl font-semibold text-white">
          {formatPrice(entry_price)}
        </p>
      </div>

      {/* Stop Loss */}
      <div className="p-3 bg-dark-card rounded-lg border border-bearish/30">
        <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Stop Loss</p>
        <p className="text-xl font-semibold text-bearish">
          {stop_loss ? formatPrice(stop_loss) : 'N/A'}
        </p>
        {stop_loss && (
          <p className="text-xs text-gray-500 mt-1">
            {Math.abs(stop_loss - entry_price).toFixed(5)} risk
          </p>
        )}
      </div>

      {/* Take Profit */}
      <div className="p-3 bg-dark-card rounded-lg border border-bullish/30">
        <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Take Profit</p>
        <p className="text-xl font-semibold text-bullish">
          {take_profit ? formatPrice(take_profit) : 'N/A'}
        </p>
        {take_profit && (
          <p className="text-xs text-gray-500 mt-1">
            {Math.abs(take_profit - entry_price).toFixed(5)} gain
          </p>
        )}
      </div>

      {/* Risk/Reward Ratio */}
      <div className="p-3 bg-dark-card rounded-lg border border-gray-700">
        <p className="text-xs text-gray-400 uppercase tracking-wide mb-1 flex items-center gap-1">
          <TrendingUp size={14} />
          Risk/Reward Ratio
        </p>
        <p className="text-xl font-semibold text-gold">
          {risk_reward_ratio ? `${risk_reward_ratio.toFixed(2)}:1` : 'N/A'}
        </p>
      </div>

      {/* Support/Resistance */}
      <div className="grid grid-cols-2 gap-2 mt-4 pt-4 border-t border-gray-700">
        <div>
          <p className="text-xs text-gray-400 uppercase mb-1">Support</p>
          <p className="text-sm font-semibold text-gray-300">
            {result.support_zone && result.support_zone.length > 0
              ? result.support_zone[0].toFixed(5)
              : '-'}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase mb-1">Resistance</p>
          <p className="text-sm font-semibold text-gray-300">
            {result.resistance_zone && result.resistance_zone.length > 0
              ? result.resistance_zone[1].toFixed(5)
              : '-'}
          </p>
        </div>
      </div>
    </div>
  )
}

export default RiskPanel
