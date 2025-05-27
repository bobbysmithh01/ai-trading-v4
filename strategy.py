
import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_data(symbol, period="7d", interval="15m"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        return df if not df.empty else None
    except:
        return None

def evaluate_signal(df):
    if df is None or df.empty:
        return None
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    latest = df.iloc[-1]
    if latest['EMA50'] > latest['EMA200']:
        direction = "Buy"
    else:
        direction = "Sell"
    return {
        "symbol": df.name,
        "price": round(latest["Close"], 2),
        "direction": direction,
        "timestamp": str(latest.name)
    }

def autonomous_trading_loop():
    symbols = ["XAUUSD=X", "^DJI", "^NDX", "EURUSD=X", "GBPUSD=X"]
    all_signals = []
    for sym in symbols:
        df = fetch_data(sym)
        if df is not None:
            df.name = sym
            signal = evaluate_signal(df)
            if signal:
                all_signals.append(signal)
    return all_signals
