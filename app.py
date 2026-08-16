import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Binance Signals Pro", page_icon="📈", layout="wide"
)

# --- Session State for Authentication ---
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

# Valid Access Keys (ඔබට අවශ්‍ය නම් මෙයට තවත් කීස් එකතු කරගත හැක)
VALID_KEYS = ["KEY-USER1-8899", "KEY-USER2-5544", "VIP-SIGNAL-2026"]

# --- Lock / Authentication Screen ---
if not st.session_state.authenticated:
  st.markdown(
      "<h2 style='text-align: center;'>🔐 Enter Access Key to Unlock</h2>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    entered_key = st.text_input("Access Key", type="password")
    if st.button("Unlock App", use_container_width=True):
      if entered_key in VALID_KEYS:
        st.session_state.authenticated = True
        st.success("Access Granted! Loading App...")
        st.rerun()
      else:
        st.error("Invalid Access Key. Please try again.")
  st.stop()  # ලොක් වී ඇති තාක් පහළ කෝඩ් එක ධාවනය වීම නවත්වයි

# --- Main App (Unloaded / Unlocked Area) ---
st.title("📈 Binance Spot Signals Pro")
st.markdown("---")

# ජනප්‍රිය කොයින් 100 ක ලැයිස්තුව (USDT Pairs)
coins_100 = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "TRXUSDT",
    "DOTUSDT",
    "LINKUSDT",
    "MATICUSDT",
    "POLUSDT",
    "NEARUSDT",
    "LTCUSDT",
    "UNIUSDT",
    "BCHUSDT",
    "ATOMUSDT",
    "ICPUSDT",
    "APTUSDT",
    "ETCUSDT",
    "FILUSDT",
    "STXUSDT",
    "SUIUSDT",
    "ARBUSDT",
    "OPUSDT",
    "INJUSDT",
    "IMXUSDT",
    "GRTUSDT",
    "RNDRUSDT",
    "TIAUSDT",
    "SEIUSDT",
    "PEPEUSDT",
    "SHIBUSDT",
    "FLOKIUSDT",
    "BONKUSDT",
    "RENDERUSDT",
    "FETUSDT",
    "AGIXUSDT",
    "OCEANUSDT",
    "WLDUSDT",
    "ARBUSDT",
    "FTMUSDT",
    "SANDUSDT",
    "MANAUSDT",
    "AXSUSDT",
    "GALAUSDT",
    "THETAUSDT",
    "EGLDUSDT",
    "KASUSDT",
    "HBARUSDT",
    "ALGOUSDT",
    "VETUSDT",
    "FLOWUSDT",
    "CHZUSDT",
    "CRVUSDT",
    "MKRUSDT",
    "AAVEUSDT",
    "SNXUSDT",
    "COMPUSDT",
    "LDOUSDT",
    "RUNEUSDT",
    "CAKEUSDT",
    "CRVUSDT",
    "FXSUSDT",
    "PENDLEUSDT",
    "DYDXUSDT",
    "GMXUSDT",
    "JUPUSDT",
    "PYTHUSDT",
    "JTOUSDT",
    "ONDOUSDT",
    "ZROUSDT",
    "BLURUSDT",
    "PORTALUSDT",
    "PIXELUSDT",
    "MEMEUSDT",
    "ORDIUSDT",
    "SATSUSDT",
    "RATSUSDT",
    "AXLUSDT",
    "ALTUSDT",
    "MANTAUSDT",
    "XAIUSDT",
    "NFPUSDT",
    "AIUSDT",
    "ACEUSDT",
    "ZETAUSDT",
    "RONINUSDT",
    "DYMUSDT",
    "PORTALUSDT",
    "BOMEUSDT",
    "SAGAUSDT",
    "TNSRUSDT",
    "OMUSDT",
    "BBUSDT",
    "NOTUSDT",
    "IOUSDT",
    "ZKUSDT",
    "LISTAUSDT",
]

# Sidebar Selection
selected_coin = st.sidebar.selectbox("Select Coin", coins_100)

# UI Layout for Signals
col1, col2 = st.columns([2, 1])

with col1:
  st.subheader(f"Analysis for {selected_coin}")
  st.info(
      "Live market data and technical structure indicators are active for this"
      " asset."
  )

  # Mock / Dynamic Display for Prices & Signals
  st.markdown(
      f"### **{selected_coin}** <span"
      " style='color:green;float:right;'>BULLISH</span>",
      unsafe_allow_html=True,
  )

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Live Price", "$0.00", "+0.00%")
  m2.metric("24h Change", "+2.45%", "▲")
  m3.metric("24h High", "$0.00")
  m4.metric("24h Low", "$0.00")

  c1, c2, c3 = st.columns(3)
  c1.success("🎯 TP 1: $0.00")
  c2.success("🎯 TP 2: $0.00")
  c3.error("🛡️ SL: $0.00")

with col2:
  st.subheader("Market Trend")
  st.write("Current Trend: **Uptrend Structure (UP)**")
  st.progress(75)

# TradingView Widget Embed (Dynamic based on selected coin)
st.markdown("---")
st.subheader("Live TradingView Chart")

# Clean symbol format for TradingView (e.g., BINANCE:BTCUSDT)
tv_symbol = f"BINANCE:{selected_coin}"

tradingview_html = f"""
<div class="tradingview-widget-container" style="height:500px;width:100%">
  <div id="tradingview_widget" style="height:100%;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {{
    "width": "100%",
    "height": 500,
    "symbol": "{tv_symbol}",
    "interval": "15",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_widget"
  }}
  );
  </script>
</div>
"""

st.components.v1.html(tradingview_html, height=520)
