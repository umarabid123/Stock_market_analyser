import React, { useEffect, useState } from 'react'
import {
  Line,
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { formatTime } from '../utils/formatters'

function TradingChart({ candles, pair }) {
  const [chartData, setChartData] = useState([])

  useEffect(() => {
    if (!Array.isArray(candles) || candles.length === 0) {
      setChartData([])
      return
    }

    const formatted = candles.map((candle) => ({
      time: formatTime(candle?.time),
      open: Number(candle?.open) || 0,
      high: Number(candle?.high) || 0,
      low: Number(candle?.low) || 0,
      close: Number(candle?.close) || 0,
      volume: Number(candle?.volume) || 0,
    }))

    setChartData(formatted)
  }, [candles])

  return (
    <div className="glass border border-gray-700 rounded-lg p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">{pair} Chart</h3>
        <p className="text-xs text-gray-400">Price chart with volume</p>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
          >
            <defs>
              <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00ff88" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00ff88" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

            <XAxis
              dataKey="time"
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
            />

            <YAxis
              yAxisId="price"
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
              domain={['auto', 'auto']}
            />

            <YAxis
              yAxisId="volume"
              orientation="right"
              hide
            />

            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#e2e8f0' }}
            />

            <Legend />

            <Bar
              yAxisId="volume"
              dataKey="volume"
              fill="url(#colorVolume)"
              name="Volume"
            />

            <Line
              yAxisId="price"
              type="monotone"
              dataKey="close"
              stroke="#00ff88"
              dot={false}
              isAnimationActive={false}
              name="Close"
            />
          </ComposedChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-96 flex items-center justify-center text-gray-400">
          <p>No candle data available</p>
        </div>
      )}
    </div>
  )
}

export default TradingChart