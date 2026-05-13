#!/usr/bin/env python
"""Quick test script to verify predictions are working."""

import pandas as pd
from models.predictor import Predictor
from features.indicators import add_indicators
import numpy as np

# Create sample OHLCV data to test predictions
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=300, freq='15min')
close_prices = 100 + np.cumsum(np.random.randn(300) * 0.5)

df = pd.DataFrame({
    'Open': close_prices + np.random.randn(300) * 0.2,
    'High': close_prices + abs(np.random.randn(300) * 0.5),
    'Low': close_prices - abs(np.random.randn(300) * 0.5),
    'Close': close_prices,
    'Volume': np.random.randint(1000, 5000, 300),
}, index=dates)

print("=" * 60)
print("TESTING PREDICTOR WITH SAMPLE DATA")
print("=" * 60)

# Add indicators
df_with_indicators = add_indicators(df)
df_with_indicators = df_with_indicators.dropna()

print(f"\nData shape: {df_with_indicators.shape}")
print(f"Latest Close: {df_with_indicators.iloc[-1]['Close']:.2f}")
print(f"\nLast 3 rows of key indicators:")
print(df_with_indicators[['Close', 'EMA_20', 'EMA_50', 'SMA_200', 'RSI_14', 'MACD_HIST', 'Momentum_5']].tail(3))

# Test predictor
predictor = Predictor()
prediction = predictor.predict(df_with_indicators)

print("\n" + "=" * 60)
print("PREDICTION RESULTS:")
print("=" * 60)
print(f"Signal: {prediction['signal']}")
print(f"Confidence: {prediction['confidence']:.2%}")
print(f"Bias: {prediction['bias']}")
print(f"Reason: {prediction['reason']}")

# Test with bullish market
print("\n" + "=" * 60)
print("TESTING WITH BULLISH MARKET SCENARIO")
print("=" * 60)

bullish_prices = 100 + np.linspace(0, 10, 300)  # Uptrend
df_bullish = pd.DataFrame({
    'Open': bullish_prices + np.random.randn(300) * 0.1,
    'High': bullish_prices + abs(np.random.randn(300) * 0.3),
    'Low': bullish_prices - abs(np.random.randn(300) * 0.3),
    'Close': bullish_prices,
    'Volume': np.random.randint(2000, 6000, 300),
}, index=dates)

df_bullish_ind = add_indicators(df_bullish).dropna()
pred_bullish = predictor.predict(df_bullish_ind)

print(f"Signal: {pred_bullish['signal']}")
print(f"Confidence: {pred_bullish['confidence']:.2%}")
print(f"Reason: {pred_bullish['reason']}")

# Test with bearish market
print("\n" + "=" * 60)
print("TESTING WITH BEARISH MARKET SCENARIO")
print("=" * 60)

bearish_prices = 100 - np.linspace(0, 10, 300)  # Downtrend
df_bearish = pd.DataFrame({
    'Open': bearish_prices + np.random.randn(300) * 0.1,
    'High': bearish_prices + abs(np.random.randn(300) * 0.3),
    'Low': bearish_prices - abs(np.random.randn(300) * 0.3),
    'Close': bearish_prices,
    'Volume': np.random.randint(2000, 6000, 300),
}, index=dates)

df_bearish_ind = add_indicators(df_bearish).dropna()
pred_bearish = predictor.predict(df_bearish_ind)

print(f"Signal: {pred_bearish['signal']}")
print(f"Confidence: {pred_bearish['confidence']:.2%}")
print(f"Reason: {pred_bearish['reason']}")

print("\n" + "=" * 60)
print("✓ PREDICTION TESTS COMPLETE")
print("=" * 60)
print("\nNOTE: You should now see BUY/SELL signals instead of always HOLD!")
print("Make sure to restart the backend with: uvicorn app:app --reload")
