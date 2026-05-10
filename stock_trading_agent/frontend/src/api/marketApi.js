import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Analyze market for a given symbol
 * @param {string} symbol - Trading pair symbol (e.g., EUR/USD, XAU/USD)
 * @param {string} timeframe - Timeframe (e.g., 15m, 1h, 4h)
 * @param {string} lookback - Lookback period (e.g., 5d, 1mo)
 * @returns {Promise<Object>} Market analysis with signal, confidence, and risk levels
 */
export const analyzeMarket = async (symbol, timeframe = '15m', lookback = '5d') => {
  try {
    const response = await client.post('/api/analyze', {
      symbol,
      timeframe,
      lookback,
    })
    return response.data
  } catch (error) {
    console.error('Error analyzing market:', error)
    throw error
  }
}

/**
 * Get candlestick data for a symbol
 * @param {string} symbol - Trading pair symbol
 * @param {string} timeframe - Timeframe
 * @param {string} lookback - Lookback period
 * @returns {Promise<Array>} Array of candle objects
 */
export const getCandles = async (symbol, timeframe = '15m', lookback = '5d') => {
  try {
    const response = await client.get('/api/candles', {
      params: {
        symbol,
        timeframe,
        lookback,
      },
    })
    return response.data
  } catch (error) {
    console.error('Error fetching candles:', error)
    throw error
  }
}

/**
 * Send message to chatbot
 * @param {string} message - User question or message
 * @param {Object} currentResult - Current market analysis result (optional)
 * @returns {Promise<Object>} Chatbot response
 */
export const sendChatMessage = async (message, currentResult = null) => {
  try {
    const response = await client.post('/api/chat', {
      message,
      current_result: currentResult,
    })
    return response.data
  } catch (error) {
    console.error('Error sending chat message:', error)
    throw error
  }
}

/**
 * Check API health
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await client.get('/api/health')
    return response.data
  } catch (error) {
    console.error('Error checking health:', error)
    throw error
  }
}

export default client
