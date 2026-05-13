#!/usr/bin/env python
"""Simple test to confirm predictions are working."""

import pandas as pd
import numpy as np
from models.predictor import Predictor
from features.indicators import add_indicators

# Create 300 candles with uptrend
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=300, freq='1H')
prices = 100 + np.linspace(0, 5, 300) + np.random.randn(300) * 0.2

df = pd.DataFrame({
    'Open': prices,
    'High': prices + 0.3,
    'Low': prices - 0.3,
    'Close': prices,
    'Volume': np.random.randint(1000, 5000, 300),
}, index=dates)

# Add indicators and test
df_ind = add_indicators(df).dropna()
predictor = Predictor()

print("\n✓ PREDICTION TEST - UPTREND SCENARIO")
print("=" * 50)

pred = predictor.predict(df_ind)
print(f"Signal:     {pred['signal']}")
print(f"Confidence: {pred['confidence']:.1%}")
print(f"Bias:       {pred['bias']}")
print("\n" + "=" * 50)

if pred['signal'] in ['BUY', 'SELL', 'WAIT_FOR_BUY', 'WAIT_FOR_SELL']:
    print("✓ SUCCESS! Dynamic signals are now working!")
    print("✓ Backend is generating BUY/SELL/WAIT signals")
    print("✓ No more stuck 'HOLD' signals!")
else:
    print("✗ Still showing HOLD - needs more investigation")

print("\nRestart backend to apply these changes:")
print("  cd backend")
print("  uvicorn app:app --reload --port 8000")
