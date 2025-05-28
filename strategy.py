import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# Train a basic RandomForest for filtering
X_train = pd.DataFrame({
    'ema_diff': np.random.randn(500),
    'rsi': np.random.uniform(30, 70, 500),
    'fvg': np.random.randint(0, 2, 500)
})
y_train = ((X_train['ema_diff'] > 0) & (X_train['rsi'] < 60) & (X_train['fvg'] == 1)).astype(int)
model = RandomForestClassifier()
model.fit(X_train, y_train)

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
    df['FVG'] = (df['High'] - df['Low']) > (df['High'] - df['Close'].shift(1))
    df['Support'] = df['Low'].rolling(window=20).min()
    df['Resistance'] = df['High'].rolling(window=20).max()
    df = df.dropna()
    return df

def compute_fib_level(df):
    high = df['High'].max()
    low = df['Low'].min()
    last = df['Close'].iloc[-1]
    retrace = (last - low) / (high - low)
    return round(retrace, 3)

def in_supply_zone(latest, df):
    recent_highs = df['High'].rolling(10).max()
    return bool(latest['Close'] > recent_highs.iloc[-1] * 0.98)

def evaluate_signal(df, symbol):
    df = calculate_indicators(df)
    if df.empty or len(df) < 250:
        return None

    latest = df.iloc[-1]
    ema50, ema200 = float(latest['EMA50']), float(latest['EMA200'])
    rsi = float(latest['RSI'])
    fvg = int(latest['FVG'])

    features = pd.DataFrame([{
        'ema_diff': ema50 - ema200,
        'rsi': rsi,
        'fvg': fvg
    }])
    prob = model.predict_proba(features)[0][1]
    if prob < 0.6:
        return None

    direction = "Buy" if ema50 > ema200 else "Sell"
    entry = float(latest['Close'])
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
    trades = []
    for sym in symbols:
        df = fetch_data(sym)
        if df is not None:
            trade = evaluate_signal(df, sym)
            if trade:
                trades.append(trade)
    return trades

def get_metrics(trades):
    total = len(trades)
    wins = [t for t in trades if t['status'] == "TP Hit"]
    pnl = sum(t['pnl'] for t in trades)
    win_rate = round((len(wins) / total) * 100, 2) if total else 0
    return {"total": total, "win_rate": win_rate, "net_pnl": round(pnl, 2)}

def autonomous_trading_insights():
    symbols = ["XAUUSD=X", "EURUSD=X", "GBPUSD=X", "^DJI", "^NDX"]
    insights = []
    for sym in symbols:
        df = fetch_data(sym)
        if df is None or df.empty:
            continue
        df = calculate_indicators(df)
        latest = df.iloc[-1]
        ema50, ema200 = float(latest['EMA50']), float(latest['EMA200'])
        rsi = float(latest['RSI'])
        fib_level = compute_fib_level(df)
        supply_zone = in_supply_zone(latest, df)

        features = pd.DataFrame([{
            'ema_diff': ema50 - ema200,
            'rsi': rsi,
            'fvg': int(latest['FVG'])
        }])
        prob = model.predict_proba(features)[0][1]
        decision = "Buy" if prob > 0.6 and ema50 > ema200 else "Sell" if prob > 0.6 else "Hold"

        insights.append({
            "symbol": sym,
            "EMA50": round(ema50, 2),
            "EMA200": round(ema200, 2),
            "RSI": round(rsi, 2),
            "FibLevel": fib_level,
            "SupplyZone": supply_zone,
            "AI_Score": round(prob, 2),
            "Decision": decision
        })
    return insights
