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
  const [chartHeight, setChartHeight] = useState(400)

  // Adjust chart height based on screen size
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 640) {
        setChartHeight(250)
      } else if (window.innerWidth < 1024) {
        setChartHeight(300)
      } else {
        setChartHeight(400)
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

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
    <div className="glass border border-gray-700 rounded-lg p-3 sm:p-4 md:p-6 w-full overflow-x-auto">
      <div className="mb-3 sm:mb-4">
        <h3 className="text-base sm:text-lg font-semibold">{pair} Chart</h3>
        <p className="text-xs text-gray-400">Price chart with volume</p>
      </div>

      {chartData.length > 0 ? (
        <div className="w-full" style={{ minHeight: `${chartHeight}px` }}>
          <ResponsiveContainer width="100%" height={chartHeight}>
            <ComposedChart
              data={chartData}
              margin={{ top: 15, right: 20, left: -20, bottom: 15 }}
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
                style={{ fontSize: '10px' }}
                interval={Math.floor(chartData.length / 6)}
              />

              <YAxis
                yAxisId="price"
                stroke="#94a3b8"
                style={{ fontSize: '10px' }}
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
                  fontSize: '12px',
                }}
                labelStyle={{ color: '#e2e8f0' }}
              />

              <Legend wrapperStyle={{ fontSize: '12px' }} />

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
                strokeWidth={2}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-40 sm:h-64 md:h-96 flex items-center justify-center text-gray-400">
          <p className="text-sm">No candle data available</p>
        </div>
      )}
    </div>
  )
}

export default TradingChart