import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Crypto Live Signal Center", layout="wide")

TOP_COINS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", 
    "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TRXUSDT", "NEARUSDT", "APTUSDT", "SUIUSDT", 
    "PEPEUSDT", "FETUSDT", "INJUSDT", "FILUSDT", "OPUSDT", "ARBUSDT", "SHIBUSDT"
]

# Fetch Data from Binance Vision API (No Cloud IP Block)
@st.cache_data(ttl=5)
def get_live_signal(symbol="BTCUSDT", interval="15m"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    df = None
    error_msg = ""
    
    # 1. Primary Source: Binance Vision Official Public API
    try:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            raw_data = res.json()
            if isinstance(raw_data, list) and len(raw_data) > 0:
                df = pd.DataFrame(raw_data, columns=['time', 'open', 'high', 'low', 'close', 'volume', '_1', '_2', '_3', '_4', '_5', '_6'])
                df['close'] = df['close'].astype(float)
    except Exception as e:
        error_msg = str(e)

    # 2. Secondary Source: Bybit Spot API
    if df is None or df.empty:
        try:
            interval_map = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "4h": "240"}
            bybit_tf = interval_map.get(interval, "15")
            bybit_url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}&interval={bybit_tf}&limit=100"
            res_bybit = requests.get(bybit_url, headers=headers, timeout=5).json()
            if res_bybit.get("retCode") == 0 and res_bybit.get("result", {}).get("list"):
                df = pd.DataFrame(res_bybit["result"]["list"], columns=['time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
                df['close'] = df['close'].astype(float)
                df = df.iloc[::-1].reset_index(drop=True)
        except Exception:
            pass

    if df is None or df.empty:
        return 0.0, "සම්ප්‍රේෂණ දෝෂයකි ⚠️", "#848e9c", "-", "-", f"Data Error: {error_msg}"

    # Technical Indicators (EMA 20/50 & RSI 14)
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    price = latest['close']
    
    bullish = latest['ema20'] > latest['ema50']
    ema_cross_up = (prev['ema20'] <= prev['ema50']) and (latest['ema20'] > latest['ema50'])
    ema_cross_down = (prev['ema20'] >= prev['ema50']) and (latest['ema20'] < latest['ema50'])
    
    # Calculate Signal & Targets
    if ema_cross_up or (bullish and latest['rsi'] < 60):
        signal = "BUY SIGNAL (මාකට් එක UP වේ) 🟢"
        color = "#0ecb81"
        tp = round(price * 1.02, 4)
        sl = round(price * 0.99, 4)
        reason = f"Bullish Trend (EMA20 > EMA50) | RSI: {round(latest['rsi'], 1)}"
    elif ema_cross_down or (not bullish and latest['rsi'] > 40):
        signal = "SELL SIGNAL (මාකට් එක DOWN වේ) 🔴"
        color = "#f6465d"
        tp = round(price * 0.98, 4)
        sl = round(price * 1.01, 4)
        reason = f"Bearish Trend (EMA20 < EMA50) | RSI: {round(latest['rsi'], 1)}"
    else:
        signal = "HOLD / NEUTRAL (රඳවා තබාගන්න) 🟡"
        color = "#f0b90b"
        tp = "-"
        sl = "-"
        reason = f"Market Consolidating | RSI: {round(latest['rsi'], 1)}"
        
    return price, signal, color, tp, sl, reason

# Header
st.markdown("<h2 style='text-align: center; color: #F0B90B;'>⚡ Crypto Live Signal Center</h2>", unsafe_allow_html=True)

search_query = st.text_input("🔍 Coin එකක් Search කරන්න (උදා: TRX, BTC, SOL):", "").strip().upper()

filtered_coins = [c for c in TOP_COINS if search_query in c] if search_query else TOP_COINS
if not filtered_coins:
    filtered_coins = TOP_COINS

col1, col2 = st.columns(2)
with col1:
    selected_symbol = st.selectbox("Coin එක තෝරන්න", filtered_coins, index=0)
with col2:
    timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h"], index=2)

price, signal, color, tp, sl, reason = get_live_signal(selected_symbol, timeframe)

# Signal Display Box
st.markdown(f"""
<div style="background-color: #1e2329; border: 2px solid {color}; padding: 20px; border-radius: 12px; margin: 15px 0;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2 style="color: {color}; margin: 0;">{signal}</h2>
        <h3 style="color: #ffffff; margin: 0;">මිල: ${price:,.4f}</h3>
    </div>
    <p style="color: #848e9c; font-size: 14px; margin-top: 10px;"><b>හේතුව:</b> {reason}</p>
    <hr style="border: 0.5px solid #2b313a; margin: 15px 0;">
    <div style="display: flex; justify-content: space-around; text-align: center;">
        <div>
            <span style="color: #848e9c; font-size: 14px;">Take Profit (TP)</span><br>
            <b style="color: #0ecb81; font-size: 22px;">${tp}</b>
        </div>
        <div>
            <span style="color: #848e9c; font-size: 14px;">Stop Loss (SL)</span><br>
            <b style="color: #f6465d; font-size: 22px;">${sl}</b>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Live TradingView Chart
tradingview_html = f"""
<div class="tradingview-widget-container" style="height:500px;width:100%;">
  <div id="tradingview_chart" style="height:100%;width:100%;"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
      "autosize": true,
      "symbol": "BINANCE:{selected_symbol}",
      "interval": "{timeframe.replace('m', '') if 'm' in timeframe else timeframe.replace('h', '60')}",
      "theme": "dark",
      "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
components.html(tradingview_html, height=500)
