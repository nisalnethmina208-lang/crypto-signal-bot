import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Binance Pro Signal App VIP", page_icon="👑", layout="wide")

# --- Password Protection Function ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234Binance@":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("## 👑 VIP App Login")
        st.text_input("Enter Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("## 👑 VIP App Login")
        st.text_input("Enter Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        st.error("😕 Incorrect Password")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Compact & VIP Styled CSS
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; color: #0F172A; }
    .vip-header { font-size: 26px; font-weight: 900; color: #1E293B; margin-bottom: 2px; letter-spacing: -0.5px; }
    .vip-badge { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 2px 8px; font-size: 10px; font-weight: 800; border-radius: 4px; text-transform: uppercase; vertical-align: middle; margin-left: 8px; }
    .sub-desc { color: #64748B; font-size: 13px; margin-bottom: 20px; }
    .card { background: #FFFFFF; border: 1px solid #E2E8F0; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
    .signal-box { color: white; padding: 10px; font-size: 16px; font-weight: 700; border-radius: 8px; text-align: center; }
    .t-card { background: #F1F5F9; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_binance_data(symbol, interval="1h", limit=100):
    """Binance API එකෙන් කෙලින්ම කෑන්ඩ්ල් ඩේටා ලබාගෙන ඉන්ඩිකේටර්ස් ගණනය කිරීම"""
    try:
        clean_sym = symbol.replace("BINANCE:", "")
        url = f"https://api.binance.com/api/v3/klines?symbol={clean_sym}&interval={interval}&limit={limit}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume',
                                             'close_time', 'quote_asset_volume', 'number_of_trades',
                                             'taker_buy_base', 'taker_buy_quote', 'ignore'])
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['open'] = df['open'].astype(float)
            df['volume'] = df['volume'].astype(float)
            return df
        return None
    except:
        return None

def calculate_indicators(df):
    close = df['close']
    
    # 1. EMA 9 & EMA 21
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    
    # 2. RSI (14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # 3. MACD (12, 26, 9)
    exp12 = close.ewm(span=12, adjust=False).mean()
    exp26 = close.ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal_line = macd.ewm(span=9, adjust=False).mean()
    
    # 4. Bollinger Bands (20, 2)
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    upper_band = sma20 + (std20 * 2)
    lower_band = sma20 - (std20 * 2)
    
    return {
        "price": close.iloc[-1],
        "ema9": ema9.iloc[-1],
        "ema21": ema21.iloc[-1],
        "rsi": rsi.iloc[-1],
        "macd": macd.iloc[-1],
        "macd_signal": signal_line.iloc[-1],
        "upper_band": upper_band.iloc[-1],
        "lower_band": lower_band.iloc[-1]
    }

# Sidebar with Coins List
with st.sidebar:
    st.markdown("### 👑 VIP Pro Menu")
    page = st.selectbox("Navigation", ["Live Signal", "Advanced Analytics", "Notepad"])
    
    coins = {
        "BTC/USDT": "BINANCE:BTCUSDT", "ETH/USDT": "BINANCE:ETHUSDT",
        "BNB/USDT": "BINANCE:BNBUSDT", "SOL/USDT": "BINANCE:SOLUSDT",
        "XRP/USDT": "BINANCE:XRPUSDT", "ADA/USDT": "BINANCE:ADAUSDT",
        "DOGE/USDT": "BINANCE:DOGEUSDT", "AVAX/USDT": "BINANCE:AVAXUSDT",
        "TRX/USDT": "BINANCE:TRXUSDT", "DOT/USDT": "BINANCE:DOTUSDT",
        "LINK/USDT": "BINANCE:LINKUSDT", "NEAR/USDT": "BINANCE:NEARUSDT",
        "PEPE/USDT": "BINANCE:PEPEUSDT", "SHIB/USDT": "BINANCE:SHIBUSDT",
        "SUI/USDT": "BINANCE:SUIUSDT", "RENDER/USDT": "BINANCE:RNDRUSDT",
        "FET/USDT": "BINANCE:FETUSDT", "WIF/USDT": "BINANCE:WIFUSDT"
    }
    
    sel = st.selectbox("Select Coin Pair", list(coins.keys()))
    tv_sym = coins[sel]
    
    timeframe = st.selectbox("Select Timeframe", ["15m", "1h", "4h", "1d"], index=1)

# Fetch data & Calculate indicators
df = get_binance_data(tv_sym, interval=timeframe)

if df is not None and not df.empty:
    ind = calculate_indicators(df)
    price = ind["price"]
    change = ((price - df['open'].iloc[0]) / df['open'].iloc[0]) * 100
    
    # Advanced Multi-Indicator Scoring System (වඩාත් නිවැරදි සිග්නල් සඳහා)
    score = 0
    
    # EMA Trend Check
    if ind["ema9"] > ind["ema21"]: score += 1
    else: score -= 1
    
    # RSI Condition
    if ind["rsi"] < 45: score += 1      # Oversold (Bullish)
    elif ind["rsi"] > 55: score -= 1   # Overbought (Bearish)
    
    # MACD Crossover Check
    if ind["macd"] > ind["macd_signal"]: score += 1
    else: score -= 1
    
    # Bollinger Bands Touch Check
    if price <= ind["lower_band"]: score += 1    # Bounce from lower band
    elif price >= ind["upper_band"]: score -= 1  # Rejection from upper band

    # Final Signal Determination
    if score >= 2:
        signal = "STRONG BUY 🚀"
        sig_color = "#10B981"
    elif score == 1:
        signal = "BUY 📈"
        sig_color = "#34D399"
    elif score <= -2:
        signal = "STRONG SELL 🔻"
        sig_color = "#EF4444"
    elif score == -1:
        signal = "SELL 📉"
        sig_color = "#F87171"
    else:
        signal = "HOLD / NEUTRAL ⚖️"
        sig_color = "#F59E0B"

    is_buy = "BUY" in signal
else:
    st.error("Failed to fetch data from Binance API. Please check your connection.")
    st.stop()

# App Header (VIP Title)
st.markdown(f'<p class="vip-header">👑 Binance Pro Signal App <span class="vip-badge">VIP AI Pro</span></p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-desc">Multi-Indicator AI Engine (EMA, RSI, MACD, Bollinger Bands) analyzing <b>{sel}</b> on <b>{timeframe}</b> timeframe.</p>', unsafe_allow_html=True)

if page == "Live Signal":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Price:** ${price:,.4f} | **Change:** <span style='color: {'#059669' if change >= 0 else '#DC2626'};'>{change:,.2f}%</span> | **RSI:** <b>{ind['rsi']:.1f}</b>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="signal-box" style="background: {sig_color};">{signal}</div>', unsafe_allow_html=True)

    # Dynamic TP / SL Calculations
    tp1 = price * (1.025 if is_buy else 0.975)
    tp2 = price * (1.050 if is_buy else 0.950)
    sl = price * (0.985 if is_buy else 1.015)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="t-card">Entry Price<br><b>${price:,.4f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="t-card">Target 1 (TP1)<br><b style="color: #059669;">${tp1:,.4f}</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="t-card">Target 2 (TP2)<br><b style="color: #059669;">${tp2:,.4f}</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="t-card">Stop Loss (SL)<br><b style="color: #DC2626;">${sl:,.4f}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # TradingView Chart
    tv_clean_sym = tv_sym.replace("BINANCE:", "BINANCE:")
    chart_html = f"""
    <div class="tradingview-widget-container" style="height:400px;width:100%">
      <div id="tv_chart" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{"autosize": true, "symbol": "{tv_clean_sym}", "interval": "60", "timezone": "Etc/UTC", "theme": "light", "style": "1", "locale": "en", "container_id": "tv_chart"}});
      </script>
    </div>
    """
    st.components.v1.html(chart_html, height=410)

elif page == "Advanced Analytics":
    st.markdown("### 📊 Indicator Deep-Dive Metrics", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="RSI Status (14)", value=f"{ind['rsi']:.2f}", delta="Oversold (<45)" if ind['rsi'] < 45 else "Overbought (>55)" if ind['rsi'] > 55 else "Neutral")
        st.metric(label="MACD Value", value=f"{ind['macd']:.4f}", delta="Bullish" if ind['macd'] > ind['macd_signal'] else "Bearish")
    with col2:
        st.metric(label="EMA 9 vs EMA 21", value="Uptrend" if ind['ema9'] > ind['ema21'] else "Downtrend")
        st.metric(label="Bollinger Upper / Lower", value=f"${ind['upper_band']:,.2f} / ${ind['lower_band']:,.2f}")

elif page == "Notepad":
    st.markdown('### 📝 VIP Trading Notepad', unsafe_allow_html=True)
    if 'note' not in st.session_state: 
        st.session_state.note = ""
    st.session_state.note = st.text_area("Note", value=st.session_state.note, height=200, label_visibility="collapsed", placeholder="Write down your VIP notes here...")
    if st.button("Clear Notes"): 
        st.session_state.note = ""
        st.rerun()
