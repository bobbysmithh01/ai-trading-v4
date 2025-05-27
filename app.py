
import streamlit as st
import json
import pandas as pd
import yfinance as yf
from strategy import autonomous_trading_loop
from telegram_bot import send_telegram_alert

st.set_page_config(page_title="AI Trading", layout="wide")

# LOGIN
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bot_active" not in st.session_state:
    st.session_state.bot_active = False

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
    # Top right corner: logout
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()
    st.sidebar.title("AI Trading")
    menu = st.sidebar.radio("Menu", ["Live Trading", "Accounts", "Feedback & Improvements"])

    st.title("AI Trading Dashboard")
    st.markdown("---")

    if menu == "Live Trading":
        toggle = st.toggle("Activate AI Bot", value=st.session_state.bot_active)
        st.session_state.bot_active = toggle
        if toggle:
            st.success("Bot is running and scanning markets...")
            trades = autonomous_trading_loop()
            if trades:
                st.write("Latest Trade Signal:")
                st.json(trades[-1])
        else:
            st.warning("Bot is paused.")

    elif menu == "Accounts":
        st.subheader("Connected Accounts")
        st.write("This section will let you manage trading accounts in the future.")

    elif menu == "Feedback & Improvements":
        st.subheader("Feedback Form")
        feedback = st.text_area("Suggest a feature, improvement, or report an issue:")
        if st.button("Submit Feedback"):
            st.success("Thank you! Your feedback has been recorded.")
