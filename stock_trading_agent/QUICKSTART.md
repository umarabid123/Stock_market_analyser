# 🚀 Quick Start Guide - AI Forex Trading Assistant

Get the platform up and running in **5 minutes**.

---

## ⚡ Prerequisites

Before you start, make sure you have:

- ✅ **Python 3.10+** - [Download](https://www.python.org/downloads/)
- ✅ **Node.js 18+** & npm - [Download](https://nodejs.org/)
- ✅ **Git** - [Download](https://git-scm.com/)
- ✅ **API Key** (optional but recommended) - [TwelveData](https://twelvedata.com)

---

## 📋 Step 1: Clone & Navigate

```bash
# Clone repository
git clone <repository-url>
cd Stock_market_analyser/stock_trading_agent
```

---

## 🔧 Step 2: Backend Setup (Terminal 1)

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env

# Edit .env - Optional but recommended:
# - Add your TWELVEDATA_API_KEY
# - Default settings are fine for testing
```

**Note:** yfinance is included as a fallback, so API keys are optional for testing.

---

## 💻 Step 3: Frontend Setup (Terminal 2)

```bash
# Open NEW terminal window/tab
# Navigate to frontend folder
cd frontend

# Install Node dependencies
npm install

# Copy environment file
cp .env.example .env

# VITE_API_BASE_URL is already set correctly
```

---

## 🎯 Step 4: Start Backend

**From Terminal 1 (backend directory with venv activated):**

```bash
# Make sure you're in backend/ directory
cd backend

# Start FastAPI server
uvicorn app:app --reload --port 8000
```

✅ Backend running on: **http://localhost:8000**

📚 API Documentation: **http://localhost:8000/docs**

You should see:
```
Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🎨 Step 5: Start Frontend

**From Terminal 2 (frontend directory):**

```bash
# Make sure you're in frontend/ directory
cd frontend

# Start React development server
npm run dev
```

✅ Frontend running on: **http://localhost:5173**

You should see:
```
VITE v5.0.7  ready in 2345 ms

➜ Local:   http://localhost:5173/
```

---

## 🎮 Step 6: Use the Platform

1. **Open browser** → http://localhost:5173
2. **Left Sidebar:**
   - Select Market type: Forex / Commodities / Crypto
   - Choose trading pair: EUR/USD, XAU/USD, BTC/USD, etc.
   - Set timeframe: 5m, 15m, 1h, 4h, 1d
   - Set lookback: 1d, 5d, 1mo, 3mo
3. **Click "Analyze Market"** button
4. **View Results:**
   - Trading signal (BUY/SELL/HOLD/WAIT)
   - Confidence score
   - Multi-timeframe trends
   - Risk levels (Stop Loss, Take Profit)
   - Floating chatbot (bottom-right)

---

## 💬 Testing the Chatbot

Click the **💬 chat button** (bottom-right) to:
- Ask "What does BUY mean?"
- "Explain current signal"
- "What is XAU/USD?"
- Or type custom questions

---

## 🔗 API Testing (Optional)

Use **Swagger UI** at http://localhost:8000/docs

Try endpoints:
- **GET** `/api/health` - Check backend
- **POST** `/api/analyze` - Get market signal
- **GET** `/api/candles` - Get candlestick data
- **POST** `/api/chat` - Chat with bot

---

## ⚙️ Configuration

### Using API Keys (Optional but Recommended)

Edit `backend/.env`:

```env
# Get free key from https://twelvedata.com
TWELVEDATA_API_KEY=your_api_key_here

# Other API keys (optional)
OANDA_API_KEY=your_oanda_key
FINNHUB_API_KEY=your_finnhub_key

# Default settings
DEFAULT_PAIR=EUR/USD
DEFAULT_TIMEFRAME=15m
DEFAULT_LOOKBACK=5d
```

Reload backend after changes.

### Frontend Configuration

Edit `frontend/.env` (usually already correct):

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🛑 Stopping Servers

**Backend (Terminal 1):**
```bash
# Press CTRL+C
```

**Frontend (Terminal 2):**
```bash
# Press CTRL+C
```

---

## ❌ Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.10+

# Rebuild dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Try different port
uvicorn app:app --reload --port 8001
```

### Frontend won't start

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Try different port
npm run dev -- --port 3000
```

### "Cannot connect to backend"

1. Check if backend is running on port 8000
2. Check backend logs for errors
3. Try http://localhost:8000/api/health in browser
4. Check CORS settings in `backend/app.py`

### API key not working

- Verify key is correct in `.env`
- Check API quotas on provider's dashboard
- Try without key (yfinance fallback will work)

---

## 📚 Next Steps

1. **Explore Dashboard:**
   - Try different pairs (EUR/USD, XAU/USD, BTC/USD)
   - Change timeframes to see how signals change
   - Use different lookback periods

2. **Learn Signals:**
   - Read chatbot explanations
   - Understand BUY/SELL/HOLD/WAIT signals
   - Study risk management levels

3. **Read Documentation:**
   - Full README: `README.md`
   - API docs: http://localhost:8000/docs
   - Code comments in `/backend` and `/frontend/src`

4. **Customize:**
   - Add more pairs in `frontend/src/components/Sidebar.jsx`
   - Modify indicators in `backend/features/indicators.py`
   - Change default settings in `backend/config.py`

---

## ⚖️ Important Reminder

⚠️ **This is for educational purposes only!**

- No real money trading
- Not financial advice
- Signals are probability-based, not guaranteed
- Always use risk management
- Do your own research before trading

---

## 🆘 Need Help?

1. Check `backend` logs for errors
2. Check browser console (F12) for frontend errors
3. Review API documentation at `/docs`
4. Read full README.md
5. Check component comments in code

---

**Enjoy exploring AI-powered trading analysis! 📈**

Happy trading! 🚀
