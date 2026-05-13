import React, { useState, useCallback, useEffect, useRef } from 'react'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import MainDashboard from './components/MainDashboard'
import Chatbot from './components/Chatbot'
import { analyzeMarket, getCandles } from './api/marketApi'

function App() {
  const [selectedMarket, setSelectedMarket] = useState('Forex')
  const [selectedPair, setSelectedPair] = useState('GBP/USD')
  const [selectedTimeframe, setSelectedTimeframe] = useState('1m')
  const [selectedLookback, setSelectedLookback] = useState('1d')
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
      const [result, candleData] = await Promise.all([
        analyzeMarket(selectedPair, selectedTimeframe, selectedLookback),
        getCandles(selectedPair, selectedTimeframe, selectedLookback),
      ])

      setAnalysisResult(result ?? null)
      setCandles(Array.isArray(candleData) ? candleData : [])
    } catch (err) {
      setError(err?.message || 'Failed to analyze market')
      console.error('Analysis error:', err)
      setCandles([])
      setAnalysisResult(null)
    } finally {
      setLoading(false)
    }
  }, [selectedPair, selectedTimeframe, selectedLookback])

  const hasAutoRunRef = useRef(false)

  useEffect(() => {
    if (hasAutoRunRef.current) return
    hasAutoRunRef.current = true
    performAnalysis()
  }, [performAnalysis])

  // Handle market change
  const handleMarketChange = (market) => {
    setSelectedMarket(market)
    // Auto-select appropriate pair based on market
    const marketPairs = {
      'Forex': 'GBP/USD',
      'Commodities': 'XAU/USD',
      'Crypto': 'BTC/USD',
    }
    setSelectedPair(marketPairs[market] || 'GBP/USD')
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
          loading={loading}
        />

        {/* Dashboard */}
        <MainDashboard
          analysisResult={analysisResult}
          candles={candles}
          loading={loading}
          error={error}
          selectedPair={selectedPair}
          selectedTimeframe={selectedTimeframe}
          selectedLookback={selectedLookback}
          selectedMarket={selectedMarket}
        />
      </div>

      {/* Floating Chatbot */}
      <Chatbot currentResult={analysisResult} />
    </div>
  )
}

export default App
