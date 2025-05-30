import streamlit as st
import json
import pandas as pd
import threading
import time
from strategy import autonomous_trading_loop, get_metrics
from telegram_bot import send_telegram_alert

st.set_page_config(page_title="AI Trading", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bot_active" not in st.session_state:
    st.session_state.bot_active = False
if "trades" not in st.session_state:
    st.session_state.trades = []

def bot_loop():
    while st.session_state.bot_active:
        new_trades = autonomous_trading_loop()
        for trade in new_trades:
            st.session_state.trades.append(trade)
            send_telegram_alert(f"Signal: {trade['symbol']} {trade['direction']} @ {trade['entry']} | SL: {trade['sl']} | TP: {trade['tp']}")
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

    menu = st.radio("Menu", ["Live Trading", "Feedback"], horizontal=True)

    if menu == "Live Trading":
        st.header("Live Trading")
        toggle = st.toggle("Activate AI Bot", value=st.session_state.bot_active)
        if toggle and not st.session_state.bot_active:
            st.session_state.bot_active = True
            threading.Thread(target=bot_loop, daemon=True).start()
        elif not toggle:
            st.session_state.bot_active = False

        st.subheader("📊 Performance")
        metrics = get_metrics(st.session_state.trades)
        st.metric("Total Trades", metrics['total'])
        st.metric("Win Rate", f"{metrics['win_rate']}%")
        st.metric("Net PnL (pips)", metrics['net_pnl'])

        st.subheader("📈 Trade Log")
        for trade in reversed(st.session_state.trades):
            with st.container():
                st.markdown(f"**{trade['symbol']} - {trade['direction']}**")
                st.markdown(f"Entry: `{trade['entry']}` | SL: `{trade['sl']}` | TP: `{trade['tp']}` | R:R: `{trade['rr']}`")
                st.markdown(f"Status: `{trade['status']}` | PnL: `{trade['pnl']}` pips")
                st.markdown("---")

    elif menu == "Feedback":
        st.header("Feedback")
        feedback = st.text_area("Suggest improvements:")
        if st.button("Submit Feedback"):
            st.success("Thanks for your feedback!")
