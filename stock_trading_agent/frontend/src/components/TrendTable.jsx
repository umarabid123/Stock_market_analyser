import React from 'react'
import { BarChart2 } from 'lucide-react'
import { getTrendColor } from '../utils/formatters'

function TrendTable({ result }) {
  const trends = [
    { name: '5 Min', value: result.trends?.['5m'] || 'NEUTRAL' },
    { name: '15 Min', value: result.trends?.['15m'] || 'NEUTRAL' },
    { name: '1 Hour', value: result.trends?.['1h'] || 'NEUTRAL' },
    { name: '4 Hour', value: result.trends?.['4h'] || 'NEUTRAL' },
    { name: '1 Day', value: result.trends?.['1d'] || 'NEUTRAL' },
  ]
  const trendStrength = typeof result.trend_strength === 'number' ? result.trend_strength : 0

  return (
    <div className="glass-lg border border-gray-700/50 rounded-xl p-6 fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-br from-gold to-yellow-500 rounded-lg">
            <BarChart2 size={22} className="text-dark-bg" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Multi-Timeframe Analysis</h3>
            <p className="text-xs text-gray-400">Cross-timeframe trend confirmation</p>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700/50 bg-dark-card-light/30">
              <th className="text-left py-4 px-4 text-gray-400 font-bold uppercase tracking-widest text-xs">Timeframe</th>
              <th className="text-center py-4 px-4 text-gray-400 font-bold uppercase tracking-widest text-xs">Trend</th>
              <th className="text-center py-4 px-4 text-gray-400 font-bold uppercase tracking-widest text-xs">Status</th>
            </tr>
          </thead>
          <tbody>
            {trends.map((trend, idx) => (
              <tr
                key={idx}
                className="border-b border-gray-700/30 hover:bg-dark-card-light/40 transition-smooth"
              >
                <td className="py-4 px-4 font-semibold text-gray-200">{trend.name}</td>
                <td className="py-4 px-4 text-center">
                  <span
                    style={{ color: getTrendColor(trend.value) }}
                    className="font-bold text-lg"
                  >
                    {trend.value}
                  </span>
                </td>
                <td className="py-4 px-4 text-center">
                  <div
                    className="w-3 h-3 rounded-full mx-auto"
                    style={{ backgroundColor: getTrendColor(trend.value) }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Details */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-6 border-t border-gray-700/50">
        <div className="p-3 bg-dark-card-light/30 border border-gray-700/30 rounded-lg">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Market Structure</p>
          <p className="text-sm font-semibold text-accent">{result.market_structure || '-'}</p>
        </div>
        <div className="p-3 bg-dark-card-light/30 border border-gray-700/30 rounded-lg">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Break of Structure</p>
          <p className="text-sm font-semibold text-accent">{result.bos || '-'}</p>
        </div>
        <div className="p-3 bg-dark-card-light/30 border border-gray-700/30 rounded-lg">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Liquidity Sweep</p>
          <p className="text-sm font-semibold text-accent">{result.liquidity_sweep || '-'}</p>
        </div>
        <div className="p-3 bg-dark-card-light/30 border border-gray-700/30 rounded-lg">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Trend Strength</p>
          <p className="text-sm font-semibold text-gold">{(trendStrength * 100).toFixed(1)}%</p>
        </div>
      </div>
    </div>
  )
}

export default TrendTable
