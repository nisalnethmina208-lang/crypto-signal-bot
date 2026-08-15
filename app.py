import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Pro Crypto Signal App", layout="wide")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
BASE_URLS = [
    "https://data-api.binance.vision/api/v3",
    "https://api1.binance.com/api/v3",
    "https://api2.binance.com/api/v3"
]

def fetch_binance_data(endpoint, params=None):
    for base in BASE_URLS:
        try:
            res = requests.get(f"{base}/{endpoint}", params=params, headers=HEADERS, timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            continue
    return None

@st.cache_data(ttl=3600)
def get_all_usdt_symbols():
    data = fetch_binance_data("exchangeInfo")
    if data and 'symbols' in data:
        symbols = [s['symbol'] for s in data['symbols'] if s['symbol'].endswith('USDT') and s['status'] == 'TRADING']
        return sorted(symbols)
    return ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT"]

def get_klines(symbol, interval="1h", limit=150):
    data = fetch_binance_data("klines", params={'symbol': symbol, 'interval': interval, 'limit': limit})
    if data and isinstance(data, list):
        df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume', '_', '_', '_', '_', '_', '_'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df['close'] = df['close'].astype(float)
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        return df
    return pd.DataFrame()

# Indicators Calculation
def calculate_indicators(df):
    if df.empty or len(df) < 50:
        return df
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # EMAs
    df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
    return df

# UI Interface
st.title("⚡ Pro Binance Signal Dashboard")

all_symbols = get_all_usdt_symbols()
default_index = all_symbols.index('BTCUSDT') if 'BTCUSDT' in all_symbols else 0

selected_symbol = st.sidebar.selectbox("🪙 Coin එක තෝරන්න:", all_symbols, index=default_index)
timeframe = st.sidebar.selectbox("⏱️ Timeframe එක:", ["15m", "1h", "4h", "1d"], index=1)

df = get_klines(selected_symbol, interval=timeframe)

if not df.empty and len(df) >= 50:
    df = calculate_indicators(df)

    current_price = df['close'].iloc[-1]
    current_rsi = df['RSI'].iloc[-1]
    ema_20 = df['EMA_20'].iloc[-1]
    ema_50 = df['EMA_50'].iloc[-1]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"📊 {selected_symbol} Live Chart")
        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            name="Price", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        ))

        # EMA Lines
        fig.add_trace(go.Scatter(x=df['time'], y=df['EMA_20'], mode='lines', name='EMA 20', line=dict(color='#ff9800', width=1.5)))
        fig.add_trace(go.Scatter(x=df['time'], y=df['EMA_50'], mode='lines', name='EMA 50', line=dict(color='#2196f3', width=1.5)))

        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🎯 Signal Analysis")
        st.metric("Current Price", f"${current_price:,.4f}")
        st.metric("RSI (14)", f"{current_rsi:.2f}")
        
        st.divider()

        # Advanced Signal Logic
        if current_rsi < 35 and current_price > ema_20:
            st.success("🚀 STRONG BUY SIGNAL")
            tp = current_price * 1.03
            sl = current_price * 0.985
            st.write(f"🎯 **Target (TP 3%):** `${tp:,.4f}`")
            st.write(f"🛡️ **Stop Loss (SL 1.5%):** `${sl:,.4f}`")

        elif current_rsi < 40:
            st.info("📈 BUY SIGNAL (Oversold Area)")
            tp = current_price * 1.02
            sl = current_price * 0.99
            st.write(f"🎯 **Target (TP 2%):** `${tp:,.4f}`")
            st.write(f"🛡️ **Stop Loss (SL 1%):** `${sl:,.4f}`")

        elif current_rsi > 65 and current_price < ema_20:
            st.error("🔻 STRONG SELL SIGNAL")
            tp = current_price * 0.97
            sl = current_price * 1.015
            st.write(f"🎯 **Target (TP 3%):** `${tp:,.4f}`")
            st.write(f"🛡️ **Stop Loss (SL 1.5%):** `${sl:,.4f}`")

        elif current_rsi > 60:
            st.warning("📉 SELL SIGNAL (Overbought Area)")
            tp = current_price * 0.98
            sl = current_price * 1.01
            st.write(f"🎯 **Target (TP 2%):** `${tp:,.4f}`")
            st.write(f"🛡️ **Stop Loss (SL 1%):** `${sl:,.4f}`")

        else:
            st.warning("⏳ SIGNAL: NEUTRAL (Hold/Wait)")
            st.write("Market එක එක දිශාවකට තහවුරු වන තෙක් රැඳී සිටින්න.")
else:
    st.error("Data load කරගැනීමට නොහැකි විය. කරුණාකර පිටුව Refresh කරන්න.")
