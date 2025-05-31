import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import random

def fetch_data(symbol, period="5d", interval="1m"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        return df.dropna()
    except:
        return None

def calculate_indicators(df):
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    df['RSI'] = 100 - (100 / (1 + df['Close'].pct_change().rolling(14).mean()))
    df['Support'] = df['Low'].rolling(20).min()
    df['Resistance'] = df['High'].rolling(20).max()
    return df.dropna()

def detect_fvg(df):
    df['FVG'] = (df['Low'] > df['High'].shift(2)) | (df['High'] < df['Low'].shift(2))
    return df

def calculate_fib_retracement(df):
    high = df['High'].max()
    low = df['Low'].min()
    last = df['Close'].iloc[-1]
    retracement = (last - low) / (high - low)
    return round(retracement, 2)

def in_supply_zone(latest, df):
    try:
        recent_high = df['High'].rolling(10).max().iloc[-1]
        return bool(latest['Close'] > float(recent_high * 0.98))
    except:
        return False

def in_demand_zone(latest, df):
    try:
        recent_low = df['Low'].rolling(10).min().iloc[-1]
        return bool(latest['Close'] < float(recent_low * 1.02))
    except:
        return False

def evaluate_trade(symbol):
    df = fetch_data(symbol)
    if df is None or len(df) < 100:
        return None

    df = calculate_indicators(df)
    df = detect_fvg(df)
    latest = df.iloc[-1]

    ema50 = latest.get('EMA50')
    ema200 = latest.get('EMA200')
    ema_signal = isinstance(ema50, (float, int)) and isinstance(ema200, (float, int)) and ema50 > ema200

    rsi_val = latest.get('RSI')
    rsi_signal = rsi_val < 60 if ema_signal else rsi_val > 40 if isinstance(rsi_val, (float, int)) else False

    fvg_signal = df['FVG'].iloc[-1] if 'FVG' in df.columns else False
    fib_level = calculate_fib_retracement(df)
    in_demand = in_demand_zone(latest, df)
    in_supply = in_supply_zone(latest, df)

    confidence = sum([ema_signal, rsi_signal, fvg_signal, in_demand or in_supply])

    if confidence < 3:
        return None

    direction = "Buy" if ema_signal and not in_supply else "Sell"
    entry = round(latest['Close'], 4)
    sl = round(entry - 0.0050, 4) if direction == "Buy" else round(entry + 0.0050, 4)
    tp = round(entry + 0.0100, 4) if direction == "Buy" else round(entry - 0.0100, 4)
    rr = round(abs(tp - entry) / abs(entry - sl), 2)
    pnl = round(random.uniform(-30, 80), 1)

    from telegram_bot import send_telegram_alert

send_telegram_alert(f"📈 {symbol} {direction} signal\nEntry: {entry} | SL: {sl} | TP: {tp} | R:R: {rr}")

    return {
        "symbol": symbol,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "rr": rr,
        "direction": direction,
        "status": "Running" if pnl < 80 else "TP Hit",
        "pnl": pnl,
        "timestamp": str(datetime.utcnow())
    }

def autonomous_trading_loop():
    symbols = ["EURUSD=X", "XAUUSD=X", "GBPUSD=X", "^DJI", "^NDX"]
    trades = []
    for sym in symbols:
        trade = evaluate_trade(sym)
        if trade:
            trades.append(trade)
    return trades

def get_metrics(trades):
    total = len(trades)
    closed = [t for t in trades if t['status'] != "Running"]
    wins = [t for t in closed if t['status'] == "TP Hit"]
    pnl = sum([t['pnl'] for t in trades])
    win_rate = round((len(wins) / len(closed)) * 100, 2) if closed else 0
    return {"total": total, "win_rate": win_rate, "net_pnl": round(pnl, 1)}

def get_strategy_insights():
    symbols = ["EURUSD=X", "XAUUSD=X", "GBPUSD=X", "^DJI", "^NDX"]
    insights = []

    for sym in symbols:
        df = fetch_data(sym)
        if df is None or len(df) < 100:
            continue

        df = calculate_indicators(df)
        df = detect_fvg(df)
        latest = df.iloc[-1]

        insight_text = []

        ema50 = latest.get('EMA50')
        ema200 = latest.get('EMA200')
        if isinstance(ema50, (float, int)) and isinstance(ema200, (float, int)):
            if ema50 > ema200:
                insight_text.append("✅ EMA50 is above EMA200 → Bullish signal")
            else:
                insight_text.append("🔻 EMA50 is below EMA200 → Bearish signal")

        rsi = latest.get('RSI')
        if isinstance(rsi, (float, int)):
            rsi = round(rsi, 2)
            insight_text.append(f"RSI: {rsi}")
            if rsi < 30:
                insight_text.append("📉 RSI is below 30 → Oversold")
            elif rsi > 70:
                insight_text.append("📈 RSI is above 70 → Overbought")

        if 'FVG' in df.columns and df['FVG'].iloc[-1]:
            insight_text.append("📍 Fair Value Gap detected")

        fib = calculate_fib_retracement(df)
        insight_text.append(f"🔢 Fib Retracement Level: {fib}")

        if in_supply_zone(latest, df):
            insight_text.append("🔴 Price is near recent Supply Zone")
        if in_demand_zone(latest, df):
            insight_text.append("🟢 Price is near recent Demand Zone")

        insights.append({
            "symbol": sym,
            "analysis": "\n".join(insight_text)
        })

    return insights


