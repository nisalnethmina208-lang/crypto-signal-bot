import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Binance Signal App VIP - Real-time MSNR Pro", page_icon="👑", layout="wide")

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
    .signal-box { color: white; padding: 10px; font-size: 16px; font-weight: 700; border-radius: 8px; text-align: center; }
    .t-card { background: #F1F5F9; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# Fetch Top 210+ Coins from CoinGecko API
@st.cache_data(ttl=3600, show_spinner=False)
def get_top_coins_list():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=210&page=1&sparkline=false"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            coins_dict = {}
            for item in data:
                symbol = item['symbol'].upper() + "/USDT"
                coin_id = item['id']
                tv_symbol = f"BINANCE:{item['symbol'].upper()}USDT"
                coins_dict[symbol] = {"id": coin_id, "sym": tv_symbol}
            return coins_dict
    except:
        pass
     
    # Fallback default list if API fails
    return {
        "BTC/USDT": {"id": "bitcoin", "sym": "BINANCE:BTCUSDT"},
        "ETH/USDT": {"id": "ethereum", "sym": "BINANCE:ETHUSDT"},
        "BNB/USDT": {"id": "binancecoin", "sym": "BINANCE:BNBUSDT"},
        "SOL/USDT": {"id": "solana", "sym": "BINANCE:SOLUSDT"},
        "XRP/USDT": {"id": "ripple", "sym": "BINANCE:XRPUSDT"}
    }

coins = get_top_coins_list()

@st.cache_data(ttl=300, show_spinner=False)
def get_coingecko_market_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=14"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=8)
        
        if res.status_code == 200:
            data = res.json()
            if 'prices' in data and len(data['prices']) > 0:
                prices = [x[1] for x in data['prices']]
                volumes = [x[1] for x in data['total_volumes']] if 'total_volumes' in data else [100000] * len(prices)
                
                df = pd.DataFrame(prices, columns=['close'])
                df['volume'] = volumes[:len(df)]
                df['open'] = df['close'].shift(1).fillna(df['close'])
                df['high'] = df['close'] * 1.006
                df['low'] = df['close'] * 0.994
                return df
        return None
    except:
        return None

def calculate_realtime_confluence_indicators(df):
    close = df['close']
    high = df['high']
    low = df['low']
    open_p = df['open']
    volume = df['volume']
    
    # Moving Averages (EMA 9, 21, 50)
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    
    # RSI (14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line

    # Bollinger Bands
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    bb_upper = sma20 + (std20 * 2)
    bb_lower = sma20 - (std20 * 2)
    
    # ATR (Average True Range) for SL / TP
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    atr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).rolling(window=14).mean()

    current_close = close.iloc[-1]
    
    # Real-time Volume Spike Analysis
    avg_volume = volume.rolling(window=14).mean().iloc[-1]
    current_volume = volume.iloc[-1]
    high_volume_spike = current_volume > (avg_volume * 1.25)

    # Premium / Discount Zones
    range_high = high.rolling(window=20).max().iloc[-1]
    range_low = low.rolling(window=20).min().iloc[-1]
    equilibrium = (range_high + range_low) / 2
    zone = "Premium Zone (Sell/Short Area)" if current_close > equilibrium else "Discount Zone (Buy/Long Area)"

    # --- Real-time MSNR (Malaysian Support and Resistance) Confluence Engine ---
    body_high = pd.concat([open_p, close], axis=1).max(axis=1)
    body_low = pd.concat([open_p, close], axis=1).min(axis=1)
    
    msnr_resistance = body_high.rolling(window=10).max().iloc[-1]
    msnr_support = body_low.rolling(window=10).min().iloc[-1]
    
    # Real-time reaction check with tolerance range
    distance_to_res = abs(current_close - msnr_resistance) / current_close
    distance_to_sup = abs(current_close - msnr_support) / current_close

    if distance_to_res <= 0.008:
        msnr_status = "Testing MSNR Resistance (Supply Reaction 🔴)"
        msnr_zone_type = "Supply"
    elif distance_to_sup <= 0.008:
        msnr_status = "Testing MSNR Support (Demand Reaction 🟢)"
        msnr_zone_type = "Demand"
    elif current_close > equilibrium:
        msnr_status = "In Upper MSNR Range (Bullish Control)"
        msnr_zone_type = "Neutral-High"
    else:
        msnr_status = "In Lower MSNR Range (Bearish Control)"
        msnr_zone_type = "Neutral-Low"

    return {
        "price": current_close,
        "ema9": ema9.iloc[-1],
        "ema21": ema21.iloc[-1],
        "ema50": ema50.iloc[-1],
        "rsi": rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0,
        "macd": macd_line.iloc[-1] if not np.isnan(macd_line.iloc[-1]) else 0.0,
        "macd_signal": signal_line.iloc[-1] if not np.isnan(signal_line.iloc[-1]) else 0.0,
        "macd_hist": macd_hist.iloc[-1] if not np.isnan(macd_hist.iloc[-1]) else 0.0,
        "bb_upper": bb_upper.iloc[-1] if not np.isnan(bb_upper.iloc[-1]) else current_close * 1.02,
        "bb_lower": bb_lower.iloc[-1] if not np.isnan(bb_lower.iloc[-1]) else current_close * 0.98,
        "atr": atr.iloc[-1] if not np.isnan(atr.iloc[-1]) else current_close * 0.01,
        "zone": zone,
        "volume_spike": high_volume_spike,
        "msnr_support": msnr_support,
        "msnr_resistance": msnr_resistance,
        "msnr_status": msnr_status,
        "msnr_zone_type": msnr_zone_type
    }

# Sidebar with Coins List
with st.sidebar:
    st.markdown("### 👑 VIP Menu (210+ Coins)")
    page = st.selectbox("Navigation", ["Live Signal", "Advanced Analytics", "Notepad"])
    
    sel = st.selectbox("Select Coin Pair", list(coins.keys()))
    coin_id = coins[sel]["id"]
    tv_sym = coins[sel]["sym"]

df = get_coingecko_market_data(coin_id)

if df is not None and not df.empty:
    ind = calculate_realtime_confluence_indicators(df)
    price = ind["price"]
    change = ((price - df['open'].iloc[0]) / df['open'].iloc[0]) * 100
    
    # --- Advanced Real-time Confluence Scoring Engine ---
    score = 0
    
    # 1. Trend Filter (EMA Confluence)
    if ind["ema9"] > ind["ema21"] > ind["ema50"]: score += 2
    elif ind["ema9"] < ind["ema21"] < ind["ema50"]: score -= 2
    
    # 2. RSI Momentum Filter
    if ind["rsi"] < 35: score += 2  # Oversold Bounce Potential
    elif ind["rsi"] > 65: score -= 2  # Overbought Drop Potential
    elif 45 <= ind["rsi"] <= 55:
        if ind["ema9"] > ind["ema21"]: score += 1
        else: score -= 1

    # 3. MACD Histogram Trend Momentum
    if ind["macd_hist"] > 0: score += 1
    else: score -= 1

    # 4. Real-time MSNR & Premium/Discount Confluence
    if ind["msnr_zone_type"] == "Demand":
        score += 3  price reacting precisely at MSNR Support!
    elif ind["msnr_zone_type"] == "Supply":
        score -= 3  price reacting precisely at MSNR Resistance!
    
    if "Discount" in ind["zone"] and score > 0: score += 1
    elif "Premium" in ind["zone"] and score < 0: score -= 1

    # 5. Volume Spike Confirmation Booster
    if ind["volume_spike"]:
        if score > 0: score += 2
        elif score < 0: score -= 2

    # Final Signal Determination based on Confluence Score
    if score >= 5:
        signal, sig_color = "STRONG BUY 🚀", "#10B981"
    elif score >= 2:
        signal, sig_color = "BUY 📈", "#34D399"
    elif score <= -5:
        signal, sig_color = "STRONG SELL 🔻", "#EF4444"
    elif score <= -2:
        signal, sig_color = "SELL 📉", "#F87171"
    else:
        signal, sig_color = "HOLD / NEUTRAL ⚖️", "#F59E0B"

    is_buy = "BUY" in signal
else:
    st.error("දත්ත ලබා ගැනීම අසාර්ථක විය. කරුණාකර මොහොතަކින් උත්සාහ කරන්න.")
    st.stop()

st.markdown('<p class="vip-header">👑 Binance Signal App VIP <span class="vip-badge">Real-time MSNR Pro</span></p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-desc">Real-time market confluence analysis and precision targets for <b>{sel}</b>.</p>', unsafe_allow_html=True)

if page == "Live Signal":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Price:** ${price:,.4f} | **Change:** <span style='color: {'#059669' if change >= 0 else '#DC2626'};'>{change:,.2f}%</span> | **MSNR State:** <b>{ind['msnr_status']}</b>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="signal-box" style="background: {sig_color};">{signal}</div>', unsafe_allow_html=True)

    # Risk-Reward ATR Based Targets
    if is_buy:
        tp1 = price + (ind['atr'] * 1.5)
        tp2 = price + (ind['atr'] * 3.0)
        sl = price - (ind['atr'] * 1.2)
    else:
        tp1 = price - (ind['atr'] * 1.5)
        tp2 = price - (ind['atr'] * 3.0)
        sl = price + (ind['atr'] * 1.2)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="t-card">Entry<br><b>${price:,.4f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="t-card">TP 1<br><b style="color: #059669;">${tp1:,.4f}</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="t-card">TP 2<br><b style="color: #059669;">${tp2:,.4f}</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="t-card">SL<br><b style="color: #DC2626;">${sl:,.4f}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # TradingView Chart
    chart_html = f"""
    <div class="tradingview-widget-container" style="height:450px;width:100%">
      <div id="tv_chart" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{tv_sym}",
        "interval": "60",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "studies": [
          "RSI@tv-basicstudies",
          "MACD@tv-basicstudies",
          "BollingerBands@tv-basicstudies"
        ],
        "container_id": "tv_chart"
      }});
      </script>
    </div>
    """
    st.components.v1.html(chart_html, height=460)

elif page == "Advanced Analytics":
    st.markdown("### 📊 Real-time Confluence & MSNR Metrics", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Real-time MSNR Status", value=ind['msnr_status'])
        st.metric(label="MSNR Support (Demand)", value=f"${ind['msnr_support']:,.4f}")
        st.metric(label="MSNR Resistance (Supply)", value=f"${ind['msnr_resistance']:,.4f}")
        st.metric(label="RSI (14) Momentum", value=f"{ind['rsi']:.2f}")
    with col2:
        st.metric(label="Market Zone", value=ind['zone'])
        st.metric(label="MACD Histogram", value=f"{ind['macd_hist']:.4f}")
        st.metric(label="Volume Spike Status", value="Active Spike 🚀" if ind['volume_spike'] else "Normal Volume ⚖️")
        st.metric(label="ATR Volatility (SL Guide)", value=f"${ind['atr']:.4f}")

elif page == "Notepad":
    st.markdown('### 📝 VIP Trading Notepad', unsafe_allow_html=True)
    if 'note' not in st.session_state: 
        st.session_state.note = ""
    st.session_state.note = st.text_area("Note", value=st.session_state.note, height=200, label_visibility="collapsed")
    if st.button("Clear Notes"): 
        st.session_state.note = ""
        st.rerun()
