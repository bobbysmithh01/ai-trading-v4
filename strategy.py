
import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_data(symbol, period="7d", interval="15m"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        return df if not df.empty else None
    except:
        return None

def evaluate_signal(df, symbol="UNKNOWN"):
    if df is None or df.empty or len(df) < 200:
        return None

    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    df = df.dropna()

    if df.empty:
        return None

    latest = df.iloc[-1]

    try:
        ema_50 = float(latest["EMA50"])
        ema_200 = float(latest["EMA200"])
        direction = "Buy" if ema_50 > ema_200 else "Sell"
    except Exception as e:
        print("Error comparing EMA values:", e)
        return None

    return {
        "symbol": symbol,
        "price": float(latest["Close"]),
        "direction": direction,
        "timestamp": str(latest.name)
    }


def autonomous_trading_loop():
    symbols = ["XAUUSD=X", "^DJI", "^NDX", "EURUSD=X", "GBPUSD=X"]
    all_signals = []
    for sym in symbols:
        df = fetch_data(sym)
        if df is not None:
            signal = evaluate_signal(df, symbol=sym)
            if signal:
                all_signals.append(signal)
    return all_signals

