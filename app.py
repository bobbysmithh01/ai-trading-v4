from strategy import autonomous_trading_loop, get_metrics, get_strategy_insights
import streamlit as st
import json
from strategy import autonomous_trading_loop, get_metrics
from telegram_bot import send_telegram_alert

st.set_page_config(page_title="AI Trading", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bot_active" not in st.session_state:
    st.session_state.bot_active = False
if "trades" not in st.session_state:
    st.session_state.trades = []

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

    st.sidebar.title("AI Trading")
    menu = st.sidebar.radio("Menu", ["Live Trading", "Strategy Insights", "Accounts", "Feedback & Improvements"])

    st.title("AI Trading Dashboard")
    st.markdown("---")

    if menu == "Live Trading":
        toggle = st.toggle("Activate AI Bot", value=st.session_state.bot_active)
        st.session_state.bot_active = toggle

        if toggle:
            new_trades = autonomous_trading_loop()
            if new_trades:
                for trade in new_trades:
                    st.session_state.trades.append(trade)
                    send_telegram_alert(f"New Trade: {trade['symbol']} {trade['direction']} @ {trade['entry']} | SL: {trade['sl']} | TP: {trade['tp']}")

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

    elif menu == "Accounts":
        st.subheader("Connected Accounts")
        st.info("Feature coming soon for client management and MT5 linking.")

    elif menu == "Feedback & Improvements":
        st.subheader("Feedback Form")
        feedback = st.text_area("Suggest an improvement or feature:")
        if st.button("Submit Feedback"):
            st.success("Feedback received — thank you!")
elif menu == "Strategy Insights":
+       st.subheader("Strategy Insights (Real-Time)")
+       insights = autonomous_trading_insights()  # new function
+       if insights:
+           df = pd.DataFrame(insights)
+           st.dataframe(df)  # shows columns: symbol, EMA50, EMA200, RSI, FibLevel, SupplyZone, AI_Score, Decision
+       else:
+           st.info("No insights available yet. Activate the bot to start scanning.")
