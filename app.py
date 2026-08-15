import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Binance All-Coins Signal Center", layout="wide")

# Fetch All Trading Pairs from Binance
@st.cache_data(ttl=3600)
def get_all_binance_usdt_symbols():
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        res = requests.get(url, timeout=10).json()
        symbols = [
            s['symbol'] for s in res['symbols']
            if s['symbol'].endswith('USDT') and s['status'] == 'TRADING'
            and not s['symbol'].endswith('UPUSDT') and not s['symbol'].endswith('DOWNUSDT')
        ]
        symbols.sort()
        return symbols
    except Exception:
        return ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT"]

# Translations (English, Sinhala, Tamil)
TRANSLATIONS = {
    "English": {
        "title": "⚡ Binance Crypto Signal Center (All Coins)",
        "select_coin": "Search / Select Any Crypto Pair",
        "timeframe": "Select Timeframe",
        "price": "Current Price",
        "reason": "Signal Reason",
        "tp": "Take Profit (TP)",
        "sl": "Stop Loss (SL)",
        "refresh_note": "🔄 Signals update automatically based on Live Market Data (EMA & RSI)."
    },
    "සිංහල": {
        "title": "⚡ බයිනෑන්ස් ක්‍රිප්ටෝ සිග්නල් මධ්‍යස්ථානය",
        "select_coin": "Coin එක Search කරන්න / තෝරන්න",
        "timeframe": "කාලරාමුව තෝරන්න (Timeframe)",
        "price": "වත්මන් මිල",
        "reason": "සිග්නල් එකට හේතුව",
        "tp": "වාසි ලබාගැනීම (TP)",
        "sl": "අලාභය පාලනය (SL)",
        "refresh_note": "🔄 වෙළඳපොළේ සජීවී දත්ත (EMA & RSI) මත සිග්නල් ස්වයංක්‍රීයව වෙනස් වේ."
    },
    "தமிழ்": {
        "title": "⚡ Binance Crypto சிக்னல் மையம்",
        "select_coin": "நாணயங்களைத் தேடவும் / தேர்ந்தெடுக்கவும்",
        "timeframe": "காலகட்டம்",
        "price": "தற்போதைய விலை",
        "reason": "சிக்னல் காரணம்",
        "tp": "இலாபம் (TP)",
        "sl": "நஷ்டத் தடுப்பு (SL)",
        "refresh_note": "🔄 சிக்னல்கள் தானாகவே கணக்கிடப்படும்."
    }
}

# Language Selector
lang_col1, lang_col2 = st.columns([4, 1])
with lang_col2:
    selected_lang = st.selectbox("🌐 Language / භාෂාව", list(TRANSLATIONS.keys()), index=1)

t = TRANSLATIONS[selected_lang]

# Fetch Live Signal from Binance
@st.cache_data(ttl=10)
def get_live_signal(symbol="BTCUSDT", interval="15m"):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        res = requests.get(url, timeout=5).json()
        df = pd.DataFrame(res, columns=['time', 'open', 'high', 'low', 'close', 'volume', '_1', '_2', '_3', '_4', '_5', '_6'])
        df['close'] = df['close'].astype(float)
        
        # EMA Calculations
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # RSI Calculation
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
        return 0.0, "LOADING...", "#848e9c", "-", "-", "Binance Data Loading..."

# Header & Controls
st.markdown(f"<h2 style='text-align: center; color: #F0B90B;'>{t['title']}</h2>", unsafe_allow_html=True)
st.caption(f"<p style='text-align: center;'>{t['refresh_note']}</p>", unsafe_allow_html=True)

# Load All USDT Coins Dynamic List
all_coins = get_all_binance_usdt_symbols()
default_index = all_coins.index("BTCUSDT") if "BTCUSDT" in all_coins else 0

col1, col2 = st.columns(2)
with col1:
    selected_symbol = st.selectbox(t['select_coin'], all_coins, index=default_index)
with col2:
    timeframe = st.selectbox(t['timeframe'], ["1m", "5m", "15m", "1h", "4h"], index=2)

# Load Signal Data
price, signal, color, tp, sl, reason = get_live_signal(selected_symbol, timeframe)

# Signal Dashboard Box
st.markdown(f"""
<div style="background-color: #1e2329; border: 2px solid {color}; padding: 20px; border-radius: 12px; margin: 15px 0;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2 style="color: {color}; margin: 0;">{signal} ({selected_symbol})</h2>
        <h3 style="color: #ffffff; margin: 0;">{t['price']}: ${price:,.4f}</h3>
    </div>
    <p style="color: #848e9c; font-size: 14px; margin-top: 8px;"><b>{t['reason']}:</b> {reason}</p>
    <hr style="border: 0.5px solid #2b313a; margin: 15px 0;">
    <div style="display: flex; justify-content: space-around; text-align: center;">
        <div>
            <span style="color: #848e9c; font-size: 14px;">{t['tp']}</span><br>
            <b style="color: #0ecb81; font-size: 22px;">${tp}</b>
        </div>
        <div>
            <span style="color: #848e9c; font-size: 14px;">{t['sl']}</span><br>
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
