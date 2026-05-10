import React, { useState } from 'react'
import {
  Menu,
  X,
  TrendingUp,
  BarChart3,
  RotateCw,
  Play,
} from 'lucide-react'

function Sidebar({
  selectedMarket,
  onMarketChange,
  selectedPair,
  onPairChange,
  selectedTimeframe,
  onTimeframeChange,
  selectedLookback,
  onLookbackChange,
  autoRefresh,
  onAutoRefreshChange,
  refreshInterval,
  onRefreshIntervalChange,
  onAnalyze,
  loading,
}) {
  const [isOpen, setIsOpen] = useState(true)

  const markets = ['Forex', 'Commodities', 'Crypto']

  const pairsByMarket = {
    Forex: ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD'],
    Commodities: ['XAU/USD', 'XAG/USD', 'CL=F', 'NG=F'],
    Crypto: ['BTC/USD', 'ETH/USD', 'XRP/USD', 'ADA/USD'],
  }

  const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
  const lookbacks = ['1d', '5d', '1mo', '3mo', '6mo']

  const pairs = pairsByMarket[selectedMarket] || []

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden glass p-2 rounded-lg"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`glass border-r border-gray-700 w-64 overflow-y-auto transition-all duration-300 flex flex-col ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } fixed lg:static h-full z-40 lg:z-auto`}
      >
        {/* Logo Section */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <BarChart3 size={24} className="text-gold" />
            <span className="font-bold text-lg">AI Forex</span>
          </div>
        </div>

        {/* Market Selector */}
        <div className="p-6 border-b border-gray-700">
          <label className="block text-sm font-semibold text-gray-300 mb-3">Market Type</label>
          <div className="space-y-2">
            {markets.map((market) => (
              <button
                key={market}
                onClick={() => {
                  onMarketChange(market)
                  setIsOpen(false)
                }}
                className={`w-full px-4 py-2 rounded-lg text-sm font-medium transition ${
                  selectedMarket === market
                    ? 'bg-gold text-dark-bg'
                    : 'bg-dark-card hover:bg-gray-700'
                }`}
              >
                {market}
              </button>
            ))}
          </div>
        </div>

        {/* Pair Selector */}
        <div className="p-6 border-b border-gray-700">
          <label className="block text-sm font-semibold text-gray-300 mb-3">Trading Pair</label>
          <select
            value={selectedPair}
            onChange={(e) => onPairChange(e.target.value)}
            className="w-full px-3 py-2 bg-dark-card border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-gold"
          >
            {pairs.map((pair) => (
              <option key={pair} value={pair}>
                {pair}
              </option>
            ))}
          </select>
        </div>

        {/* Timeframe Selector */}
        <div className="p-6 border-b border-gray-700">
          <label className="block text-sm font-semibold text-gray-300 mb-3">Timeframe</label>
          <div className="grid grid-cols-3 gap-2">
            {timeframes.map((tf) => (
              <button
                key={tf}
                onClick={() => onTimeframeChange(tf)}
                className={`px-2 py-1 rounded text-xs font-medium transition ${
                  selectedTimeframe === tf
                    ? 'bg-bullish text-dark-bg'
                    : 'bg-dark-card hover:bg-gray-700'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* Lookback Period */}
        <div className="p-6 border-b border-gray-700">
          <label className="block text-sm font-semibold text-gray-300 mb-3">Lookback</label>
          <div className="grid grid-cols-2 gap-2">
            {lookbacks.map((lb) => (
              <button
                key={lb}
                onClick={() => onLookbackChange(lb)}
                className={`px-2 py-1 rounded text-xs font-medium transition ${
                  selectedLookback === lb
                    ? 'bg-bullish text-dark-bg'
                    : 'bg-dark-card hover:bg-gray-700'
                }`}
              >
                {lb}
              </button>
            ))}
          </div>
        </div>

        {/* Auto Refresh */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-semibold text-gray-300">Auto Refresh</label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => onAutoRefreshChange(e.target.checked)}
              className="w-4 h-4 rounded cursor-pointer"
            />
          </div>
          {autoRefresh && (
            <input
              type="number"
              min="10"
              max="300"
              value={refreshInterval}
              onChange={(e) => onRefreshIntervalChange(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-dark-card border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-gold"
              placeholder="Interval (seconds)"
            />
          )}
        </div>

        {/* Analyze Button */}
        <div className="p-6 mt-auto">
          <button
            onClick={onAnalyze}
            disabled={loading}
            className={`w-full py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition ${
              loading
                ? 'bg-gray-700 cursor-not-allowed opacity-50'
                : 'bg-gradient-to-r from-bullish to-gold text-dark-bg hover:shadow-lg hover:shadow-bullish/50'
            }`}
          >
            <Play size={18} />
            {loading ? 'Analyzing...' : 'Analyze Market'}
          </button>
        </div>

        {/* Footer Info */}
        <div className="p-6 border-t border-gray-700 text-center text-xs text-gray-500">
          <p>Paper Trading Mode</p>
          <p>Educational Use Only</p>
        </div>
      </aside>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 lg:hidden z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  )
}

export default Sidebar
