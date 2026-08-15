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

# Fetch Multi-Source Live Signal (Bybit Primary + Binance Backup)
@st.cache_data(ttl=5)
def get_live_signal(symbol="BTCUSDT", interval="15m"):
    interval_map = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "4h": "240"}
    bybit_interval = interval_map.get(interval, "15")
    
    df = None
    
    # 1. Try Bybit API (No IP Block on Streamlit Cloud)
    try:
        url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}&interval={bybit_interval}&limit=100"
        res = requests.get(url, timeout=4).json()
        if res.get("retCode") == 0 and res.get("result", {}).get("list"):
            raw_candles = res["result"]["list"]
            df = pd.DataFrame(raw_candles, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
            df['close'] = df['close'].astype(float)
            df = df.iloc[::-1].reset_index(drop=True)
    except Exception:
        df = None

    # 2. Fallback to Binance Mirror API if Bybit fails
    if df is None or df.empty:
        try:
            bin_url = f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
            res_bin = requests.get(bin_url, timeout=4).json()
            if isinstance(res_bin, list) and len(res_bin) > 0:
                df = pd.DataFrame(res_bin, columns=['time', 'open', 'high', 'low', 'close', 'volume', '_1', '_2', '_3', '_4', '_5', '_6'])
                df['close'] = df['close'].astype(float)
        except Exception:
            df = None

    if df is None or df.empty:
        return 0.0, "DATA ERROR ⚠️", "#848e9c", "-", "-", "Servers Busy - Try Changing Coin"

    # Technical Analysis (EMA & RSI)
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
    
    # Clearly defines Market UP or DOWN
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

# Header UI
st.markdown("<h2 style='text-align: center; color: #F0B90B;'>⚡ Crypto Live Signal Center</h2>", unsafe_allow_html=True)

# Search Bar
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

# Signal Result Box
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
