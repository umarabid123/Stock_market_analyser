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
    <div className="flex-1 overflow-auto p-6 bg-dark-bg space-y-6">
      {/* Error Message */}
      {error && (
        <div className="glass border-l-4 border-bearish p-4 bg-red-900/20 flex items-start gap-3">
          <AlertCircle className="text-bearish flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-bearish">Error</h3>
            <p className="text-sm text-gray-300">{error}</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && !analysisResult && (
        <div className="glass border border-gray-700 p-8 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <BarChart3 size={24} className="animate-bounce text-gold" />
            <span className="text-lg font-semibold">Analyzing market...</span>
          </div>
          <p className="text-sm text-gray-400">Fetching real-time data and indicators</p>
        </div>
      )}

      {/* No Data State */}
      {!loading && !analysisResult && (
        <div className="glass border border-gray-700 p-8 text-center border-dashed">
          <BarChart3 size={32} className="mx-auto mb-3 text-gray-500" />
          <p className="text-gray-400">Click "Analyze Market" to get started</p>
        </div>
      )}

      {/* Dashboard Content */}
      {analysisResult && (
        <>
          {/* Market Cards Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MarketCards result={analysisResult} />
          </div>

          {/* Chart and Risk Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Trading Chart - Takes 2 columns */}
            <div className="lg:col-span-2">
              <TradingChart candles={candles} pair={selectedPair} />
            </div>

            {/* Risk Panel - Takes 1 column */}
            <RiskPanel result={analysisResult} />
          </div>

          {/* Signal Panel */}
          <SignalPanel result={analysisResult} />

          {/* Trends Table */}
          <TrendTable result={analysisResult} />

          {/* Warning Footer */}
          <div className="glass border border-yellow-700/50 p-4 bg-yellow-900/10 text-center text-xs text-yellow-200">
            <p>
              ⚠️ This is AI-assisted market analysis for educational and research purposes only.
              It is not financial advice and does not guarantee profit.
            </p>
          </div>
        </>
      )}
    </div>
  )
}

export default MainDashboard
