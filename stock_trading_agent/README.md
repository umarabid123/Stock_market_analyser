# AI Forex & Commodity Trading Assistant

A professional full-stack AI-powered trading analysis platform for forex, commodities, and cryptocurrency. Built with **React + Vite** frontend and **FastAPI** backend.

> ⚠️ **DISCLAIMER**: This is an educational and research tool only. It does NOT provide financial advice and does NOT guarantee profit. Use for paper trading and learning purposes only.

---

## 🎯 Features

✅ **Real-time Market Analysis**
- Multi-timeframe technical analysis (5m, 15m, 1h, 4h, 1d)
- AI-powered BUY/SELL/HOLD/WAIT signals
- Confidence scoring (0-100%)

✅ **Professional Dashboard**
- Modern glassmorphism UI with dark theme
- Real-time candlestick charts
- Market bias and trend analysis
- Support/resistance zones

✅ **Risk Management**
- ATR-based stop loss calculations
- Risk/Reward ratios (1:2, 1:3 levels)
- Position sizing recommendations

✅ **Chatbot Assistant**
- Educational Q&A about signals
- Trading concepts explained
- Real-time market explanations

✅ **Supported Assets**
- **Forex**: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD
- **Commodities**: Gold (XAU/USD), Silver (XAG/USD), Oil, Natural Gas
- **Crypto**: BTC/USD, ETH/USD, XRP/USD, ADA/USD

✅ **Market Data Sources**
- Primary: TwelveData API
- Fallback: yfinance
- Support for OANDA, Alpha Vantage, Finnhub

---

## 🏗️ Project Structure

```
project-root/
├── backend/                    # FastAPI server
│   ├── app.py                 # FastAPI main server
│   ├── config.py              # Configuration & settings
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── market_data.py     # Data fetching (TwelveData, yfinance)
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   ├── indicators.py      # Technical indicators
│   │   └── sentiment.py       # News sentiment analysis
│   │
│   ├── strategy/
│   │   ├── __init__.py
│   │   └── signal_engine.py   # Signal generation logic
│   │
│   ├── risk/
│   │   ├── __init__.py
│   │   └── risk_manager.py    # Risk management & ATR
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── predictor.py       # ML prediction model
│   │
│   └── assistant/
│       ├── __init__.py
│       └── chatbot.py         # Chatbot responses
│
├── frontend/                   # React + Vite
│   ├── package.json           # Dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── tailwind.config.js     # Tailwind CSS config
│   ├── postcss.config.js      # PostCSS config
│   ├── .env.example           # Environment template
│   ├── index.html             # HTML entry point
│   │
│   └── src/
│       ├── main.jsx           # React entry point
│       ├── App.jsx            # Main app component
│       │
│       ├── api/
│       │   └── marketApi.js   # API client (Axios)
│       │
│       ├── components/
│       │   ├── Navbar.jsx     # Top navigation bar
│       │   ├── Sidebar.jsx    # Left sidebar (controls)
│       │   ├── MainDashboard.jsx
│       │   ├── MarketCards.jsx
│       │   ├── TradingChart.jsx
│       │   ├── SignalPanel.jsx
│       │   ├── RiskPanel.jsx
│       │   ├── TrendTable.jsx
│       │   └── Chatbot.jsx    # Floating chat
│       │
│       ├── styles/
│       │   └── global.css     # Global Tailwind styles
│       │
│       └── utils/
│           └── formatters.js  # Number/price formatting
│
├── README.md                   # This file
└── .gitignore                 # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- Git

### Setup

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

**2. Backend Setup**

```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
```

**3. Frontend Setup**

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
```

**4. Run Backend**

```bash
# From backend directory (with venv activated)
cd backend
uvicorn app:app --reload --port 8000
```

Backend will run on: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

**5. Run Frontend**

```bash
# From frontend directory (new terminal)
cd frontend
npm run dev
```

Frontend will run on: **http://localhost:5173**

---

## 📡 API Endpoints

### Health Check
```
GET /api/health
```

### Analyze Market
```
POST /api/analyze
{
  "symbol": "EUR/USD",
  "timeframe": "15m",
  "lookback": "5d"
}
```

**Response** includes: `signal`, `confidence`, `market_bias`, `trends`, `risk` levels, `support_zone`, `resistance_zone`

### Get Candles
```
GET /api/candles?symbol=EUR/USD&timeframe=15m&lookback=5d
```

### Chat
```
POST /api/chat
{
  "message": "What does BUY mean?",
  "current_result": {...}
}
```

---

## 🛠️ Configuration

### Backend `.env` File

```env
# API Keys
TWELVEDATA_API_KEY=your_api_key
OANDA_API_KEY=your_oanda_key
FINNHUB_API_KEY=your_finnhub_key

# Data Provider
DATA_PROVIDER=auto

# Defaults
DEFAULT_MARKET=Forex
DEFAULT_PAIR=EUR/USD
DEFAULT_LOOKBACK=5d
DEFAULT_TIMEFRAME=15m

# Safety
PAPER_TRADING_ONLY=true

# Frontend
FRONTEND_URL=http://localhost:5173
```

### Frontend `.env` File

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📊 Signals Explained

| Signal | Meaning |
|--------|---------|
| **STRONG BUY** | Multiple timeframes aligned bullish |
| **BUY** | Bullish conditions detected |
| **WAIT_FOR_BUY** | Bullish bias, waiting for confirmation |
| **HOLD** | No clear setup |
| **WAIT_FOR_SELL** | Bearish bias, waiting for confirmation |
| **SELL** | Bearish conditions detected |
| **STRONG SELL** | Multiple timeframes aligned bearish |

---

## 📈 Technical Indicators Used

- **EMA 20, 50** - Exponential Moving Averages
- **SMA 200** - Simple Moving Average
- **RSI 14** - Relative Strength Index
- **MACD** - Moving Average Convergence Divergence
- **ATR 14** - Average True Range (risk management)
- **Volume** - Trading volume analysis
- **Support/Resistance** - Key price levels

---

## ⚙️ Data Providers

Automatic fallback order:
1. **TwelveData** (Primary) - Forex-specialized
2. **yfinance** (Free fallback) - Stocks & crypto

---

## 🎓 Learning Resources

- **Technical Analysis**: https://www.investopedia.com/
- **Forex Trading**: https://www.babypips.com/
- **Python**: https://docs.python.org/3/
- **React**: https://react.dev/
- **FastAPI**: https://fastapi.tiangolo.com/

---

## ⚖️ Disclaimer

**IMPORTANT NOTICE:**

This tool is provided for **educational and research purposes only**.

- **No Guarantees**: Signals may not be accurate
- **Risk Disclosure**: You can lose money trading
- **Paper Trading Only**: Never use real money without backtesting
- **Always Use Risk Management**: Stop losses, position sizing, etc.
- **Not Financial Advice**: Do your own research

By using this tool, you agree to these terms and use it responsibly.
