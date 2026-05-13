import React, { useEffect, useMemo, useRef, useState } from 'react'
import {
  formatDate,
  formatNumber,
  formatPercent,
  formatPrice,
  formatTime,
} from '../utils/formatters'

const SAMPLE_CANDLES = [
  { time: '2024-04-01', open: 173.4, high: 176.2, low: 172.1, close: 175.6, volume: 53100000 },
  { time: '2024-04-02', open: 175.7, high: 178.9, low: 175.1, close: 178.2, volume: 48200000 },
  { time: '2024-04-03', open: 178.3, high: 179.4, low: 176.8, close: 177.2, volume: 46350000 },
  { time: '2024-04-04', open: 177.1, high: 178.2, low: 174.6, close: 175.1, volume: 51230000 },
  { time: '2024-04-05', open: 175.2, high: 177.8, low: 174.7, close: 177.4, volume: 49870000 },
  { time: '2024-04-08', open: 177.5, high: 181.2, low: 176.3, close: 180.6, volume: 61590000 },
  { time: '2024-04-09', open: 180.8, high: 182.4, low: 179.7, close: 181.9, volume: 44210000 },
  { time: '2024-04-10', open: 181.7, high: 182.1, low: 178.6, close: 179.4, volume: 52450000 },
  { time: '2024-04-11', open: 179.6, high: 181.5, low: 177.9, close: 178.2, volume: 47880000 },
  { time: '2024-04-12', open: 178.1, high: 179.9, low: 176.4, close: 179.2, volume: 50230000 },
  { time: '2024-04-15', open: 179.4, high: 182.2, low: 178.6, close: 181.7, volume: 51470000 },
  { time: '2024-04-16', open: 181.5, high: 183.9, low: 180.8, close: 183.1, volume: 46320000 },
  { time: '2024-04-17', open: 183.2, high: 185.3, low: 182.4, close: 184.8, volume: 47290000 },
  { time: '2024-04-18', open: 184.7, high: 186.1, low: 182.6, close: 183.2, volume: 50580000 },
  { time: '2024-04-19', open: 183.1, high: 184.4, low: 181.3, close: 181.9, volume: 53810000 },
  { time: '2024-04-22', open: 182.1, high: 184.8, low: 181.2, close: 184.2, volume: 52640000 },
  { time: '2024-04-23', open: 184.3, high: 186.2, low: 183.7, close: 185.6, volume: 49700000 },
  { time: '2024-04-24', open: 185.5, high: 187.6, low: 184.1, close: 186.9, volume: 48120000 },
  { time: '2024-04-25', open: 186.8, high: 189.3, low: 185.7, close: 188.4, volume: 54270000 },
  { time: '2024-04-26', open: 188.2, high: 189.9, low: 186.4, close: 187.1, volume: 51960000 },
]

const DEFAULT_HEIGHT = 500
const THEME_OPTIONS = {
  light: {
    background: '#f8fafc',
    text: '#0f172a',
    grid: '#e2e8f0',
    border: '#cbd5f5',
    crosshair: '#64748b',
  },
  dark: {
    background: '#0b1120',
    text: '#e2e8f0',
    grid: '#1f2937',
    border: '#334155',
    crosshair: '#94a3b8',
  },
}

const bullishColor = '#22c55e'
const bearishColor = '#ef4444'

const parseToTimestamp = (value) => {
  if (!value) return null
  if (typeof value === 'number') {
    return value > 1e12 ? Math.floor(value / 1000) : value
  }
  if (typeof value === 'string') {
    const parsed = new Date(value)
    if (Number.isNaN(parsed.getTime())) return null
    return Math.floor(parsed.getTime() / 1000)
  }
  return null
}

const toDateFromTime = (time) => {
  if (!time) return null
  if (typeof time === 'number') return new Date(time * 1000)
  if (typeof time === 'string') return new Date(time)
  if (typeof time === 'object' && time.year) {
    return new Date(time.year, time.month - 1, time.day)
  }
  return null
}

const formatCrosshairTime = (time, useDateLabels) => {
  const date = toDateFromTime(time)
  if (!date || Number.isNaN(date.getTime())) return '-'
  return useDateLabels ? formatDate(date) : formatTime(date)
}

const normalizeCandles = (candles) =>
  candles
    .map((candle) => {
      const time = parseToTimestamp(candle?.time)
      if (!time) return null
      return {
        time,
        open: Number(candle?.open) || 0,
        high: Number(candle?.high) || 0,
        low: Number(candle?.low) || 0,
        close: Number(candle?.close) || 0,
        volume: Number(candle?.volume) || 0,
      }
    })
    .filter(Boolean)

function TradingChart({
  candles,
  pair,
  timeframe,
  loading = false,
  theme = 'dark',
  useSampleData = false,
}) {
  const resolvedTheme = theme === 'light' ? 'light' : 'dark'
  const themeTokens = THEME_OPTIONS[resolvedTheme]
  const useDateLabels = Boolean(timeframe && /d|w|mo/i.test(timeframe))
  const shouldUseSampleData = Boolean(useSampleData)

  const [chartHeight, setChartHeight] = useState(DEFAULT_HEIGHT)
  const [tooltip, setTooltip] = useState(null)

  const containerRef = useRef(null)
  const chartRef = useRef(null)
  const candleSeriesRef = useRef(null)
  const volumeSeriesRef = useRef(null)
  const resizeObserverRef = useRef(null)
  const rafRef = useRef(null)
  const dateLabelRef = useRef(useDateLabels)
  const chartHeightRef = useRef(chartHeight)
  const themeRef = useRef(themeTokens)

  const candleData = useMemo(() => {
    const raw = shouldUseSampleData ? SAMPLE_CANDLES : candles || []
    return normalizeCandles(raw)
  }, [candles, shouldUseSampleData])

  const volumeData = useMemo(() =>
    candleData.map((item) => ({
      time: item.time,
      value: item.volume,
      color: item.close >= item.open ? bullishColor : bearishColor,
    })), [candleData])

  const lastCandle = candleData[candleData.length - 1]
  const change = lastCandle ? lastCandle.close - lastCandle.open : 0
  const changePercent = lastCandle?.open ? change / lastCandle.open : 0
  const changeClass = change >= 0 ? 'tv-chart__price-up' : 'tv-chart__price-down'
  const changeLabel = `${change >= 0 ? '+' : ''}${formatPrice(change)}`

  useEffect(() => {
    dateLabelRef.current = useDateLabels
  }, [useDateLabels])

  useEffect(() => {
    chartHeightRef.current = chartHeight
  }, [chartHeight])

  useEffect(() => {
    themeRef.current = themeTokens
  }, [themeTokens])

  useEffect(() => {
    if (typeof window === 'undefined') return undefined

    const handleResize = () => {
      if (window.innerWidth < 640) {
        setChartHeight(360)
      } else if (window.innerWidth < 1024) {
        setChartHeight(430)
      } else {
        setChartHeight(DEFAULT_HEIGHT)
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    let isMounted = true
    let crosshairHandler

    const setupChart = async () => {
      if (!containerRef.current || typeof window === 'undefined') return
      const { createChart, CrosshairMode } = await import('lightweight-charts')
      if (!containerRef.current || !isMounted) return

      const currentTheme = themeRef.current
      const chart = createChart(containerRef.current, {
        height: chartHeightRef.current,
        layout: {
          background: { color: currentTheme.background },
          textColor: currentTheme.text,
          fontFamily: 'Space Grotesk, system-ui, sans-serif',
          fontSize: 12,
        },
        grid: {
          vertLines: { color: currentTheme.grid },
          horzLines: { color: currentTheme.grid },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
          borderColor: currentTheme.border,
        },
        rightPriceScale: {
          borderColor: currentTheme.border,
        },
        crosshair: {
          mode: CrosshairMode.Normal,
          vertLine: {
            color: currentTheme.crosshair,
            labelBackgroundColor: currentTheme.background,
          },
          horzLine: {
            color: currentTheme.crosshair,
            labelBackgroundColor: currentTheme.background,
          },
        },
        handleScroll: true,
        handleScale: true,
      })

      const candleSeries = chart.addCandlestickSeries({
        upColor: bullishColor,
        downColor: bearishColor,
        borderUpColor: bullishColor,
        borderDownColor: bearishColor,
        wickUpColor: bullishColor,
        wickDownColor: bearishColor,
      })

      const volumeSeries = chart.addHistogramSeries({
        priceScaleId: '',
        priceFormat: { type: 'volume' },
        color: bullishColor,
      })

      volumeSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.8, bottom: 0 },
      })

      candleSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.15, bottom: 0.2 },
      })

      crosshairHandler = (param) => {
        if (!param || !param.time || !param.point || !containerRef.current) {
          setTooltip(null)
          return
        }

        const seriesData = param.seriesData.get(candleSeries)
        if (!seriesData) {
          setTooltip(null)
          return
        }

        const volumePoint = param.seriesData.get(volumeSeries)
        const label = formatCrosshairTime(param.time, dateLabelRef.current)
        const containerWidth = containerRef.current.clientWidth
        const tooltipWidth = 170
        const left = Math.min(
          Math.max(param.point.x + 16, 12),
          containerWidth - tooltipWidth - 12
        )
        const top = Math.max(param.point.y - 40, 12)

        if (rafRef.current) cancelAnimationFrame(rafRef.current)
        rafRef.current = requestAnimationFrame(() => {
          setTooltip({
            left,
            top,
            label,
            open: seriesData.open,
            high: seriesData.high,
            low: seriesData.low,
            close: seriesData.close,
            volume: volumePoint?.value ?? 0,
            isBullish: seriesData.close >= seriesData.open,
          })
        })
      }

      chart.subscribeCrosshairMove(crosshairHandler)

      if (typeof ResizeObserver !== 'undefined') {
        resizeObserverRef.current = new ResizeObserver(() => {
          if (!containerRef.current) return
          const { width } = containerRef.current.getBoundingClientRect()
          chart.applyOptions({ width, height: chartHeightRef.current })
        })
        resizeObserverRef.current.observe(containerRef.current)
      }

      chartRef.current = chart
      candleSeriesRef.current = candleSeries
      volumeSeriesRef.current = volumeSeries
    }

    setupChart()

    return () => {
      isMounted = false
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      if (resizeObserverRef.current) {
        resizeObserverRef.current.disconnect()
        resizeObserverRef.current = null
      }
      if (chartRef.current && crosshairHandler) {
        chartRef.current.unsubscribeCrosshairMove(crosshairHandler)
      }
      if (chartRef.current) {
        chartRef.current.remove()
      }
      chartRef.current = null
      candleSeriesRef.current = null
      volumeSeriesRef.current = null
    }
  }, [])

  useEffect(() => {
    if (!chartRef.current || !candleSeriesRef.current || !volumeSeriesRef.current) {
      return
    }
    candleSeriesRef.current.setData(candleData)
    volumeSeriesRef.current.setData(volumeData)
    chartRef.current.timeScale().fitContent()
  }, [candleData, volumeData])

  useEffect(() => {
    if (!chartRef.current) return
    chartRef.current.applyOptions({
      height: chartHeight,
      layout: {
        background: { color: themeTokens.background },
        textColor: themeTokens.text,
      },
      grid: {
        vertLines: { color: themeTokens.grid },
        horzLines: { color: themeTokens.grid },
      },
      timeScale: {
        borderColor: themeTokens.border,
      },
      rightPriceScale: {
        borderColor: themeTokens.border,
      },
      crosshair: {
        vertLine: {
          color: themeTokens.crosshair,
          labelBackgroundColor: themeTokens.background,
        },
        horzLine: {
          color: themeTokens.crosshair,
          labelBackgroundColor: themeTokens.background,
        },
      },
    })
  }, [chartHeight, themeTokens])

  return (
    <div className={`tv-chart tv-chart--${resolvedTheme}`}>
      <div className="tv-chart__header">
        <div>
          <div className="tv-chart__title">
            <span className="tv-chart__badge">{pair || 'Symbol'}</span>
            <span className="tv-chart__badge tv-chart__badge-muted">{timeframe || 'Timeframe'}</span>
            {shouldUseSampleData && <span className="tv-chart__badge tv-chart__badge-muted">Sample</span>}
          </div>
          {lastCandle && (
            <div className="tv-chart__ohlc">
              <span>O {formatPrice(lastCandle.open)}</span>
              <span>H {formatPrice(lastCandle.high)}</span>
              <span>L {formatPrice(lastCandle.low)}</span>
              <span>C {formatPrice(lastCandle.close)}</span>
              <span className={changeClass}>
                {changeLabel} ({formatPercent(changePercent)})
              </span>
            </div>
          )}
        </div>
        {lastCandle && (
          <div className={`tv-chart__price ${changeClass}`}>
            {formatPrice(lastCandle.close)}
          </div>
        )}
      </div>

      <div className="tv-chart__canvas" ref={containerRef} />

      {loading && (
        <div className="tv-chart__state">
          <div className="tv-chart__loader" />
          <span>Loading market data...</span>
        </div>
      )}

      {!loading && candleData.length === 0 && (
        <div className="tv-chart__state">
          <span>No candlestick data available.</span>
        </div>
      )}

      {tooltip && (
        <div
          className="tv-chart__tooltip"
          style={{ left: tooltip.left, top: tooltip.top }}
        >
          <div className="tv-chart__tooltip-header">
            <span>{tooltip.label}</span>
            <span className={tooltip.isBullish ? 'tv-chart__price-up' : 'tv-chart__price-down'}>
              {tooltip.isBullish ? 'Bullish' : 'Bearish'}
            </span>
          </div>
          <div className="tv-chart__tooltip-grid">
            <span>Open</span>
            <span>{formatPrice(tooltip.open)}</span>
            <span>High</span>
            <span>{formatPrice(tooltip.high)}</span>
            <span>Low</span>
            <span>{formatPrice(tooltip.low)}</span>
            <span>Close</span>
            <span>{formatPrice(tooltip.close)}</span>
            <span>Volume</span>
            <span>{formatNumber(tooltip.volume)}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default TradingChart