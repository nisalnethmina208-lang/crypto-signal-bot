import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Crypto Signal Bot", layout="wide", initial_sidebar_state="expanded")

# 1. Binance එකේ සියලුම USDT Pairs ලබාගැනීම
@st.cache_data(ttl=3600)
def get_all_usdt_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    res = requests.get(url).json()
    symbols = [s['symbol'] for s in res['symbols'] if s['symbol'].endswith('USDT') and s['status'] == 'TRADING']
    return sorted(symbols)

# 2. Market Candlestick Data ලබාගැනීම
def get_klines(symbol, interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume', '_', '_', '_', '_', '_', '_'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['close'] = df['close'].astype(float)
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    return df

# 3. RSI ගණනය
def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Header UI
st.title("⚡ Binance Crypto Signal App")

# Sidebar - Coin Selection
all_symbols = get_all_usdt_symbols()
default_index = all_symbols.index('BTCUSDT') if 'BTCUSDT' in all_symbols else 0
selected_symbol = st.sidebar.selectbox("🪙 Coin එක තෝරන්න:", all_symbols, index=default_index)
timeframe = st.sidebar.selectbox("⏱️ Timeframe එක:", ["15m", "1h", "4h", "1d"], index=1)

# Fetch Data
df = get_klines(selected_symbol, interval=timeframe)
df['RSI'] = calculate_rsi(df)

current_price = df['close'].iloc[-1]
current_rsi = df['RSI'].iloc[-1]

# Layout: Chart & Signals
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📊 {selected_symbol} Chart")
    fig = go.Figure(data=[go.Candlestick(
        x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    )])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Live Signal")
    st.metric("Current Price", f"${current_price:,.4f}")
    st.metric("RSI (14)", f"{current_rsi:.2f}")
    
    st.divider()
    if current_rsi < 30:
        st.success("🚀 SIGNAL: BUY (Oversold)")
    elif current_rsi > 70:
        st.error("🔻 SIGNAL: SELL (Overbought)")
    else:
        st.warning("⏳ SIGNAL: HOLD (Neutral)")
