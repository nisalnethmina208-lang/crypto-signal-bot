import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(page_title="Binance Signals Pro", page_icon="📈", layout="wide")

# --- Session State for Authentication ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

VALID_KEYS = ["KEY-USER1-8899", "KEY-USER2-5544", "VIP-SIGNAL-2026"]

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: white;'>🔐 Enter Access Key to Unlock</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        entered_key = st.text_input("Access Key", type="password")
        if st.button("Unlock App", use_container_width=True):
            if entered_key in VALID_KEYS:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Access Key.")
    st.stop()

# --- Main App ---
# කොයින් 100 ලැයිස්තුව
coins_100 = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "TRXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "POLUSDT", "NEARUSDT", "LTCUSDT", "UNIUSDT", "BCHUSDT", "ATOMUSDT", "ICPUSDT", "APTUSDT", "ETCUSDT", "FILUSDT", "STXUSDT", "SUIUSDT", "ARBUSDT", "OPUSDT", "INJUSDT", "IMXUSDT", "GRTUSDT", "RNDRUSDT", "TIAUSDT", "SEIUSDT", "PEPEUSDT", "SHIBUSDT", "FLOKIUSDT", "BONKUSDT", "RENDERUSDT", "FETUSDT", "AGIXUSDT", "OCEANUSDT", "WLDUSDT", "FTMUSDT", "SANDUSDT", "MANAUSDT", "AXSUSDT", "GALAUSDT", "THETAUSDT", "EGLDUSDT", "KASUSDT", "HBARUSDT", "ALGOUSDT", "VETUSDT", "FLOWUSDT", "CHZUSDT", "CRVUSDT", "MKRUSDT", "AAVEUSDT", "SNXUSDT", "COMPUSDT", "LDOUSDT", "RUNEUSDT", "CAKEUSDT", "FXSUSDT", "PENDLEUSDT", "DYDXUSDT", "GMXUSDT", "JUPUSDT", "PYTHUSDT", "JTOUSDT", "ONDOUSDT", "ZROUSDT", "BLURUSDT", "PORTALUSDT", "PIXELUSDT", "MEMEUSDT", "ORDIUSDT", "SATSUSDT", "RATSUSDT", "AXLUSDT", "ALTUSDT", "MANTAUSDT", "XAIUSDT", "NFPUSDT", "AIUSDT", "ACEUSDT", "ZETAUSDT", "RONINUSDT", "DYMUSDT", "BOMEUSDT", "SAGAUSDT", "TNSRUSDT", "OMUSDT", "BBUSDT", "NOTUSDT", "IOUSDT", "ZKUSDT", "LISTAUSDT"]

# කොයින් තෝරන කොටුව කෙළින්ම පේන්න තියන්න
st.subheader("Select Your Trading Pair")
selected_coin = st.selectbox("Choose a coin from the list below:", coins_100)

# CSS for UI
st.markdown("""
    <style>
    .spot-card { background-color: #161a25; padding: 20px; border-radius: 10px; border: 1px solid #2b313a; }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="spot-card">', unsafe_allow_html=True)
    
    # Top Section
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"<h1 style='color: #fcd535;'>{selected_coin}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #f6465d; font-weight: bold;'>● Downtrend Structure (DOWN)</p>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='text-align: right;'><span style='background-color: #f6465d; color: white; padding: 10px 20px; border-radius: 5px;'>SELL 📉</span></div>", unsafe_allow_html=True)

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("PRICE", "$0.00")
    m2.metric("24H CHG", "+0.00%")
    m3.metric("HIGH", "$0.00")
    m4.metric("LOW", "$0.00")

    # TP/SL
    t1, t2, t3 = st.columns(3)
    t1.markdown("<div style='border: 1px solid #0ecb81; padding:10px; text-align:center;'>🎯 TP 1<br><b>$0.00</b></div>", unsafe_allow_html=True)
    t2.markdown("<div style='border: 1px solid #0ecb81; padding:10px; text-align:center;'>🎯 TP 2<br><b>$0.00</b></div>", unsafe_allow_html=True)
    t3.markdown("<div style='border: 1px solid #f6465d; padding:10px; text-align:center;'>🛡️ SL<br><b>$0.00</b></div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# TradingView
tv_symbol = f"BINANCE:{selected_coin}"
st.components.v1.html(f"""
<div class="tradingview-widget-container">
  <div id="tv_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "width": "100%", "height": 400, "symbol": "{tv_symbol}",
    "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_chart"
  }});
  </script>
</div>
""", height=420)
