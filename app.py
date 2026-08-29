import streamlit as st
import requests
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Binance Pro Signal Center", 
    page_icon="⚡", 
    layout="centered"
)

# Initialize Session State
if "tp1_pct" not in st.session_state:
    st.session_state["tp1_pct"] = 2.0
if "tp2_pct" not in st.session_state:
    st.session_state["tp2_pct"] = 4.0
if "sl_pct" not in st.session_state:
    st.session_state["sl_pct"] = 2.0

# Fetch Top USDT Pairs safely
@st.cache_data(ttl=3600)
def get_binance_usdt_pairs():
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            symbols = [
                s['symbol'].replace('USDT', '/USDT') 
                for s in data['symbols'] 
                if s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING'
            ]
            if symbols:
                return sorted(symbols)
    except Exception:
        pass
    return [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
        "APT/USDT", "ADA/USDT", "DOGE/USDT", "PEPE/USDT", "AVAX/USDT"
    ]

# Fetch Live Market Data safely
def fetch_live_market_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            return float(data["lastPrice"]), float(data["priceChangePercent"]), float(data["highPrice"]), float(data["lowPrice"])
    except Exception:
        pass
    return 100.0, 1.0, 105.0, 95.0

# UI Header
st.markdown("""
<div style="background: linear-gradient(135deg, #1E2329 0%, #0B0E11 100%); padding: 20px; border-radius: 16px; border: 1px solid #F0B90B; margin-bottom: 20px; text-align: center;">
    <h1 style="color: #F0B90B; margin: 0; font-size: 24px;">⚡ BINANCE PRO SIGNAL CENTER</h1>
    <p style="color: #848E9C; margin: 5px 0 0 0; font-size: 13px;">Live Crypto Signals & Analysis</p>
</div>
""", unsafe_allow_html=True)

# Main Controls
all_coins = get_binance_usdt_pairs()
selected_pair = st.selectbox("Coin Pair එක තෝරන්න:", all_coins)
tv_symbol = selected_pair.replace("/", "")

# Fetch Data
current_price, price_change_pct, high_price, low_price = fetch_live_market_data(tv_symbol)

# Trend & Signal Determination
if price_change_pct >= 0:
    signal_badge, signal_bg = "BUY 📈", "#0ECB81"
    trend_text, trend_color = "Bullish Momentum", "#0ECB81"
    is_buy = True
else:
    signal_badge, signal_bg = "SELL 📉", "#F6465D"
    trend_text, trend_color = "Bearish Momentum", "#F6465D"
    is_buy = False

# Targets Calculation
tp1_ratio = st.session_state["tp1_pct"] / 100.0
tp2_ratio = st.session_state["tp2_pct"] / 100.0
sl_ratio = st.session_state["sl_pct"] / 100.0

if is_buy:
    tp1 = current_price * (1 + tp1_ratio)
    tp2 = current_price * (1 + tp2_ratio)
    sl = current_price * (1 - sl_ratio)
else:
    tp1 = current_price * (1 - tp1_ratio)
    tp2 = current_price * (1 - tp2_ratio)
    sl = current_price * (1 + sl_ratio)

# Signal Card Display
signal_card_html = f"""
<div style="background: #181A20; padding: 20px; border-radius: 14px; border: 1px solid #2B313A; color: white;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="color: #848E9C; font-size: 12px;">BINANCE SPOT</span>
            <h2 style="margin: 2px 0 0 0; color: #F0B90B; font-size: 28px;">{selected_pair}</h2>
            <p style="margin: 4px 0 0 0; color: {trend_color}; font-size: 13px;">● {trend_text}</p>
        </div>
        <div style="background: {signal_bg}; color: white; padding: 10px 20px; border-radius: 10px; font-weight: bold; font-size: 16px;">
            {signal_badge}
        </div>
    </div>
    <hr style="border: 0.5px solid #2B313A; margin: 15px 0;">
    <div style="display: flex; justify-content: space-between; text-align: center;">
        <div>
            <span style="color: #848E9C; font-size: 11px;">ENTRY PRICE</span>
            <h3 style="margin: 4px 0 0 0; font-size: 16px;">${current_price:,.4f}</h3>
        </div>
        <div>
            <span style="color: #848E9C; font-size: 11px;">24H CHANGE</span>
            <h3 style="margin: 4px 0 0 0; color: {trend_color}; font-size: 16px;">{price_change_pct:+.2f}%</h3>
        </div>
        <div>
            <span style="color: #848E9C; font-size: 11px;">24H HIGH</span>
            <h3 style="margin: 4px 0 0 0; font-size: 16px;">${high_price:,.4f}</h3>
        </div>
    </div>
    <hr style="border: 0.5px solid #2B313A; margin: 15px 0;">
    <div style="display: flex; justify-content: space-between; gap: 10px;">
        <div style="background: rgba(14, 203, 129, 0.1); border: 1px solid #0ECB81; padding: 10px; border-radius: 8px; flex: 1; text-align: center;">
            <span style="color: #0ECB81; font-size: 11px;">TP 1 (+{st.session_state['tp1_pct']}%)</span>
            <h4 style="margin: 4px 0 0 0; color: #FFF; font-size: 14px;">${tp1:,.4f}</h4>
        </div>
        <div style="background: rgba(14, 203, 129, 0.1); border: 1px solid #0ECB81; padding: 10px; border-radius: 8px; flex: 1; text-align: center;">
            <span style="color: #0ECB81; font-size: 11px;">TP 2 (+{st.session_state['tp2_pct']}%)</span>
            <h4 style="margin: 4px 0 0 0; color: #FFF; font-size: 14px;">${tp2:,.4f}</h4>
        </div>
        <div style="background: rgba(246, 70, 93, 0.1); border: 1px solid #F6465D; padding: 10px; border-radius: 8px; flex: 1; text-align: center;">
            <span style="color: #F6465D; font-size: 11px;">SL (-{st.session_state['sl_pct']}%)</span>
            <h4 style="margin: 4px 0 0 0; color: #FFF; font-size: 14px;">${sl:,.4f}</h4>
        </div>
    </div>
</div>
"""
st.markdown(signal_card_html, unsafe_allow_html=True)

# Settings Section
st.markdown("---")
st.subheader("⚙️ Settings")
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.session_state["tp1_pct"] = st.number_input("TP 1 (%)", 0.5, 20.0, st.session_state["tp1_pct"], 0.5)
with col_s2:
    st.session_state["tp2_pct"] = st.number_input("TP 2 (%)", 1.0, 30.0, st.session_state["tp2_pct"], 0.5)
with col_s3:
    st.session_state["sl_pct"] = st.number_input("Stop Loss (%)", 0.5, 15.0, st.session_state["sl_pct"], 0.5)
