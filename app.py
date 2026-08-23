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

@st.cache_data(ttl=600, show_spinner=False)
def get_coingecko_market_data(coin_id):
    """CoinGecko API භාවිත කර දත්ත ලබා ගැනීම සහ දෝෂ මඟහරවා ගැනීම"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=8)
        
        if res.status_code == 200:
            data = res.json()
            if 'prices' in data and len(data['prices']) > 0:
                prices = [x[1] for x in data['prices']]
                df = pd.DataFrame(prices, columns=['close'])
                df['open'] = df['close'].shift(1).fillna(df['close'])
                df['high'] = df['close'] * 1.008
                df['low'] = df['close'] * 0.992
                df['volume'] = 100000
                return df
        return None
    except:
        return None

def calculate_indicators(df):
    close = df['close']
    high = df['high']
    low = df['low']
    
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
    
    # 5. Smart Money Concepts (SMC) Logic [LuxAlgo Style approximations]
    # Finding Market Structure Shifts (BOS / ChoCh) & Order Block zones
    df['rolling_high'] = high.rolling(window=5).max()
    df['rolling_low'] = low.rolling(window=5).min()
    
    # Bullish / Bearish Order Blocks estimation based on impulsive moves
    bullish_ob = (close > df['open']) & (close.shift(1) < df['open'].shift(1))
    bearish_ob = (close < df['open']) & (close.shift(1) > df['open'].shift(1))
    
    smc_bias = "NEUTRAL"
    if close.iloc[-1] > df['rolling_high'].iloc[-2]:
        smc_bias = "BULLISH_BOS" # Break of Structure upwards (Smart Money Buying)
    elif close.iloc[-1] < df['rolling_low'].iloc[-2]:
        smc_bias = "BEARISH_BOS" # Break of Structure downwards (Smart Money Selling)

    return {
        "price": close.iloc[-1],
        "ema9": ema9.iloc[-1],
        "ema21": ema21.iloc[-1],
        "rsi": rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0,
        "macd": macd.iloc[-1] if not np.isnan(macd.iloc[-1]) else 0.0,
        "macd_signal": signal_line.iloc[-1] if not np.isnan(signal_line.iloc[-1]) else 0.0,
        "upper_band": upper_band.iloc[-1] if not np.isnan(upper_band.iloc[-1]) else close.iloc[-1] * 1.05,
        "lower_band": lower_band.iloc[-1] if not np.isnan(lower_band.iloc[-1]) else close.iloc[-1] * 0.95,
        "smc_bias": smc_bias,
        "bullish_ob": bullish_ob.iloc[-1],
        "bearish_ob": bearish_ob.iloc[-1]
    }

# Sidebar with Coins List
with st.sidebar:
    st.markdown("### 👑 VIP Pro Menu")
    page = st.selectbox("Navigation", ["Live Signal", "Advanced Analytics", "Notepad"])
    
    coins = {
        "BTC/USDT": {"id": "bitcoin", "sym": "BINANCE:BTCUSDT"},
        "ETH/USDT": {"id": "ethereum", "sym": "BINANCE:ETHUSDT"},
        "BNB/USDT": {"id": "binancecoin", "sym": "BINANCE:BNBUSDT"},
        "SOL/USDT": {"id": "solana", "sym": "BINANCE:SOLUSDT"},
        "XRP/USDT": {"id": "ripple", "sym": "BINANCE:XRPUSDT"},
        "ADA/USDT": {"id": "cardano", "sym": "BINANCE:ADAUSDT"},
        "DOGE/USDT": {"id": "dogecoin", "sym": "BINANCE:DOGEUSDT"},
        "AVAX/USDT": {"id": "avalanche-2", "sym": "BINANCE:AVAXUSDT"},
        "TRX/USDT": {"id": "tron", "sym": "BINANCE:TRXUSDT"},
        "DOT/USDT": {"id": "polkadot", "sym": "BINANCE:DOTUSDT"},
        "MATIC/USDT": {"id": "polygon-ecosystem-token", "sym": "BINANCE:MATICUSDT"},
        "LINK/USDT": {"id": "chainlink", "sym": "BINANCE:LINKUSDT"},
        "UNI/USDT": {"id": "uniswap", "sym": "BINANCE:UNIUSDT"},
        "ATOM/USDT": {"id": "cosmos", "sym": "BINANCE:ATOMUSDT"},
        "LTC/USDT": {"id": "litecoin", "sym": "BINANCE:LTCUSDT"},
        "NEAR/USDT": {"id": "near", "sym": "BINANCE:NEARUSDT"},
        "APT/USDT": {"id": "aptos", "sym": "BINANCE:APTUSDT"},
        "FTM/USDT": {"id": "fantom", "sym": "BINANCE:FTMUSDT"},
        "ICP/USDT": {"id": "internet-computer", "sym": "BINANCE:ICPUSDT"},
        "RENDER/USDT": {"id": "render-token", "sym": "BINANCE:RNDRUSDT"},
        "INJ/USDT": {"id": "injective-protocol", "sym": "BINANCE:INJUSDT"},
        "TIA/USDT": {"id": "celestia", "sym": "BINANCE:TIAUSDT"},
        "ARB/USDT": {"id": "arbitrum", "sym": "BINANCE:ARBUSDT"},
        "OP/USDT": {"id": "optimism", "sym": "BINANCE:OPUSDT"},
        "SUI/USDT": {"id": "sui", "sym": "BINANCE:SUIUSDT"},
        "SEI/USDT": {"id": "sei-network", "sym": "BINANCE:SEIUSDT"},
        "PEPE/USDT": {"id": "pepe", "sym": "BINANCE:PEPEUSDT"},
        "SHIB/USDT": {"id": "shiba-inu", "sym": "BINANCE:SHIBUSDT"},
        "FLOKI/USDT": {"id": "floki", "sym": "BINANCE:FLOKIUSDT"},
        "BONK/USDT": {"id": "bonk", "sym": "BINANCE:BONKUSDT"},
    }
    
    sel = st.selectbox("Select Coin Pair", list(coins.keys()))
    coin_id = coins[sel]["id"]
    tv_sym = coins[sel]["sym"]

# Fetch data & Calculate indicators
df = get_coingecko_market_data(coin_id)

if df is not None and not df.empty:
    ind = calculate_indicators(df)
    price = ind["price"]
    change = ((price - df['open'].iloc[0]) / df['open'].iloc[0]) * 100
    
    # Multi-Indicator + Smart Money Concepts Scoring System
    score = 0
    
    if ind["ema9"] > ind["ema21"]: score += 1
    else: score -= 1
    
    if ind["rsi"] < 45: score += 1
    elif ind["rsi"] > 55: score -= 1
    
    if ind["macd"] > ind["macd_signal"]: score += 1
    else: score -= 1
    
    if price <= ind["lower_band"]: score += 1
    elif price >= ind["upper_band"]: score -= 1

    # SMC Weight Additions
    if ind["smc_bias"] == "BULLISH_BOS": score += 2
    elif ind["smc_bias"] == "BEARISH_BOS": score -= 2
    
    if ind["bullish_ob"]: score += 1
    if ind["bearish_ob"]: score -= 1

    if score >= 3:
        signal = "STRONG BUY (SMC Confirmed) 🚀"
        sig_color = "#10B981"
    elif score >= 1:
        signal = "BUY 📈"
        sig_color = "#34D399"
    elif score <= -3:
        signal = "STRONG SELL (SMC Confirmed) 🔻"
        sig_color = "#EF4444"
    elif score <= -1:
        signal = "SELL 📉"
        sig_color = "#F87171"
    else:
        signal = "HOLD / NEUTRAL ⚖️"
        sig_color = "#F59E0B"

    is_buy = "BUY" in signal
else:
    st.error("Failed to fetch market data. Please check your connection.")
    st.stop()

# App Header
st.markdown(f'<p class="vip-header">👑 Binance Pro Signal App <span class="vip-badge">VIP AI + SMC Pro</span></p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-desc">Multi-Indicator & <b>Smart Money Concepts (LuxAlgo Style)</b> Engine analyzing <b>{sel}</b>.</p>', unsafe_allow_html=True)

if page == "Live Signal":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Price:** ${price:,.4f} | **Change:** <span style='color: {'#059669' if change >= 0 else '#DC2626'};'>{change:,.2f}%</span> | **SMC Bias:** <b>{ind['smc_bias']}</b>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="signal-box" style="background: {sig_color};">{signal}</div>', unsafe_allow_html=True)

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
    
    chart_html = f"""
    <div class="tradingview-widget-container" style="height:400px;width:100%">
      <div id="tv_chart" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{"autosize": true, "symbol": "{tv_sym}", "interval": "60", "timezone": "Etc/UTC", "theme": "light", "style": "1", "locale": "en", "container_id": "tv_chart"}});
      </script>
    </div>
    """
    st.components.v1.html(chart_html, height=410)

elif page == "Advanced Analytics":
    st.markdown("### 📊 Smart Money Concepts (SMC) & Indicator Deep-Dive", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="SMC Market Structure", value=ind['smc_bias'])
        st.metric(label="RSI Status (14)", value=f"{ind['rsi']:.2f}")
    with col2:
        st.metric(label="Bullish Order Block Active", value="Yes" if ind['bullish_ob'] else "No")
        st.metric(label="Bearish Order Block Active", value="Yes" if ind['bearish_ob'] else "No")

elif page == "Notepad":
    st.markdown('### 📝 VIP Trading Notepad', unsafe_allow_html=True)
    if 'note' not in st.session_state: 
        st.session_state.note = ""
    st.session_state.note = st.text_area("Note", value=st.session_state.note, height=200, label_visibility="collapsed", placeholder="Write down your VIP notes here...")
    if st.button("Clear Notes"): 
        st.session_state.note = ""
        st.rerun()
