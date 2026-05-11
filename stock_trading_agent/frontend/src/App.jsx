import React, { useState, useCallback } from 'react'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import MainDashboard from './components/MainDashboard'
import Chatbot from './components/Chatbot'
import { analyzeMarket, getCandles } from './api/marketApi'

function App() {
  const [selectedMarket, setSelectedMarket] = useState('Forex')
  const [selectedPair, setSelectedPair] = useState('EUR/USD')
  const [selectedTimeframe, setSelectedTimeframe] = useState('15m')
  const [selectedLookback, setSelectedLookback] = useState('5d')
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [refreshInterval, setRefreshInterval] = useState(60)

  const [analysisResult, setAnalysisResult] = useState(null)
  const [candles, setCandles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Perform market analysis
  const performAnalysis = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeMarket(selectedPair, selectedTimeframe, selectedLookback)
      const safeResult = result ?? null
      setAnalysisResult(safeResult)
      console.log('analysis', safeResult)

      // Fetch candles
      const candleData = await getCandles(selectedPair, selectedTimeframe, selectedLookback)
      const safeCandles = Array.isArray(candleData) ? candleData : []
      setCandles(safeCandles)
      console.log('candles', safeCandles)
    } catch (err) {
      setError(err?.message || 'Failed to analyze market')
      console.error('Analysis error:', err)
      setCandles([])
      setAnalysisResult(null)
    } finally {
      setLoading(false)
    }
  }, [selectedPair, selectedTimeframe, selectedLookback])

  // Handle market change
  const handleMarketChange = (market) => {
    setSelectedMarket(market)
    // Auto-select appropriate pair based on market
    const marketPairs = {
      'Forex': 'EUR/USD',
      'Commodities': 'XAU/USD',
      'Crypto': 'BTC/USD',
    }
    setSelectedPair(marketPairs[market] || 'EUR/USD')
  }

  // Handle analyze button click
  const handleAnalyze = () => {
    performAnalysis()
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-dark-bg via-dark-bg to-dark-card text-gray-100 overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        selectedMarket={selectedMarket}
        onMarketChange={handleMarketChange}
        selectedPair={selectedPair}
        onPairChange={setSelectedPair}
        selectedTimeframe={selectedTimeframe}
        onTimeframeChange={setSelectedTimeframe}
        selectedLookback={selectedLookback}
        onLookbackChange={setSelectedLookback}
        autoRefresh={autoRefresh}
        onAutoRefreshChange={setAutoRefresh}
        refreshInterval={refreshInterval}
        onRefreshIntervalChange={setRefreshInterval}
        onAnalyze={handleAnalyze}
        loading={loading}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Navbar */}
        <Navbar
          selectedPair={selectedPair}
          analysisResult={analysisResult}
        />

        {/* Dashboard */}
        <MainDashboard
          analysisResult={analysisResult}
          candles={candles}
          loading={loading}
          error={error}
          selectedPair={selectedPair}
          selectedTimeframe={selectedTimeframe}
        />
      </div>

      {/* Floating Chatbot */}
      <Chatbot currentResult={analysisResult} />
    </div>
  )
}

export default App
