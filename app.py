import streamlit as st
import requests

st.set_page_config(page_title="Binance Signal App VIP", page_icon="👑", layout="wide")

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
def get_data(cid):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd&include_24hr_change=true"
        return requests.get(url, timeout=5).json()
    except:
        return None

# Sidebar
with st.sidebar:
    st.markdown("### 👑 VIP Menu")
    page = st.selectbox("Navigation", ["Live Signal", "Notepad"])
    coins = {
        "BTC": {"id": "bitcoin", "sym": "BINANCE:BTCUSDT"}, 
        "ETH": {"id": "ethereum", "sym": "BINANCE:ETHUSDT"}, 
        "SOL": {"id": "solana", "sym": "BINANCE:SOLUSDT"},
        "BNB": {"id": "binancecoin", "sym": "BINANCE:BNBUSDT"},
        "XRP": {"id": "ripple", "sym": "BINANCE:XRPUSDT"}
    }
    sel = st.selectbox("Select Coin", list(coins.keys()))
    cid, tv_sym = coins[sel]["id"], coins[sel]["sym"]

data = get_data(cid)
price = data[cid]['usd'] if data and cid in data else 0.0
change = data[cid]['usd_24h_change'] if data and cid in data else 0.0
up = change >= 0

# App Header (VIP Title)
st.markdown('<p class="vip-header">👑 Binance Signal App VIP <span class="vip-badge">VIP Pro</span></p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-desc">Real-time automated technical signals and targets for <b>{sel}/USDT</b>.</p>', unsafe_allow_html=True)

if page == "Live Signal":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Price:** ${price:,.2f} | **24h Change:** <span style='color: {'#059669' if up else '#DC2626'};'>{change:,.2f}%</span>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="signal-box" style="background: {"#10B981" if up else "#EF4444"};">{"BUY 🚀" if up else "SELL 🔻"}</div>', unsafe_allow_html=True)

    # TP / SL Compact Cards
    tp1 = price * (1.015 if up else 0.985)
    tp2 = price * (1.035 if up else 0.965)
    sl = price * (0.992 if up else 1.008)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="t-card">Entry<br><b>${price:,.2f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="t-card">TP 1<br><b style="color: #059669;">${tp1:,.2f}</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="t-card">TP 2<br><b style="color: #059669;">${tp2:,.2f}</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="t-card">SL<br><b style="color: #DC2626;">${sl:,.2f}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Small TradingView Chart
    chart_html = f"""
    <div class="tradingview-widget-container" style="height:350px;width:100%">
      <div id="tv_chart" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{"autosize": true, "symbol": "{tv_sym}", "interval": "15", "timezone": "Etc/UTC", "theme": "light", "style": "1", "locale": "en", "container_id": "tv_chart"}});
      </script>
    </div>
    """
    st.components.v1.html(chart_html, height=360)

elif page == "Notepad":
    st.markdown('### 📝 VIP Trading Notepad', unsafe_allow_html=True)
    if 'note' not in st.session_state: st.session_state.note = ""
    st.session_state.note = st.text_area("Note", value=st.session_state.note, height=200, label_visibility="collapsed", placeholder="Write down your VIP notes here...")
    if st.button("Clear Notes"): st.session_state.note = ""; st.rerun()
