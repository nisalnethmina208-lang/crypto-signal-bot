import streamlit as st
import requests

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
    .sell-btn {
        background-color: #F6465D;
        color: white;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        text-align: center;
        float: right;
    }
    .trend-up { color: #0ECB81 !important; font-weight: bold; }
    .trend-down { color: #F6465D !important; font-weight: bold; }
    .stat-label { color: #848E9C; font-size: 13px; }
    .stat-val { color: #FFFFFF; font-size: 16px; font-weight: bold; }

    .stTextArea textarea {
        background-color: #1E2329 !important;
        color: #FFFFFF !important;
        border: 1px solid #2B313A !important;
    }
    </style>
""", unsafe_allow_html=True)

# Function to fetch live data from CoinGecko
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
    st.markdown("## ⚙️ Binance Settings")
    
    coin_options = {
        "BTC/USDT": {"id": "bitcoin", "symbol": "BINANCE:BTCUSDT"},
        "ETH/USDT": {"id": "ethereum", "symbol": "BINANCE:ETHUSDT"},
        "BNB/USDT": {"id": "binancecoin", "symbol": "BINANCE:BNBUSDT"},
        "SOL/USDT": {"id": "solana", "symbol": "BINANCE:SOLUSDT"},
        "XRP/USDT": {"id": "ripple", "symbol": "BINANCE:XRPUSDT"},
        "ADA/USDT": {"id": "cardano", "symbol": "BINANCE:ADAUSDT"}
    }
    selected_coin_display = st.selectbox("Select Market:", list(coin_options.keys()), index=0)
    coin_id = coin_options[selected_coin_display]["id"]
    tv_symbol = coin_options[selected_coin_display]["symbol"]
    
    chart_interval = st.selectbox("Chart Interval:", ["1", "15", "60", "D"], index=1, format_func=lambda x: {"1": "1m", "15": "15m", "60": "1H", "D": "1D"}[x])
    st.markdown("---")

# --- Main App Layout ---
st.markdown(f'<p class="main-title">📈 Binance Live Trading Center - {selected_coin_display}</p>', unsafe_allow_html=True)

# Fetch Live Stats
data = get_coin_data(coin_id)

last_price = 0.0
change_24h = 0.0
high_24h = 0.0
low_24h = 0.0

if data and coin_id in data:
    price_data = data[coin_id]
    last_price = price_data.get('usd', 0.0)
    change_24h = price_data.get('usd_24h_change', 0.0)
    high_24h = price_data.get('usd_24h_high', last_price * 1.02)
    low_24h = price_data.get('usd_24h_low', last_price * 0.98)

is_uptrend = change_24h >= 0
trend_class = "trend-up" if is_uptrend else "trend-down"
action_type = "BUY" if is_uptrend else "SELL"
btn_class = "buy-btn" if is_uptrend else "sell-btn"
change_icon = "▲" if is_uptrend else "▼"

# Top Row
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.markdown(f'<p class="binance-spot">BINANCE SPOT</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="ticker-title">{selected_coin_display}</p>', unsafe_allow_html=True)
with col_top2:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown(f'<div class="{btn_class}">{action_type} 🚀</div>', unsafe_allow_html=True)

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

# --- TradingView Live Chart Widget (Direct HTML Embed - No Error) ---
st.subheader("📊 Live Price Chart")

chart_html = f"""
<div class="tradingview-widget-container" style="height:500px;width:100%">
  <div id="tradingview_chart" style="height:100%;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {{
    "autosize": true,
    "symbol": "{tv_symbol}",
    "interval": "{chart_interval}",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#1e2329",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
st.components.v1.html(chart_html, height=520)

st.markdown("---")

# --- Notepad Section ---
st.subheader("📝 Trading Notepad")
if 'notepad_content' not in st.session_state:
    st.session_state.notepad_content = ""

note_text = st.text_area("Notes Area", value=st.session_state.notepad_content, height=120, label_visibility="collapsed")

col_n1, col_n2 = st.columns(2)
with col_n1:
    if st.button("Save Notes", use_container_width=True):
        st.session_state.notepad_content = note_text
        st.success("Notes saved successfully!")
with col_n2:
    if st.button("Clear Notes", use_container_width=True):
        st.session_state.notepad_content = ""
        st.rerun()
