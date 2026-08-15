import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import urllib.parse

# Page config
st.set_page_config(page_title="Multi-Language Binance Signal App", layout="wide")

# 1. TRANSLATION DICTIONARY (ඕනෑම භාෂාවක් මෙතැනට එකතු කළ හැක)
TRANSLATIONS = {
    "English": {
        "title": "⚡ Binance Signal & WP Alert Center",
        "select_coin": "Select Coin / Pair",
        "timeframe": "Timeframe",
        "price": "Price",
        "reason": "Reason",
        "tp": "Take Profit (TP)",
        "sl": "Stop Loss (SL)",
        "send_wp": "📲 Send Signal to WhatsApp",
        "settings_title": "⚙️ WhatsApp Alert Settings",
        "phone_label": "WhatsApp Number (with country code e.g., +94771234567)",
        "api_label": "CallMeBot API Key",
        "save_btn": "Save Settings",
        "tab_main": "📊 Signals & Market",
        "tab_settings": "⚙️ Settings"
    },
    "සිංහල": {
        "title": "⚡ බයිනෑන්ස් සිග්නල් සහ WhatsApp ඇලර්ට් මධ්‍යස්ථානය",
        "select_coin": "Coin එක තෝරන්න",
        "timeframe": "කාලරාමුව (Timeframe)",
        "price": "වත්මන් මිල",
        "reason": "හේතුව",
        "tp": "වාසි ලබාගැනීම (TP)",
        "sl": "අලාභය පාලනය (SL)",
        "send_wp": "📲 WhatsApp එකට Signal එක යවන්න",
        "settings_title": "⚙️ WhatsApp ඇලර්ට් සැකසුම්",
        "phone_label": "WhatsApp අංකය (රටේ කේතය සමඟ e.g., +94771234567)",
        "api_label": "CallMeBot API කේතය",
        "save_btn": "තොරතුරු සුරකින්න",
        "tab_main": "📊 සිග්නල් සහ වෙළඳපොළ",
        "tab_settings": "⚙️ සැකසුම්"
    },
    "தமிழ்": {
        "title": "⚡ Binance சிக்னல் மற்றும் WP எச்சரிக்கை மையம்",
        "select_coin": "நாணயத்தைத் தேர்ந்தெடுக்கவும்",
        "timeframe": "காலகட்டம்",
        "price": "தற்போதைய விலை",
        "reason": "காரணம்",
        "tp": "இலாபம் (TP)",
        "sl": "நஷ்டத் தடுப்பு (SL)",
        "send_wp": "📲 WhatsApp-க்கு சிக்னல் அனுப்பவும்",
        "settings_title": "⚙️ WhatsApp அமைப்புகள்",
        "phone_label": "WhatsApp எண் (+94771234567)",
        "api_label": "CallMeBot API சாவி",
        "save_btn": "சேமிக்கவும்",
        "tab_main": "📊 சிக்னல்கள்",
        "tab_settings": "⚙️ அமைப்புகள்"
    }
}

# 2. LANGUAGE SELECTOR TOP BAR
lang_col1, lang_col2 = st.columns([4, 1])
with lang_col2:
    selected_lang = st.selectbox("🌐 Language / භාෂාව", list(TRANSLATIONS.keys()), index=0)

t = TRANSLATIONS[selected_lang] # Current Language Object

# Session State Setup
if 'wp_phone' not in st.session_state:
    st.session_state['wp_phone'] = ""
if 'wp_api_key' not in st.session_state:
    st.session_state['wp_api_key'] = ""

def send_whatsapp_alert(phone_number, api_key, message):
    try:
        encoded_msg = urllib.parse.quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={encoded_msg}&apikey={api_key}"
        res = requests.get(url, timeout=10)
        return res.status_code == 200
    except Exception:
        return False

@st.cache_data(ttl=10)
def get_live_signal(symbol="BTCUSDT", interval="15m"):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        res = requests.get(url, timeout=5).json()
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
        return 0.0, "LOADING...", "#848e9c", "-", "-", "Error"

# Tabs Setup
tab_main, tab_settings = st.tabs([t['tab_main'], t['tab_settings']])

with tab_main:
    st.markdown(f"<h3 style='text-align: center; color: #F0B90B;'>{t['title']}</h3>", unsafe_allow_html=True)
    
    col_coin, col_tf = st.columns([2, 1])
    with col_coin:
        coin_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT"]
        selected_symbol = st.selectbox(t['select_coin'], coin_list, index=0)
    with col_tf:
        timeframe = st.selectbox(t['timeframe'], ["1m", "5m", "15m", "1h", "4h"], index=2)
    
    price, signal, color, tp, sl, reason = get_live_signal(selected_symbol, timeframe)
    
    st.markdown(f"""
    <div style="background-color: #1e2329; border-left: 6px solid {color}; padding: 15px; border-radius: 8px; margin-top: 10px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="color: {color}; margin: 0;">{signal} ({selected_symbol})</h3>
            <span style="color: #ffffff; font-weight: bold;">{t['price']}: ${price:,.4f}</span>
        </div>
        <p style="color: #848e9c; font-size: 13px; margin: 5px 0 10px 0;">{t['reason']}: {reason}</p>
        <hr style="border: 0.5px solid #2b313a; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 14px;">
            <div><span style="color: #848e9c;">{t['tp']}:</span><br><b style="color: #0ecb81;">${tp}</b></div>
            <div><span style="color: #848e9c;">{t['sl']}:</span><br><b style="color: #f6465d;">${sl}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"{t['send_wp']} ({selected_symbol})", type="primary", use_container_width=True):
        if st.session_state['wp_phone'] and st.session_state['wp_api_key']:
            msg = f"🚨 BINANCE SIGNAL 🚨\nPair: {selected_symbol}\nSignal: {signal}\nPrice: ${price}\nTP: ${tp}\nSL: ${sl}"
            if send_whatsapp_alert(st.session_state['wp_phone'], st.session_state['wp_api_key'], msg):
                st.success("Sent Successfully!")
            else:
                st.error("Failed to send!")
        else:
            st.warning("Please configure WP settings first!")

    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:450px;width:100%;">
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
    components.html(tradingview_html, height=450)

with tab_settings:
    st.markdown(f"<h3 style='color: #F0B90B;'>{t['settings_title']}</h3>", unsafe_allow_html=True)
    phone_input = st.text_input(t['phone_label'], value=st.session_state['wp_phone'])
    api_key_input = st.text_input(t['api_label'], value=st.session_state['wp_api_key'], type="password")
    
    if st.button(t['save_btn']):
        st.session_state['wp_phone'] = phone_input
        st.session_state['wp_api_key'] = api_key_input
        st.success("Saved!")
