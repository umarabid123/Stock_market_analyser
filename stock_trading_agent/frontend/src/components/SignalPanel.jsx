import React from 'react'
import { MessageCircle, AlertCircle } from 'lucide-react'
import { getSignalColor, getSignalBgColor } from '../utils/formatters'

function SignalPanel({ result }) {
  return (
    <div className={`glass border border-gray-700 rounded-lg p-6 ${getSignalBgColor(result.signal)}`}>
      <div className="flex items-start gap-4">
        {/* Left: Signal Display */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-3">
            <MessageCircle size={20} className="text-gold" />
            <h3 className="text-lg font-semibold">Trading Signal</h3>
          </div>

          <p className={`text-4xl font-bold mb-2 ${getSignalColor(result.signal)}`}>
            {result.signal}
          </p>

          <div className="mb-4 space-y-1">
            <p className="text-sm text-gray-300">
              <span className="font-semibold">Confidence:</span>{' '}
              <span className="text-bullish">
                {(result.confidence * 100).toFixed(1)}%
              </span>
            </p>
            <p className="text-sm text-gray-300">
              <span className="font-semibold">Probability:</span>{' '}
              <span className="text-white">
                Probability-based signal
              </span>
            </p>
          </div>

          {/* Reason Box */}
          <div className="mt-4 p-3 bg-dark-card/50 rounded border border-gray-700">
            <p className="text-xs text-gray-400 uppercase font-semibold mb-1">Analysis Reason</p>
            <p className="text-sm text-gray-200 leading-relaxed">
              {result.reason || 'Analyzing market conditions...'}
            </p>
          </div>
        </div>

        {/* Right: Educational Note */}
        <div className="hidden md:block w-48 p-4 bg-yellow-900/20 border border-yellow-700/50 rounded-lg">
          <div className="flex items-start gap-2 mb-2">
            <AlertCircle size={16} className="text-yellow-500 flex-shrink-0 mt-0.5" />
            <p className="text-xs font-semibold text-yellow-200 uppercase">Educational Use</p>
          </div>
          <p className="text-xs text-yellow-100 leading-relaxed">
            This signal is for educational purposes. Use proper risk management and never risk more than
            you can afford to lose.
          </p>
        </div>
      </div>
    </div>
  )
}

export default SignalPanel
