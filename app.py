import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

# Page setup
st.set_page_config(
    page_title="Crypto Signal Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit Default Headers/Footers
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #1e2329;
        border-radius: 8px;
        color: #848e9c;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0b90b !important;
        color: #000000 !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Function to fetch Binance live data & calculate signals
@st.cache_data(ttl=10) # Refresh data every 10 seconds
def get_live_signal(symbol="BTCUSDT", interval="15m"):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        res = requests.get(url, timeout=5).json()
        df = pd.DataFrame(res, columns=['time', 'open', 'high', 'low', 'close', 'volume', '_1', '_2', '_3', '_4', '_5', '_6'])
        df['close'] = df['close'].astype(float)
        
        # Calculate Moving Averages (EMA 20 & EMA 50)
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # Calculate RSI 14
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        price = latest['close']
        
        # Signal Generation Logic
        bullish = latest['ema20'] > latest['ema50']
        ema_cross_up = (prev['ema20'] <= prev['ema50']) and (latest['ema20'] > latest['ema50'])
        
        if ema_cross_up or (bullish and latest['rsi'] < 65):
            signal = "STRONG BUY"
            color = "#0ecb81" # Green
            tp = round(price * 1.015, 2)
            sl = round(price * 0.990, 2)
            reason = f"EMA Bullish Crossover | RSI: {round(latest['rsi'], 1)}"
        elif not bullish and latest['rsi'] > 35:
            signal = "STRONG SELL"
            color = "#f6465d" # Red
            tp = round(price * 0.985, 2)
            sl = round(price * 1.010, 2)
            reason = f"EMA Bearish Pressure | RSI: {round(latest['rsi'], 1)}"
        else:
            signal = "HOLD / WAIT"
            color = "#f0b90b" # Yellow
            tp = "-"
            sl = "-"
            reason = f"Market Consolidating | RSI: {round(latest['rsi'], 1)}"
            
        return price, signal, color, tp, sl, reason
    except Exception as e:
        return 0.0, "LOADING...", "#848e9c", "-", "-", "Connecting..."

# Tabs Setup
tab_main, tab_settings = st.tabs(["📊 Signals & Market", "⚙️ Settings"])

# ----------------- TAB 1: SIGNALS & MARKET -----------------
with tab_main:
    st.markdown("<h3 style='text-align: center; color: #F0B90B; margin-bottom: 15px;'>⚡ Binance Signal Center</h3>", unsafe_allow_html=True)
    
    # Fetch Live Data
    price, signal, color, tp, sl, reason = get_live_signal()
    
    # Custom Live Signal Display Card
    st.markdown(f"""
    <div style="background-color: #1e2329; border-left: 6px solid {color}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="color: {color}; margin: 0;">{"🟢" if "BUY" in signal else "🔴" if "SELL" in signal else "🟡"} {signal}</h3>
            <span style="color: #ffffff; font-weight: bold; font-size: 16px;">BTC Price: ${price:,.2f}</span>
        </div>
        <p style="color: #848e9c; font-size: 13px; margin: 5px 0 10px 0;">Reason: {reason}</p>
        <hr style="border: 0.5px solid #2b313a; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 14px;">
            <div><span style="color: #848e9c;">Take Profit (TP):</span><br><b style="color: #0ecb81;">${tp}</b></div>
            <div><span style="color: #848e9c;">Stop Loss (SL):</span><br><b style="color: #f6465d;">${sl}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time TradingView Chart Widget
    tradingview_html = """
    <div class="tradingview-widget-container" style="height:480px;width:100%;">
      <div id="tradingview_chart" style="height:100%;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({
          "autosize": true,
          "symbol": "BINANCE:BTCUSDT",
          "interval": "15",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "enable_publishing": false,
          "hide_side_toolbar": false,
          "allow_symbol_change": true,
          "details": true,
          "container_id": "tradingview_chart"
      });
      </script>
    </div>
    """
    components.html(tradingview_html, height=480)

# ----------------- TAB 2: SETTINGS -----------------
with tab_settings:
    st.markdown("<h3 style='color: #F0B90B;'>⚙️ App Settings</h3>", unsafe_allow_html=True)
    
    st.subheader("API Connections")
    st.text_input("Binance API Key", type="password")
    st.text_input("Binance Secret Key", type="password")
    
    st.subheader("Signal Configuration")
    st.selectbox("Default Pair", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"])
    st.selectbox("Default Timeframe", ["1m", "5m", "15m", "1h", "4h", "1D"], index=2)
    st.checkbox("Enable Push Notifications", value=True)
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")
