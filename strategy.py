import yfinance as yf
import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Simulated trade log for demo purposes
trade_log = []

def fetch_data(symbol, period="7d", interval="15m"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        return df if not df.empty else None
    except:
        return None

def calculate_indicators(df):
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    df['RSI'] = 100 - (100 / (1 + df['Close'].pct_change().rolling(14).mean()))
    df['FVG'] = (df['High'] - df['Low']) > (df['High'] - df['Close'].shift(1))  # Simple gap logic
    df['Support'] = df['Low'].rolling(window=20).min()
    df['Resistance'] = df['High'].rolling(window=20).max()
    df = df.dropna()
    return df

def train_filter_model():
    # Simulate some training data for the model
    X = pd.DataFrame({
        'ema_diff': np.random.randn(1000),
        'rsi': np.random.uniform(20, 80, 1000),
        'fvg': np.random.randint(0, 2, 1000),
    })
    y = (X['ema_diff'] > 0) & (X['rsi'] < 70) & (X['fvg'] == 1)
    y = y.astype(int)
    model = RandomForestClassifier()
    model.fit(X, y)
    return model

model = train_filter_model()

def evaluate_signal(df, symbol):
    df = calculate_indicators(df)
    if df.empty or len(df) < 250:
        return None

    latest = df.iloc[-1]
    ema_diff = float(latest["EMA50"] - latest["EMA200"])
    rsi = float(latest["RSI"])
    fvg = int(latest["FVG"])

    features = pd.DataFrame([{
        'ema_diff': ema_diff,
        'rsi': rsi,
        'fvg': fvg
    }])

    prediction = model.predict(features)[0]
    if prediction == 0:
        return None  # Skip low-probability trades

    direction = "Buy" if ema_diff > 0 else "Sell"
    entry = float(latest["Close"])
    sl = entry - 0.01 * entry if direction == "Buy" else entry + 0.01 * entry
    tp = entry + 0.02 * entry if direction == "Buy" else entry - 0.02 * entry
    rr = round(abs(tp - entry) / abs(entry - sl), 2)

    return {
        "symbol": symbol,
        "entry": round(entry, 2),
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "rr": rr,
        "timestamp": str(latest.name),
        "direction": direction,
        "status": "Running",
        "pnl": 0.0
    }

def autonomous_trading_loop():
    symbols = ["XAUUSD=X", "EURUSD=X", "GBPUSD=X", "^DJI", "^NDX"]
    new_trades = []
    for sym in symbols:
        df = fetch_data(sym)
        if df is not None:
            trade = evaluate_signal(df, symbol=sym)
            if trade:
                new_trades.append(trade)
    return new_trades

def get_metrics(trades):
    total = len(trades)
    wins = [t for t in trades if t['status'] == "TP Hit"]
    net_pnl = sum([t['pnl'] for t in trades])
    win_rate = round((len(wins) / total) * 100, 2) if total else 0
    return {
        "total": total,
        "win_rate": win_rate,
        "net_pnl": round(net_pnl, 2)
    }
    
def autonomous_trading_insights():
    """
    Return a list of dicts, each containing:
     - symbol
     - EMA50, EMA200, RSI
     - Fib retracement level (if within a threshold)
     - Supply/Demand zone flag
     - AI probability score
     - decision ("Buy"/"Sell"/"Hold")
    """
    insights = []
    for sym in symbols:
        df = fetch_data(sym)
        if df is None or df.empty:
            continue
        df = calculate_indicators(df)
        latest = df.iloc[-1]
        # compute features
        ema50, ema200, rsi = latest['EMA50'], latest['EMA200'], latest['RSI']
        # fib_level detection placeholder
        fib_level = compute_fib_level(df)   # you’d implement this helper
        supply_zone = in_supply_zone(latest, df)  # another helper
        # AI probability
        features = np.array([[ema50-ema200, rsi, int(fib_level==0.618), int(supply_zone)]])
        prob = model.predict_proba(features)[0,1]  # probability of a positive signal
        decision = "Buy" if prob > 0.6 and ema50>ema200 else "Sell" if prob > 0.6 else "Hold"
        insights.append({
            "symbol": sym,
            "EMA50": round(ema50,2),
            "EMA200": round(ema200,2),
            "RSI": round(rsi,2),
            "FibLevel": round(fib_level,3),
            "SupplyZone": supply_zone,
            "AI_Score": round(prob, 2),
            "Decision": decision
        })
    return insights
