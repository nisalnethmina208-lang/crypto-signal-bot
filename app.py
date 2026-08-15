import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import urllib.parse

# Page config
st.set_page_config(
    page_title="Binance Signal & WP Alert",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (Hide Streamlit Defaults)
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

# WhatsApp Message Sending Function
def send_whatsapp_alert(phone_number, api_key, message):
    try:
        encoded_msg = urllib.parse.quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={encoded_msg}&apikey={api_key}"
        res = requests.get(url, timeout=10)
        return res.status_code == 200
    except Exception:
        return False

# Fetch Binance Live Data
@st.cache_data(ttl=10)
def get_live_signal(symbol="BTCUSDT", interval="15m"):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        res = requests.get(url, timeout=5).json()
        df = pd.DataFrame(res, columns=['time', 'open', 'high', 'low', 'close', 'volume', '_1', '_2', '_3', '_4', '_5', '_6'])
        df['close'] = df['close'].astype(float)
        
        # Moving Averages & RSI
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
        
        if ema_cross_up or (bullish and latest['rsi'] < 65):
            signal = "STRONG BUY 🟢"
            color = "#0ecb81"
            tp = round(price * 1.015, 4)
            sl = round(price * 0.990, 4)
            reason = f"EMA Cross Up | RSI: {round(latest['rsi'], 1)}"
        elif not bullish and latest['rsi'] > 35:
            signal = "STRONG SELL 🔴"
            color = "#f6465d"
            tp = round(price * 0.985, 4)
            sl = round(price * 1.010, 4)
            reason = f"EMA Bearish | RSI: {round(latest['rsi'], 1)}"
        else:
            signal = "HOLD / WAIT 🟡"
            color = "#f0b90b"
            tp = "-"
            sl = "-"
            reason = f"RSI Neutral: {round(latest['rsi'], 1)}"
            
        return price, signal, color, tp, sl, reason
    except Exception:
        return 0.0, "LOADING...", "#848e9c", "-", "-", "Error Connecting"

# Session State Setup
if 'wp_phone' not in st.session_state:
    st.session_state['wp_phone'] = ""
if 'wp_api_key' not in st.session_state:
    st.session_state['wp_api_key'] = ""

# Navigation Tabs
tab_main, tab_settings = st.tabs(["📊 Signals & Market", "⚙️ Settings"])

# ----------------- TAB 1: SIGNALS & MARKET -----------------
with tab_main:
    st.markdown("<h3 style='text-align: center; color: #F0B90B;'>⚡ Binance Signal & WP Alert Center</h3>", unsafe_allow_html=True)
    
    # Dynamic Coin Selection
    col_coin, col_tf = st.columns([2, 1])
    with col_coin:
        coin_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "NEARUSDT", "PEPEUSDT"]
        selected_symbol = st.selectbox("Select Coin / Pair", coin_list, index=0)
    with col_tf:
        timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h"], index=2)
    
    # Get Live Data for Selected Coin
    price, signal, color, tp, sl, reason = get_live_signal(selected_symbol, timeframe)
    
    # Display Signal Card
    st.markdown(f"""
    <div style="background-color: #1e2329; border-left: 6px solid {color}; padding: 15px; border-radius: 8px; margin-top: 10px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="color: {color}; margin: 0;">{signal} ({selected_symbol})</h3>
            <span style="color: #ffffff; font-weight: bold; font-size: 16px;">Price: ${price:,.4f}</span>
        </div>
        <p style="color: #848e9c; font-size: 13px; margin: 5px 0 10px 0;">Reason: {reason}</p>
        <hr style="border: 0.5px solid #2b313a; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 14px;">
            <div><span style="color: #848e9c;">Take Profit (TP):</span><br><b style="color: #0ecb81;">${tp}</b></div>
            <div><span style="color: #848e9c;">Stop Loss (SL):</span><br><b style="color: #f6465d;">${sl}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Send Manual WP Alert Button
    if st.button(f"📲 Send {selected_symbol} Signal to WhatsApp", type="primary", use_container_width=True):
        if st.session_state['wp_phone'] and st.session_state['wp_api_key']:
            msg = f"🚨 BINANCE SIGNAL ALERT 🚨\n\nPair: {selected_symbol}\nSignal: {signal}\nPrice: ${price}\nTP: ${tp}\nSL: ${sl}\nReason: {reason}"
            success = send_whatsapp_alert(st.session_state['wp_phone'], st.session_state['wp_api_key'], msg)
            if success:
                st.success("WhatsApp Message Sent Successfully! 🚀")
            else:
                st.error("Failed to send WhatsApp message. Check Phone & API Key.")
        else:
            st.warning("Please configure WhatsApp Phone Number & API Key in Settings Page first!")

    # Dynamic TradingView Chart
    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:450px;width:100%;">
      <div id="tradingview_chart" style="height:100%;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
          "autosize": true,
          "symbol": "BINANCE:{selected_symbol}",
          "interval": "{timeframe.replace('m', '') if 'm' in timeframe else timeframe.replace('h', '60')}",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "enable_publishing": false,
          "hide_side_toolbar": false,
          "allow_symbol_change": true,
          "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(tradingview_html, height=450)

# ----------------- TAB 2: SETTINGS -----------------
with tab_settings:
    st.markdown("<h3 style='color: #F0B90B;'>⚙️ WhatsApp Alert Settings</h3>", unsafe_allow_html=True)
    
    st.info("WhatsApp Alerts නොමිලේ ලබාගැනීමට CallMeBot භාවිත කරයි.")
    
    phone_input = st.text_input("WhatsApp Number (Country Code සමඟ e.g., +94771234567)", value=st.session_state['wp_phone'])
    api_key_input = st.text_input("CallMeBot API Key", value=st.session_state['wp_api_key'], type="password")
    
    if st.button("Save Settings"):
        st.session_state['wp_phone'] = phone_input
        st.session_state['wp_api_key'] = api_key_input
        st.success("Settings Saved!")

    st.markdown("---")
    st.markdown("**WhatsApp API Key නොමිලේ ලබාගන්නා ආකාරය:**")
    st.markdown("""
    1. Phone එකෙන් WhatsApp ඇරඹ තබා **`+34 644 10 55 84`** අංකය Contact එකක් ලෙස Save කරගන්න.
    2. එම WhatsApp අංකයට **`I allow callmebot to send me messages`** කියා Message එකක් යවන්න.
    3. තත්පර කිහිපයකින් ඔබට **API Key** එකක් ලැබෙනු ඇත. එය උඩින් ඇති කොටුවට ඇතුළත් කරන්න.
    """)
