import streamlit as st
import requests
from streamlit_tradingview import st_tradingview

# Page Configuration
st.set_page_config(
    page_title="Binance Pro Trading Center",
    page_icon="📈",
    layout="wide"
)

# Dark Theme & Custom CSS (Binance Style)
st.markdown("""
    <style>
    .stApp {
        background-color: #121418;
        color: #FFFFFF;
    }
    .main-title {
        font-size: 28px;
        font-weight: bold;
        color: #F0B90B;
        margin-bottom: 10px;
    }
    .trading-card {
        background-color: #1E2329;
        border: 1px solid #2B313A;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .ticker-title {
        font-size: 32px;
        font-weight: bold;
        color: #F0B90B !important;
    }
    .binance-spot {
        color: #848E9C;
        font-size: 12px;
        text-transform: uppercase;
    }
    .buy-btn {
        background-color: #0ECB81;
        color: white;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        text-align: center;
        float: right;
    }
    .trend-up {
        color: #0ECB81 !important;
        font-weight: bold;
    }
    .stat-label { color: #848E9C; font-size: 13px; }
    .stat-val { color: #FFFFFF; font-size: 16px; font-weight: bold; }

    /* Notepad Styling */
    .stTextArea textarea {
        background-color: #1E2329 !important;
        color: #FFFFFF !important;
        border: 1px solid #2B313A !important;
    }
    </style>
""", unsafe_allow_html=True)

# Function to fetch live data from CoinGecko (Reliable in SL)
@st.cache_data(ttl=300)
def get_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_high=true&include_24hr_low=true"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

# --- Sidebar (Settings) ---
with st.sidebar:
    st.image("https://cryptologos.cc/logos/binance-coin-bnb-logo.png?v=032", width=50)
    st.markdown("## ⚙️ Binance Settings")
    
    # Coin Selection
    coin_options = {
        "BTC/USDT": "bitcoin",
        "ETH/USDT": "ethereum",
        "BNB/USDT": "binancecoin",
        "SOL/USDT": "solana",
        "XRP/USDT": "ripple",
        "ADA/USDT": "cardano"
    }
    selected_coin_display = st.selectbox("Select Market:", list(coin_options.keys()), index=0)
    coin_id = coin_options[selected_coin_display]
    
    # Chart Settings
    chart_interval = st.selectbox("Chart Interval:", ["1m", "5m", "15m", "1H", "4H", "1D"], index=2)
    
    st.markdown("---")
    st.write("Pro Features Enabled")

# --- Main App Layout ---
st.markdown(f'<p class="main-title">📈 Binance Live Trading Center - {selected_coin_display}</p>', unsafe_allow_html=True)

# Top Row (Ticker and Buy Button)
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.markdown(f'<p class="binance-spot">BINANCE SPOT</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="ticker-title">{selected_coin_display}</p>', unsafe_allow_html=True)
with col_top2:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="buy-btn">BUY 🚀</div>', unsafe_allow_html=True)

# Fetch and Display Live Stats
data = get_coin_data(coin_id)

if data and coin_id in data:
    price_data = data[coin_id]
    last_price = price_data.get('usd', 0.0)
    change_24h = price_data.get('usd_24h_change', 0.0)
    high_24h = price_data.get('usd_24h_high', 0.0)
    low_24h = price_data.get('usd_24h_low', 0.0)
    
    # Define Trend Color
    trend_class = "trend-up" if change_24h >= 0 else "trend-down"
    change_icon = "▲" if change_24h >= 0 else "▼"

    # Stats Card
    st.markdown(f"""
        <div class="trading-card">
            <table width="100%">
                <tr>
                    <td><div class="stat-label">LIVE PRICE</div><div class="stat-val">${last_price:,.2f}</div></td>
                    <td><div class="stat-label">24H CHANGE</div><div class="stat-val {trend_class}">{change_icon} {change_24h:,.2f}%</div></td>
                    <td><div class="stat-label">24H HIGH</div><div class="stat-val">${high_24h:,.2f}</div></td>
                    <td><div class="stat-label">24H LOW</div><div class="stat-val">${low_24h:,.2f}</div></td>
                </tr>
            </table>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("දත්ත ලබා ගැනීමේ දෝෂයක්! අන්තර්ජාලය පරීක්ෂා කරන්න.")

# --- Interactive Chart (Binance-like) ---
# This replaces the error message and the old static image
st.subheader("📊 Live Price Chart")
tv_symbol = f"BINANCE:{selected_coin_display.replace('/', '')}"
st_tradingview(
    symbol=tv_symbol,
    interval=chart_interval.replace('H', '60').replace('D', 'D'), # Convert to TV format
    theme="Dark",
    height=600,
    width="100%"
)

st.markdown("---")

# --- Notepad (Lower Section) ---
st.subheader("📝 Trading Notepad")
st.write("ඔබගේ වෙළඳ සැලසුම් හෝ සටහන් මෙහි ලියා තබා ගන්න.")

# Use session state to keep notes persistent
if 'notepad_content' not in st.session_state:
    st.session_state.notepad_content = ""

note_text = st.text_area("Notes Area", value=st.session_state.notepad_content, height=150, label_visibility="collapsed")

if st.button("Save Notes"):
    st.session_state.notepad_content = note_text
    st.success("Notes saved!")

# Optional: Clear Button
if st.button("Clear Notes"):
    st.session_state.notepad_content = ""
    st.rerun()
