import React from 'react'
import MarketCards from './MarketCards'
import TradingChart from './TradingChart'
import RiskPanel from './RiskPanel'
import TrendTable from './TrendTable'
import SignalPanel from './SignalPanel'
import { AlertCircle } from 'lucide-react'

function MainDashboard({
  analysisResult,
  candles,
  loading,
  loadingStage,
  error,
  selectedPair,
  selectedTimeframe,
  selectedLookback,
  selectedMarket,
}) {
  const defaultMarket = selectedMarket || 'Forex'
  const showInitialLoading = loadingStage === 'initial' && loading && !analysisResult
  const showSkeleton = loadingStage === 'skeleton' && loading && !analysisResult
  return (
    <div className="flex-1 overflow-auto bg-dark-bg space-y-4 sm:space-y-6 md:space-y-8 p-4 sm:p-6 md:p-8">
      {/* Error Message */}
      {error && (
        <div className="glass-lg border-l-4 border-bearish p-4 sm:p-6 bg-red-900/20 flex flex-col sm:flex-row items-start gap-3 sm:gap-4 fade-in">
          <AlertCircle className="text-bearish flex-shrink-0 mt-0.5 w-5 h-5 sm:w-6 sm:h-6" />
          <div className="flex-1">
            <h3 className="font-bold text-bearish text-base sm:text-lg">Error</h3>
            <p className="text-xs sm:text-sm text-gray-300 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Initial Loading State */}
      {showInitialLoading && (
        <div className="glass-lg border border-gray-700/50 p-5 sm:p-6 rounded-lg flex items-center gap-4 fade-in">
          <div className="w-5 h-5 sm:w-6 sm:h-6 border-2 border-bullish border-t-transparent rounded-full animate-spin" />
          <div>
            <p className="text-sm sm:text-base font-semibold text-white">Loading market analysis</p>
            <p className="text-xs text-gray-400 mt-1">Fetching live data and preparing insights.</p>
          </div>
        </div>
      )}

      {/* Loading Skeleton State */}
      {showSkeleton && (
        <div className="space-y-4 sm:space-y-6 fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="glass-lg border border-gray-700/50 p-4 rounded-lg">
                <div className="skeleton h-3 w-20 mb-3"></div>
                <div className="skeleton h-7 w-32"></div>
                <div className="skeleton h-3 w-24 mt-3"></div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
            <div className="lg:col-span-2 glass-lg border border-gray-700/50 p-4 rounded-lg">
              <div className="skeleton h-4 w-36 mb-4"></div>
              <div className="skeleton h-[360px] sm:h-[420px]"></div>
            </div>
            <div className="glass-lg border border-gray-700/50 p-4 rounded-lg">
              <div className="skeleton h-4 w-28 mb-4"></div>
              <div className="skeleton h-24"></div>
              <div className="skeleton h-24 mt-3"></div>
            </div>
          </div>
        </div>
      )}

      {/* No Data State */}
      {!loading && !analysisResult && (
        <div className="glass-lg border border-gray-700/50 p-6 sm:p-10 text-left border-dashed">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-widest text-gray-500">Default Setup</p>
              <h3 className="text-lg sm:text-xl font-bold text-white mt-2">{defaultMarket} Trading Preset</h3>
              <p className="text-xs sm:text-sm text-gray-400 mt-2">
                Use the sidebar to adjust the preset, then run a fresh analysis.
              </p>
            </div>
            <div className="glass border border-gray-700/60 px-4 py-3 rounded-lg">
              <p className="text-xs text-gray-400 uppercase tracking-widest">Ready</p>
              <p className="text-sm font-semibold text-white">Select Analyze Market</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-6">
            <div className="glass border border-gray-700/50 px-4 py-3 rounded-lg">
              <p className="text-xs text-gray-500 uppercase tracking-widest">Pair</p>
              <p className="text-base font-semibold text-white mt-1">{selectedPair}</p>
            </div>
            <div className="glass border border-gray-700/50 px-4 py-3 rounded-lg">
              <p className="text-xs text-gray-500 uppercase tracking-widest">Timeframe</p>
              <p className="text-base font-semibold text-white mt-1">{selectedTimeframe}</p>
            </div>
            <div className="glass border border-gray-700/50 px-4 py-3 rounded-lg">
              <p className="text-xs text-gray-500 uppercase tracking-widest">Lookback</p>
              <p className="text-base font-semibold text-white mt-1">{selectedLookback}</p>
            </div>
          </div>
        </div>
      )}

      {/* Dashboard Content */}
      {analysisResult && (
        <>
          {/* Market Cards Row - Responsive Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <MarketCards result={analysisResult} />
          </div>

          {/* Chart and Risk Row - Stack on mobile */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
            {/* Trading Chart - Full width on mobile */}
            <div className="lg:col-span-2">
              <TradingChart
                candles={candles}
                pair={selectedPair}
                timeframe={selectedTimeframe}
                loading={loading}
                theme="light"
              />
            </div>

            {/* Risk Panel - Full width on mobile */}
            <div className="lg:col-span-1">
              <RiskPanel result={analysisResult} />
            </div>
          </div>

          {/* Signal Panel */}
          <SignalPanel result={analysisResult} />

          {/* Trends Table */}
          <TrendTable result={analysisResult} />

          {/* Warning Footer */}
          <div className="glass-lg border border-yellow-700/40 p-4 sm:p-5 bg-yellow-900/15 text-center text-xs sm:text-sm text-yellow-200 rounded-xl">
            <p className="font-medium">
              ⚠️ AI-assisted analysis for educational purposes only. Not financial advice.
            </p>
            <p className="text-yellow-300/80 mt-2 text-xs">
              Trade at your own risk. Always use proper risk management and capital preservation strategies.
            </p>
          </div>
        </>
      )}
    </div>
  )
}

export default MainDashboard
