import pandas as pd
from mt5_live_trading_engine import get_symbol_price, close_trade_if_needed, place_trade

model = None  # Placeholder for future AI model integration

def calculate_indicators(df):
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    df['RSI'] = 100 - (100 / (1 + df['Close'].pct_change().rolling(14).mean()))
    df = df.dropna()
    return df

def evaluate_trade(symbol):
    df = get_symbol_price(symbol, lookback=250)
    if df is None or df.empty:
        return None

    df = calculate_indicators(df)
    latest = df.iloc[-1]
    ema_diff = latest['EMA50'] - latest['EMA200']
    direction = "Buy" if ema_diff > 0 else "Sell"
    entry = round(latest['Close'], 4)

    sl = round(entry - 0.0050, 4) if direction == "Buy" else round(entry + 0.0050, 4)
    tp = round(entry + 0.0100, 4) if direction == "Buy" else round(entry - 0.0100, 4)
    rr = round(abs(tp - entry) / abs(entry - sl), 2)

    return {
        "symbol": symbol,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "rr": rr,
        "direction": direction,
        "status": "Running",
        "pnl": 0.0
    }

def autonomous_trading_loop(selected_accounts):
    symbols = ["EURUSD", "XAUUSD", "GBPUSD", "US30", "NAS100"]
    trades = []
    for symbol in symbols:
        trade = evaluate_trade(symbol)
        if trade:
            for acc in selected_accounts:
                place_trade(symbol, trade['direction'], acc, trade['entry'], trade['tp'], trade['sl'])
            trades.append(trade)
    return trades

def get_metrics(trades):
    total = len(trades)
    closed = [t for t in trades if t['status'] != "Running"]
    wins = [t for t in closed if t['status'] == "TP Hit"]
    pnl = sum([t['pnl'] for t in trades])
    win_rate = round((len(wins) / len(closed)) * 100, 2) if closed else 0
    return {"total": total, "win_rate": win_rate, "net_pnl": round(pnl, 1)}

