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
    'What is risk management?',
    'Tell me about XAU/USD',
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
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-gradient-to-br from-bullish to-gold text-dark-bg flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 transition animate-float"
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div
          className={`fixed bottom-20 right-6 z-50 w-96 glass border border-gray-700 rounded-lg shadow-2xl transition-all ${
            isMinimized ? 'h-14' : 'h-96'
          }`}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gradient-to-r from-bullish/10 to-gold/10">
            <div className="flex items-center gap-2">
              <MessageCircle size={18} className="text-gold" />
              <h3 className="font-semibold">AI Trading Assistant</h3>
            </div>
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 hover:bg-dark-card rounded transition"
            >
              {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
            </button>
          </div>

          {/* Messages */}
          {!isMinimized && (
            <>
              <div className="h-56 overflow-y-auto p-4 space-y-4 bg-dark-bg">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                        msg.sender === 'user'
                          ? 'bg-bullish text-dark-bg font-semibold'
                          : 'bg-dark-card border border-gray-700 text-gray-200'
                      }`}
                    >
                      {msg.text}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-dark-card border border-gray-700 px-4 py-2 rounded-lg">
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
              {messages.length <= 2 && (
                <div className="p-3 border-t border-gray-700 space-y-2">
                  <p className="text-xs text-gray-400 uppercase font-semibold">Quick Questions</p>
                  <div className="grid grid-cols-2 gap-2">
                    {quickQuestions.map((q, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(q)}
                        className="text-xs p-2 bg-dark-card hover:bg-gray-700 rounded border border-gray-700 transition"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Input */}
              <div className="p-3 border-t border-gray-700 flex gap-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask anything..."
                  className="flex-1 px-3 py-2 bg-dark-card border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-gold"
                  disabled={loading}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={loading || !inputValue.trim()}
                  className="p-2 bg-bullish text-dark-bg rounded-lg hover:bg-bullish/90 disabled:opacity-50 disabled:cursor-not-allowed transition"
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
