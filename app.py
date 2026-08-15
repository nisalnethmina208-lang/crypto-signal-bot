import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import urllib.parse

# Streamlit Page Config
st.set_page_config(page_title="Pro Crypto Signal & Alert Bot", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Modern UI
st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #2a2e39;
        margin-bottom: 10px;
    }
    .buy-card {
        background: linear-gradient(135deg, #0e3a2f 0%, #135242 100%);
        border: 1px solid #00c853;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: #ffffff;
    }
    .sell-card {
        background: linear-gradient(135deg, #3e1215 0%, #5c1b1f 100%);
        border: 1px solid #ff1744;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: #ffffff;
    }
    .neutral-card {
        background: linear-gradient(135deg, #332b12 0%, #4d401b 100%);
        border: 1px solid #ffc107;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: #ffffff;
    }
    .badge-title {
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    .tp-sl-box {
        background-color: #131722;
        border-radius: 8px;
        padding: 10px;
        margin-top: 10px;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

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

# Notification Functions
def send_telegram_alert(bot_token, chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200
    except Exception:
        return False

def send_whatsapp_alert(phone_number, api_key, message):
    try:
        # Using CallMeBot API for Free WhatsApp Messages
        encoded_msg = urllib.parse.quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={encoded_msg}&apikey={api_key}"
        res = requests.get(url, timeout=10)
        return res.status_code == 200
    except Exception:
        return False

# UI Layout
st.title("⚡ Binance Crypto Signal & Alert Center")

# Sidebar Configuration
st.sidebar.header("⚙️ Market Options")
all_symbols = get_all_usdt_symbols()
default_index = all_symbols.index('BTCUSDT') if 'BTCUSDT' in all_symbols else 0

selected_symbol = st.sidebar.selectbox("🪙 Coin එක තෝරන්න:", all_symbols, index=default_index)
timeframe = st.sidebar.selectbox("⏱️ Timeframe එක:", ["15m", "1h", "4h", "1d"], index=1)

st.sidebar.divider()
st.sidebar.header("🔔 Alert Settings")

alert_platform = st.sidebar.radio("Alert යවන්න ඕන Platform එක:", ["None", "Telegram", "WhatsApp", "Both"])

tg_token = ""
tg_chat_id = ""
wa_phone = ""
wa_apikey = ""

if alert_platform in ["Telegram", "Both"]:
    st.sidebar.subheader("✈️ Telegram Setup")
    tg_token = st.sidebar.text_input("Bot Token", type="password", help="BotFather මඟින් ලබාගත් Token එක")
    tg_chat_id = st.sidebar.text_input("Chat ID", help="ඔබේ Telegram Chat ID එක")

if alert_platform in ["WhatsApp", "Both"]:
    st.sidebar.subheader("💬 WhatsApp Setup")
    wa_phone = st.sidebar.text_input("Phone No (with country code)", placeholder="+94771234567")
    wa_apikey = st.sidebar.text_input("CallMeBot API Key", type="password")

df = get_klines(selected_symbol, interval=timeframe)

if not df.empty and len(df) >= 50:
    df = calculate_indicators(df)

    current_price = df['close'].iloc[-1]
    current_rsi = df['RSI'].iloc[-1]
    ema_20 = df['EMA_20'].iloc[-1]

    # Signal Logic
    signal_type = "NEUTRAL"
    card_class = "neutral-card"
    signal_icon = "⏳"
    tp1, tp2, sl = 0, 0, 0

    if current_rsi < 35 and current_price > ema_20:
        signal_type = "STRONG BUY"
        card_class = "buy-card"
        signal_icon = "🚀"
        tp1 = current_price * 1.02
        tp2 = current_price * 1.04
        sl = current_price * 0.985

    elif current_rsi < 40:
        signal_type = "BUY"
        card_class = "buy-card"
        signal_icon = "📈"
        tp1 = current_price * 1.015
        tp2 = current_price * 1.03
        sl = current_price * 0.99

    elif current_rsi > 65 and current_price < ema_20:
        signal_type = "STRONG SELL"
        card_class = "sell-card"
        signal_icon = "🔻"
        tp1 = current_price * 0.98
        tp2 = current_price * 0.96
        sl = current_price * 1.015

    elif current_rsi > 60:
        signal_type = "SELL"
        card_class = "sell-card"
        signal_icon = "📉"
        tp1 = current_price * 0.985
        tp2 = current_price * 0.97
        sl = current_price * 1.01

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"📊 {selected_symbol} Live Chart ({timeframe})")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            name="Price", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        ))
        fig.add_trace(go.Scatter(x=df['time'], y=df['EMA_20'], mode='lines', name='EMA 20', line=dict(color='#ff9800', width=1.5)))
        fig.add_trace(go.Scatter(x=df['time'], y=df['EMA_50'], mode='lines', name='EMA 50', line=dict(color='#2196f3', width=1.5)))
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=480, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🎯 Live Signal Dashboard")
        
        # Styled Signal Card
        st.markdown(f"""
        <div class="{card_class}">
            <div>CURRENT SIGNAL</div>
            <div class="badge-title">{signal_icon} {signal_type}</div>
            <hr style="border:0.5px solid rgba(255,255,255,0.2); margin:10px 0;">
            <div style="font-size:20px; font-weight:bold;">Entry: ${current_price:,.4f}</div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        m1, m2 = st.columns(2)
        m1.metric("RSI (14)", f"{current_rsi:.1f}")
        m2.metric("Timeframe", timeframe)

        if signal_type != "NEUTRAL":
            st.markdown(f"""
            <div class="tp-sl-box">
                <b>🎯 Target 1 (TP1):</b> <span style="color:#26a69a;">${tp1:,.4f}</span><br>
                <b>🎯 Target 2 (TP2):</b> <span style="color:#00e676;">${tp2:,.4f}</span><br>
                <b>🛡️ Stop Loss (SL):</b> <span style="color:#ff5252;">${sl:,.4f}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💡 Market එක Neutral මට්ටමේ පවතී. සුදුසු Entry එකක් ලැබෙන තෙක් රැඳී සිටින්න.")

        st.divider()

        # Send Alert Button
        if alert_platform != "None":
            if st.button("📲 Send Signal Alert Now", use_container_width=True):
                alert_text = f"""🚨 *CRYPTO SIGNAL ALERT* 🚨

🪙 *Coin:* {selected_symbol}
⏱️ *Timeframe:* {timeframe}
📊 *Signal:* {signal_icon} {signal_type}
💵 *Price:* ${current_price:,.4f}
📈 *RSI:* {current_rsi:.1f}

🎯 *TP1:* ${tp1:,.4f}
🎯 *TP2:* ${tp2:,.4f}
🛡️ *SL:* ${sl:,.4f}
"""
                success_msg = []
                if alert_platform in ["Telegram", "Both"] and tg_token and tg_chat_id:
                    if send_telegram_alert(tg_token, tg_chat_id, alert_text):
                        success_msg.append("Telegram")
                
                if alert_platform in ["WhatsApp", "Both"] and wa_phone and wa_apikey:
                    if send_whatsapp_alert(wa_phone, wa_apikey, alert_text):
                        success_msg.append("WhatsApp")

                if success_msg:
                    st.success(f"✅ Alert sent successfully via {', '.join(success_msg)}!")
                else:
                    st.error("❌ Alert එක යැවීමට නොහැකි විය. Details හරියට දුන්නාදැයි බලන්න.")

else:
    st.error("Data load කරගැනීමට නොහැකි විය. කරුණාකර පිටුව Refresh කරන්න.")
