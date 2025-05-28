import MetaTrader5 as mt5
import pandas as pd
import json

# Load account credentials
with open("accounts.json") as f:
    ACCOUNTS = json.load(f)

# Store connections
CONNECTED_ACCOUNTS = {}

# Initialize MT5 for each selected account
def initialize_mt5_accounts(selected):
    for name in selected:
        acc = ACCOUNTS.get(name)
        if acc and mt5.initialize(login=acc["login"], password=acc["password"], server=acc["server"]):
            CONNECTED_ACCOUNTS[name] = acc

# Shutdown MT5 on logout
def shutdown_mt5():
    mt5.shutdown()

# Get live price data

def get_symbol_price(symbol, lookback=250):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, lookback)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.set_index("time", inplace=True)
    return df

# Place trade

def place_trade(symbol, direction, account_label, entry, tp, sl, lot=0.1):
    acc = ACCOUNTS[account_label]
    price = mt5.symbol_info_tick(symbol).ask if direction == "buy" else mt5.symbol_info_tick(symbol).bid
    deviation = 10
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 123456,
        "comment": f"AI Bot - {account_label}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    return result

# Check and auto-close trade on TP/SL (simplified for later expansion)
def close_trade_if_needed(ticket, symbol, tp, sl, direction):
    tick = mt5.symbol_info_tick(symbol)
    price = tick.bid if direction == "buy" else tick.ask
    if direction == "buy" and (price >= tp or price <= sl):
        return mt5.order_close(ticket, mt5.positions_get(ticket=ticket)[0].volume, price, 10)
    if direction == "sell" and (price <= tp or price >= sl):
        return mt5.order_close(ticket, mt5.positions_get(ticket=ticket)[0].volume, price, 10)

# Get basic account info
def get_account_summary(account_label):
    acc = ACCOUNTS[account_label]
    if mt5.initialize(login=acc["login"], password=acc["password"], server=acc["server"]):
        info = mt5.account_info()._asdict()
        return {
            "Login": acc["login"],
            "Balance": info["balance"],
            "Equity": info["equity"],
            "Leverage": info["leverage"]
        }
    return {"error": "Unable to connect"}
