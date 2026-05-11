import React from 'react'
import { Shield, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'
import { formatPrice } from '../utils/formatters'

function RiskPanel({ result }) {
  const { entry_price, stop_loss, take_profit, risk_reward_ratio } = result?.risk || {}
  const hasRisk = stop_loss || take_profit

  return (
    <div className="glass-lg border border-gray-700/50 rounded-xl p-6 space-y-4 fade-in">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-gradient-to-br from-gold to-yellow-500 rounded-lg">
          <Shield size={22} className="text-dark-bg" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white">Risk Management</h3>
          <p className="text-xs text-gray-400">Capital Protection</p>
        </div>
      </div>

      <div className="p-4 bg-dark-card-light/50 border border-accent/30 rounded-lg hover-glow transition-smooth">
        <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Entry Price</p>
        <p className="text-2xl font-bold text-accent">{formatPrice(entry_price)}</p>
      </div>

      <div
        className={`p-4 border rounded-lg hover-glow-bearish transition-smooth ${
          stop_loss ? 'bg-bearish/5 border-bearish/40' : 'bg-gray-900/30 border-gray-700/30'
        }`}
      >
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Stop Loss</p>
          <TrendingDown size={16} className="text-bearish" />
        </div>
        <p className="text-2xl font-bold text-bearish mb-1">{stop_loss ? formatPrice(stop_loss) : 'Not Set'}</p>
        {stop_loss && entry_price && (
          <p className="text-xs text-gray-400 font-medium">
            {(Math.abs(stop_loss - entry_price)).toFixed(5)} risk exposure
          </p>
        )}
      </div>

      <div
        className={`p-4 border rounded-lg hover-glow transition-smooth ${
          take_profit ? 'bg-bullish/5 border-bullish/40' : 'bg-gray-900/30 border-gray-700/30'
        }`}
      >
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Take Profit</p>
          <TrendingUp size={16} className="text-bullish" />
        </div>
        <p className="text-2xl font-bold text-bullish mb-1">{take_profit ? formatPrice(take_profit) : 'Not Set'}</p>
        {take_profit && entry_price && (
          <p className="text-xs text-gray-400 font-medium">
            {(Math.abs(take_profit - entry_price)).toFixed(5)} profit target
          </p>
        )}
      </div>

      <div className="p-4 bg-gold/5 border border-gold/40 rounded-lg">
        <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Risk/Reward Ratio</p>
        <p className="text-2xl font-bold text-gold">{risk_reward_ratio ? `${risk_reward_ratio.toFixed(2)}:1` : 'N/A'}</p>
      </div>

      <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-gray-700/50">
        <div className="p-3 bg-dark-card-light/50 border border-gray-700/30 rounded-lg">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Support</p>
          <p className="text-lg font-bold text-accent">
            {Array.isArray(result?.support_zone) && result.support_zone.length > 0
              ? result.support_zone[0].toFixed(5)
              : '-'}
          </p>
        </div>
        <div className="p-3 bg-dark-card-light/50 border border-gray-700/30 rounded-lg">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Resistance</p>
          <p className="text-lg font-bold text-accent">
            {Array.isArray(result?.resistance_zone) && result.resistance_zone.length > 0
              ? result.resistance_zone[0].toFixed(5)
              : '-'}
          </p>
        </div>
      </div>

      {!hasRisk && (
        <div className="p-3 bg-yellow-900/20 border border-yellow-700/40 rounded-lg flex items-start gap-2">
          <AlertTriangle size={16} className="text-yellow-400 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-yellow-200 font-medium">No stop loss/take profit set. Use risk management.</p>
        </div>
      )}
    </div>
  )
}

export default RiskPanel
