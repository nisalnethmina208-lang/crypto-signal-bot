import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Binance Crypto Signal Center", layout="wide")

# Fallback Top Coins List
TOP_COINS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", 
    "AVAXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "SHIBUSDT", "LTCUSDT", "TRXUSDT",
    "NEARUSDT", "APTUSDT", "SUIUSDT", "PEPEUSDT", "FETUSDT", "INJUSDT", "RNDRUSDT",
    "FILUSDT", "OPUSDT", "ARBUSDT", "ATOMUSDT", "WIFUSDT", "BONKUSDT", "FLOKIUSDT",
    "GALAUSDT", "FTMUSDT", "SANDUSDT", "MANAUSDT", "ALGOUSDT", "STXUSDT", "TIAUSDT"
]

@st.cache_data(ttl=3600)
def get_all_binance_symbols():
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5).json()
        symbols = [
            s['symbol'] for s in res.get('symbols', [])
            if s['symbol'].endswith('USDT') and s['status'] == 'TRADING'
            and not s['symbol'].endswith('UPUSDT') and not s['symbol'].endswith('DOWNUSDT')
        ]
        if symbols:
            symbols.sort()
            return symbols
        return TOP_COINS
    except Exception:
        return TOP_COINS

# Fetch Signal
@st.cache_data(ttl=10)
def get_live_signal(symbol="BTCUSDT", interval="15m"):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5).json()
        
        if not isinstance(res, list):
            return 0.0, "API LIMITED ⚠️", "#848e9c", "-", "-", "Binance Rate Limit"

        df = pd.DataFrame(res, columns=['time', 'open', 'high', 'low', 'close', 'volume', '_1', '_2', '_3', '_4', '_5', '_6'])
        df['close'] = df['close'].astype(float)
        
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
        
        if ema_cross_up or (bullish and latest['rsi'] < 60):
            signal = "BUY SIGNAL 🟢"
            color = "#0ecb81"
            tp = round(price * 1.02, 4)
            sl = round(price * 0.99, 4)
            reason = f"Bullish Trend (EMA20 > EMA50) | RSI: {round(latest['rsi'], 1)}"
        elif ema_cross_down or (not bullish and latest['rsi'] > 40):
            signal = "SELL SIGNAL 🔴"
            color = "#f6465d"
            tp = round(price * 0.98, 4)
            sl = round(price * 1.01, 4)
            reason = f"Bearish Trend (EMA20 < EMA50) | RSI: {round(latest['rsi'], 1)}"
        else:
            signal = "HOLD / NEUTRAL 🟡"
            color = "#f0b90b"
            tp = "-"
            sl = "-"
            reason = f"Market Consolidating | RSI: {round(latest['rsi'], 1)}"
            
        return price, signal, color, tp, sl, reason
    except Exception:
        return 0.0, "LOADING ERROR", "#848e9c", "-", "-", "Network issue"

# Header
st.markdown("<h2 style='text-align: center; color: #F0B90B;'>⚡ Binance Crypto Signal Center</h2>", unsafe_allow_html=True)

all_coins = get_all_binance_symbols()

# --- DEDICATED SEARCH BAR SECTION ---
search_query = st.text_input("🔍 Coin එකක් Search කරන්න (උදා: PEPE, BTC, SOL, ETH):", "").strip().upper()

# Filter coins based on search text
if search_query:
    filtered_coins = [c for c in all_coins if search_query in c]
    if not filtered_coins:
        st.warning(f"'{search_query}' නමින් Coin එකක් හමුවූයේ නැත. පහත ලැයිස්තුවෙන් තෝරන්න.")
        filtered_coins = all_coins
else:
    filtered_coins = all_coins

col1, col2 = st.columns(2)
with col1:
    selected_symbol = st.selectbox("Coin එක තෝරන්න", filtered_coins, index=0)
with col2:
    timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h"], index=2)

price, signal, color, tp, sl, reason = get_live_signal(selected_symbol, timeframe)

# Signal Box
st.markdown(f"""
<div style="background-color: #1e2329; border: 2px solid {color}; padding: 20px; border-radius: 12px; margin: 15px 0;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2 style="color: {color}; margin: 0;">{signal} ({selected_symbol})</h2>
        <h3 style="color: #ffffff; margin: 0;">මිල: ${price:,.4f}</h3>
    </div>
    <p style="color: #848e9c; font-size: 14px; margin-top: 8px;"><b>හේතුව:</b> {reason}</p>
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
