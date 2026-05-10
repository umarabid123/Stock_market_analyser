/**
 * Format large numbers with K/M/B suffix
 * @param {number} num - Number to format
 * @param {number} decimals - Decimal places (default 2)
 * @returns {string} Formatted number
 */
export const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '-'
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(decimals) + 'B'
  } else if (num >= 1000000) {
    return (num / 1000000).toFixed(decimals) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(decimals) + 'K'
  }
  return num.toFixed(decimals)
}

/**
 * Format price with appropriate decimal places
 * @param {number} price - Price to format
 * @returns {string} Formatted price
 */
export const formatPrice = (price) => {
  if (price === null || price === undefined) return '-'
  if (price < 1) {
    return parseFloat(price).toFixed(5)
  } else if (price < 100) {
    return parseFloat(price).toFixed(4)
  } else {
    return parseFloat(price).toFixed(2)
  }
}

/**
 * Format percentage
 * @param {number} value - Value to format as percentage
 * @param {number} decimals - Decimal places (default 2)
 * @returns {string} Formatted percentage
 */
export const formatPercent = (value, decimals = 2) => {
  if (value === null || value === undefined) return '-'
  return (parseFloat(value) * 100).toFixed(decimals) + '%'
}

/**
 * Format time from timestamp
 * @param {string|Date} time - Time to format
 * @param {boolean} includeSeconds - Include seconds (default false)
 * @returns {string} Formatted time
 */
export const formatTime = (time, includeSeconds = false) => {
  if (!time) return '-'
  try {
    const date = typeof time === 'string' ? new Date(time) : time
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    if (includeSeconds) {
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${hours}:${minutes}:${seconds}`
    }
    return `${hours}:${minutes}`
  } catch {
    return '-'
  }
}

/**
 * Format date
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date
 */
export const formatDate = (date) => {
  if (!date) return '-'
  try {
    const d = typeof date === 'string' ? new Date(date) : date
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  } catch {
    return '-'
  }
}

/**
 * Get signal color class
 * @param {string} signal - Signal value (BUY, SELL, HOLD, etc.)
 * @returns {string} Tailwind color class
 */
export const getSignalColor = (signal) => {
  if (!signal) return 'text-gray-400'
  const upper = signal.toUpperCase()
  if (upper.includes('BUY')) {
    return 'text-bullish'
  } else if (upper.includes('SELL')) {
    return 'text-bearish'
  } else if (upper.includes('WAIT')) {
    return 'text-yellow-500'
  } else {
    return 'text-neutral'
  }
}

/**
 * Get bias color class
 * @param {string} bias - Bias value (BULLISH, BEARISH, NEUTRAL)
 * @returns {string} Tailwind color class
 */
export const getBiasColor = (bias) => {
  if (!bias) return 'text-gray-400'
  const upper = bias.toUpperCase()
  if (upper === 'BULLISH') {
    return 'text-bullish'
  } else if (upper === 'BEARISH') {
    return 'text-bearish'
  } else {
    return 'text-neutral'
  }
}

/**
 * Get background color for signal
 * @param {string} signal - Signal value
 * @returns {string} Background color class
 */
export const getSignalBgColor = (signal) => {
  if (!signal) return 'bg-gray-900'
  const upper = signal.toUpperCase()
  if (upper.includes('BUY')) {
    return 'bg-green-900/20'
  } else if (upper.includes('SELL')) {
    return 'bg-red-900/20'
  } else if (upper.includes('WAIT')) {
    return 'bg-yellow-900/20'
  } else {
    return 'bg-gray-900/20'
  }
}

/**
 * Get trend color
 * @param {string} trend - Trend value
 * @returns {string} Color value
 */
export const getTrendColor = (trend) => {
  if (!trend) return '#94a3b8'
  const upper = trend.toUpperCase()
  if (upper === 'BULLISH' || upper === 'UP') {
    return '#00ff88'
  } else if (upper === 'BEARISH' || upper === 'DOWN') {
    return '#ff3333'
  } else {
    return '#94a3b8'
  }
}

/**
 * Format confidence as percentage
 * @param {number} confidence - Confidence value (0-1)
 * @returns {string} Formatted confidence
 */
export const formatConfidence = (confidence) => {
  if (confidence === null || confidence === undefined) return '-'
  const percent = confidence * 100
  return percent.toFixed(1) + '%'
}
