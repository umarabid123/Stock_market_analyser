import React from 'react'
import MarketCards from './MarketCards'
import TradingChart from './TradingChart'
import RiskPanel from './RiskPanel'
import TrendTable from './TrendTable'
import SignalPanel from './SignalPanel'
import { AlertCircle, BarChart3 } from 'lucide-react'

function MainDashboard({
  analysisResult,
  candles,
  loading,
  error,
  selectedPair,
  selectedTimeframe,
}) {
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

      {/* Loading State */}
      {loading && !analysisResult && (
        <div className="glass-lg border border-gray-700/50 p-8 sm:p-12 text-center fade-in">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-4">
            <BarChart3 size={24} className="animate-bounce text-gold flex-shrink-0" />
            <span className="text-lg sm:text-xl font-bold">Analyzing market...</span>
          </div>
          <p className="text-xs sm:text-sm text-gray-400 mt-2">Fetching real-time data and indicators</p>
          <div className="mt-4 flex justify-center gap-1">
            <div className="w-2 h-2 rounded-full bg-bullish animate-bounce"></div>
            <div className="w-2 h-2 rounded-full bg-bullish animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 rounded-full bg-bullish animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>
      )}

      {/* No Data State */}
      {!loading && !analysisResult && (
        <div className="glass-lg border border-gray-700/50 p-8 sm:p-12 text-center border-dashed">
          <BarChart3 size={32} className="mx-auto mb-3 text-gray-500" />
          <p className="text-base sm:text-lg text-gray-400">Click "Analyze Market" to get started</p>
          <p className="text-xs sm:text-sm text-gray-500 mt-3">Enter trading parameters in the sidebar</p>
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
              <TradingChart candles={candles} pair={selectedPair} />
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
