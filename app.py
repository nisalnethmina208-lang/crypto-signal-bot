import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="Binance Pro Trading Center",
    page_icon="📈",
    layout="wide"
)

# Advanced Studio Light Theme & Modern Dashboard CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    .main-title {
        font-size: 30px;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }
    .sub-title-desc {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 25px;
    }
    /* Modern Glass/Clean Trading Card */
    .trading-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    .ticker-title {
        font-size: 36px;
        font-weight: 800;
        color: #0F172A !important;
        letter-spacing: -1px;
    }
    .binance-badge {
        background-color: #FEF3C7;
        color: #D97706;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 700;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    /* Modern Action Buttons */
    .buy-btn-box {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 14px 28px;
        font-size: 18px;
        font-weight: 700;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        letter-spacing: 0.5px;
    }
    .sell-btn-box {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        padding: 14px 28px;
        font-size: 18px;
        font-weight: 700;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        letter-spacing: 0.5px;
    }
    .trend-up { color: #059669 !important; font-weight: 700; }
    .trend-down { color: #DC2626 !important; font-weight: 700; }
    
    .stat-label { color: #64748B; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .stat-val { color: #0F172A; font-size: 20px; font-weight: 700; }

    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }
    
    /* Streamlit Sidebar Clean Look */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
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
    st.markdown("## ⚙️ Trading Control")
    st.markdown("Configure your live market feeds below.")
    
    coin_options = {
        "BTC/USDT": {"id": "bitcoin", "symbol": "BINANCE:BTCUSDT"},
        "ETH/USDT": {"id": "ethereum", "symbol": "BINANCE:ETHUSDT"},
        "BNB/USDT": {"id": "binancecoin", "symbol": "BINANCE:BNBUSDT"},
        "SOL/USDT": {"id": "solana", "symbol": "BINANCE:SOLUSDT"},
        "XRP/USDT": {"id": "ripple", "symbol": "BINANCE:XRPUSDT"},
        "ADA/USDT": {"id": "cardano", "symbol": "BINANCE:ADAUSDT"},
        "DOGE/USDT": {"id": "dogecoin", "symbol": "BINANCE:DOGEUSDT"},
        "AVAX/USDT": {"id": "avalanche-2", "symbol": "BINANCE:AVAXUSDT"},
        "TRX/USDT": {"id": "tron", "symbol": "BINANCE:TRXUSDT"},
        "DOT/USDT": {"id": "polkadot", "symbol": "BINANCE:DOTUSDT"},
        "MATIC/USDT": {"id": "polygon-ecosystem-token", "symbol": "BINANCE:MATICUSDT"},
        "LINK/USDT": {"id": "chainlink", "symbol": "BINANCE:LINKUSDT"},
        "UNI/USDT": {"id": "uniswap", "symbol": "BINANCE:UNIUSDT"},
        "ATOM/USDT": {"id": "cosmos", "symbol": "BINANCE:ATOMUSDT"},
        "LTC/USDT": {"id": "litecoin", "symbol": "BINANCE:LTCUSDT"},
        "NEAR/USDT": {"id": "near", "symbol": "BINANCE:NEARUSDT"},
        "APT/USDT": {"id": "aptos", "symbol": "BINANCE:APTUSDT"},
        "FTM/USDT": {"id": "fantom", "symbol": "BINANCE:FTMUSDT"},
        "ICP/USDT": {"id": "internet-computer", "symbol": "BINANCE:ICPUSDT"},
        "RENDER/USDT": {"id": "render-token", "symbol": "BINANCE:RNDRUSDT"},
        "INJ/USDT": {"id": "injective-protocol", "symbol": "BINANCE:INJUSDT"},
        "TIA/USDT": {"id": "celestia", "symbol": "BINANCE:TIAUSDT"},
        "ARB/USDT": {"id": "arbitrum", "symbol": "BINANCE:ARBUSDT"},
        "OP/USDT": {"id": "optimism", "symbol": "BINANCE:OPUSDT"},
        "SUI/USDT": {"id": "sui", "symbol": "BINANCE:SUIUSDT"},
        "SEI/USDT": {"id": "sei-network", "symbol": "BINANCE:SEIUSDT"},
        "PEPE/USDT": {"id": "pepe", "symbol": "BINANCE:PEPEUSDT"},
        "SHIB/USDT": {"id": "shiba-inu", "symbol": "BINANCE:SHIBUSDT"},
        "FLOKI/USDT": {"id": "floki", "symbol": "BINANCE:FLOKIUSDT"},
        "BONK/USDT": {"id": "bonk", "symbol": "BINANCE:BONKUSDT"}
    }
    
    selected_coin_display = st.selectbox("Select Market Pair:", list(coin_options.keys()), index=0)
    coin_id = coin_options[selected_coin_display]["id"]
    tv_symbol = coin_options[selected_coin_display]["symbol"]
    
    chart_interval = st.selectbox("Chart Timeframe:", ["1", "15", "60", "D"], index=1, format_func=lambda x: {"1": "1m", "15": "15m", "60": "1H", "D": "1D"}[x])
    st.markdown("---")
    st.caption("⚡ Powered by Binance & CoinGecko APIs")

# --- Main App Dashboard Layout ---
st.markdown(f'<p class="main-title">📈 Pro Trading Terminal</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-title-desc">Real-time market overview and advanced charting analysis for <b>{selected_coin_display}</b>.</p>', unsafe_allow_html=True)

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
action_type = "STRONG BUY" if is_uptrend else "STRONG SELL"
btn_class = "buy-btn-box" if is_uptrend else "sell-btn-box"
change_icon = "▲" if is_uptrend else "▼"

# Top Ticker & Signal Badge Row
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.markdown(f'<span class="binance-badge">Binance Spot</span>', unsafe_allow_html=True)
    st.markdown(f'<p class="ticker-title" style="margin-top: 8px;">{selected_coin_display}</p>', unsafe_allow_html=True)
with col_top2:
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="{btn_class}">{action_type} 🚀</div>', unsafe_allow_html=True)

# Modern Stats Overview Card
st.markdown(f"""
    <div class="trading-card">
        <table width="100%">
            <tr>
                <td><div class="stat-label">Live Price</div><div class="stat-val">${last_price:,.2f}</div></td>
                <td><div class="stat-label">24h Change</div><div class="stat-val {trend_class}">{change_icon} {change_24h:,.2f}%</div></td>
                <td><div class="stat-label">24h High</div><div class="stat-val" style="color: #059669;">${high_24h:,.2f}</div></td>
                <td><div class="stat-label">24h Low</div><div class="stat-val" style="color: #DC2626;">${low_24h:,.2f}</div></td>
            </tr>
        </table>
    </div>
""", unsafe_allow_html=True)

# --- TradingView Live Chart Widget ---
st.markdown("### 📊 Advanced Price Chart")

chart_html = f"""
<div class="tradingview-widget-container" style="height:520px;width:100%; border-radius: 12px; overflow: hidden; border: 1px solid #E2E8F0;">
  <div id="tradingview_chart" style="height:100%;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {{
    "autosize": true,
    "symbol": "{tv_symbol}",
    "interval": "{chart_interval}",
    "timezone": "Etc/UTC",
    "theme": "light",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#FFFFFF",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
st.components.v1.html(chart_html, height=540)

st.markdown("<br>", unsafe_allow_html=True)

# --- Notepad Section ---
st.markdown("### 📝 Strategy & Notes")
if 'notepad_content' not in st.session_state:
    st.session_state.notepad_content = ""

note_text = st.text_area("Notes Area", value=st.session_state.notepad_content, height=130, label_visibility="collapsed", placeholder="Write down your trading plans, entry points, or targets here...")

col_n1, col_n2, col_n3 = st.columns([1, 1, 4])
with col_n1:
    if st.button("💾 Save Notes", use_container_width=True):
        st.session_state.notepad_content = note_text
        st.success("Saved!")
with col_n2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.notepad_content = ""
        st.rerun()
