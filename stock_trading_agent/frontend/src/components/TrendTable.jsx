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
    <div className="glass border border-gray-700 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <BarChart2 size={20} className="text-gold" />
        <h3 className="text-lg font-semibold">Multi-Timeframe Analysis</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-3 px-4 text-gray-400 font-semibold">Timeframe</th>
              <th className="text-center py-3 px-4 text-gray-400 font-semibold">Trend</th>
              <th className="text-left py-3 px-4 text-gray-400 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody>
            {trends.map((trend, idx) => (
              <tr
                key={idx}
                className="border-b border-gray-700 hover:bg-dark-card/50 transition"
              >
                <td className="py-3 px-4 font-semibold">{trend.name}</td>
                <td className="py-3 px-4 text-center">
                  <span
                    style={{ color: getTrendColor(trend.value) }}
                    className="font-bold"
                  >
                    {trend.value}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: getTrendColor(trend.value) }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Details */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-700">
        <div>
          <p className="text-xs text-gray-400 uppercase mb-1">Market Structure</p>
          <p className="text-sm font-semibold">{result.market_structure || '-'}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase mb-1">Break of Structure</p>
          <p className="text-sm font-semibold">{result.bos || '-'}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase mb-1">Liquidity Sweep</p>
          <p className="text-sm font-semibold">{result.liquidity_sweep || '-'}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase mb-1">Trend Strength</p>
          <p className="text-sm font-semibold">{(trendStrength * 100).toFixed(1)}%</p>
        </div>
      </div>
    </div>
  )
}

export default TrendTable
