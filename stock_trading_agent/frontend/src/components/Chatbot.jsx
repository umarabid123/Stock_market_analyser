import React, { useState, useRef, useEffect } from 'react'
import { MessageCircle, Send, X, Minimize2, Maximize2 } from 'lucide-react'
import { sendChatMessage } from '../api/marketApi'

function Chatbot({ currentResult }) {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hi! I\'m your AI trading assistant. Ask me anything about trading signals, risk management, or forex education.',
      sender: 'bot',
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const quickQuestions = [
    'Explain current signal',
    'What is HOLD?',
    'Why risk is empty?',
    'What is XAU/USD?',
    'What is timeframe?',
    'How should beginner use this?',
  ]

  // Scroll to bottom
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Handle sending message
  const handleSendMessage = async (message = inputValue) => {
    if (!message.trim()) return

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: message,
      sender: 'user',
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      // Call API
      const response = await sendChatMessage(message, currentResult)
      const botMessage = {
        id: messages.length + 2,
        text: response.reply,
        sender: 'bot',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botMessage])
    } catch (error) {
      const errorMessage = {
        id: messages.length + 2,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="chatbot-fab w-16 h-16 rounded-full bg-gradient-to-br from-bullish to-gold text-dark-bg flex items-center justify-center shadow-2xl hover:shadow-[0_0_30px_rgba(0,255,136,0.5)] hover:scale-110 transition-smooth live-pulse"
      >
        {isOpen ? <X size={28} /> : <MessageCircle size={28} />}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div
          className={`chatbot-panel glass-lg border border-gray-700/50 rounded-xl shadow-2xl transition-all fade-in ${
            isMinimized ? 'h-16' : 'h-[500px]'
          }`}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-700/50 bg-gradient-to-r from-bullish/20 to-gold/10 rounded-t-xl">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-bullish/20 rounded-lg">
                <MessageCircle size={20} className="text-bullish" />
              </div>
              <div>
                <h3 className="font-bold text-white">AI Assistant</h3>
                <p className="text-xs text-gray-400">Trading support</p>
              </div>
            </div>
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1.5 hover:bg-bullish/10 rounded-lg transition-smooth text-gray-400 hover:text-bullish"
            >
              {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
            </button>
          </div>

          {/* Messages */}
          {!isMinimized && (
            <>
              <div className="chatbot-messages space-y-4 bg-dark-bg/50 p-4">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                        msg.sender === 'user'
                          ? 'bg-gradient-to-r from-bullish to-bullish-dark text-dark-bg rounded-br-none shadow-glow-bullish'
                          : 'bg-dark-card-light/70 border border-gray-700/50 text-gray-100 rounded-bl-none'
                      }`}
                    >
                      {msg.text}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-dark-card-light/70 border border-gray-700/50 px-4 py-3 rounded-lg rounded-bl-none">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 rounded-full bg-gold animate-bounce" />
                        <div
                          className="w-2 h-2 rounded-full bg-gold animate-bounce"
                          style={{ animationDelay: '0.1s' }}
                        />
                        <div
                          className="w-2 h-2 rounded-full bg-gold animate-bounce"
                          style={{ animationDelay: '0.2s' }}
                        />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Quick Questions */}
              <div className="chatbot-quick-questions bg-dark-card-light/30">
                <div className="space-y-2">
                  <p className="text-xs text-gray-400 uppercase font-bold tracking-widest">Quick Questions</p>
                  <div className="grid grid-cols-2 gap-2">
                    {quickQuestions.map((q, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(q)}
                        className="text-xs p-2 bg-dark-card-light/50 hover:bg-dark-card-light border border-gray-700/50 hover:border-bullish/50 rounded-lg font-medium transition-smooth text-gray-300 hover:text-bullish"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Input */}
              <div className="chatbot-input-area flex gap-2 bg-dark-card-light/30 rounded-b-xl">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask anything..."
                  className="flex-1 px-3 py-2 bg-dark-card-light/50 border border-gray-700/50 rounded-lg text-sm focus:outline-none focus:border-bullish focus:ring-1 focus:ring-bullish/50 text-gray-100 placeholder-gray-500 transition-smooth"
                  disabled={loading}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={loading || !inputValue.trim()}
                  className="p-2 bg-gradient-to-r from-bullish to-bullish-dark text-dark-bg rounded-lg hover:shadow-glow-bullish disabled:opacity-50 disabled:cursor-not-allowed transition-smooth font-semibold"
                >
                  <Send size={16} />
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  )
}

export default Chatbot
