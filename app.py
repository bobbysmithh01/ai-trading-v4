import streamlit as st
import json
import pandas as pd
import threading
import time
from strategy import autonomous_trading_loop, get_metrics, autonomous_trading_insights
from telegram_bot import send_telegram_alert

st.set_page_config(page_title="AI Trading", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bot_active" not in st.session_state:
    st.session_state.bot_active = False
if "trades" not in st.session_state:
    st.session_state.trades = []
if "bot_thread" not in st.session_state:
    st.session_state.bot_thread = None

# Auto-refreshing bot thread

def bot_loop():
    while st.session_state.bot_active:
        new_trades = autonomous_trading_loop()
        if new_trades:
            for trade in new_trades:
                st.session_state.trades.append(trade)
                send_telegram_alert(f"New Trade: {trade['symbol']} {trade['direction']} @ {trade['entry']} | SL: {trade['sl']} | TP: {trade['tp']}")
        time.sleep(60)

if not st.session_state.logged_in:
    with st.form("Login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            with open("users.json") as f:
                users = json.load(f)
            if username in users and users[username] == password:
                st.session_state.logged_in = True
            else:
                st.error("Invalid credentials")

if st.session_state.logged_in:
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()

    menu = st.radio("Menu", ["Live Trading", "Strategy Insights", "Accounts", "Feedback & Improvements"], horizontal=True)

    if menu == "Live Trading":
        st.header("Live Trading")
        toggle = st.toggle("Activate AI Bot", value=st.session_state.bot_active)
        if toggle and not st.session_state.bot_thread:
            st.session_state.bot_active = True
            t = threading.Thread(target=bot_loop, daemon=True)
            t.start()
            st.session_state.bot_thread = t
        elif not toggle:
            st.session_state.bot_active = False
            st.session_state.bot_thread = None

        st.subheader("📊 Performance Stats")
        metrics = get_metrics(st.session_state.trades)
        st.metric("Total Trades", metrics['total'])
        st.metric("Win Rate", f"{metrics['win_rate']}%")
        st.metric("Net PnL (pips)", metrics['net_pnl'])

        st.markdown("---")
        st.subheader("📈 Active & Closed Trades")
        for trade in reversed(st.session_state.trades):
            with st.container():
                st.markdown(f"**{trade['symbol']} - {trade['direction']}**")
                st.markdown(f"**Time:** {trade['timestamp']}")
                st.markdown(f"Entry: `{trade['entry']}` | SL: `{trade['sl']}` | TP: `{trade['tp']}` | R:R: `{trade['rr']}`")
                st.markdown(f"Status: `{trade['status']}` | Current PnL: `{trade['pnl']}` pips")
                st.markdown("---")

        st.subheader("📊 Live Charts")
        symbols = ["XAUUSD", "EURUSD", "GBPUSD", "DJI", "NDX"]
        for sym in symbols:
            st.markdown(f"#### {sym} Chart")
            st.components.v1.html(f"""
                <iframe src="https://s.tradingview.com/embed-widget/symbol-overview/?locale=en#%7B%22symbols%22%3A%5B%5B%22FOREXCOM%3A{sym}%22%5D%5D%2C%22width%22%3A%22100%25%22%2C%22height%22%3A"400"%7D" width="100%" height="400"></iframe>
            """, height=400)

    elif menu == "Strategy Insights":
        st.header("Strategy Insights (Real-Time)")
        insights = autonomous_trading_insights()
        if insights:
            df = pd.DataFrame(insights)
            st.dataframe(df)
        else:
            st.info("No insights available yet. Activate the bot to start scanning.")

    elif menu == "Accounts":
        st.header("Connected Accounts")
        st.info("Feature coming soon for client management and MT5 linking.")

    elif menu == "Feedback & Improvements":
        st.header("Feedback Form")
        feedback = st.text_area("Suggest an improvement or feature:")
        if st.button("Submit Feedback"):
            st.success("Feedback received — thank you!")
