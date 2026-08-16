import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Binance Signals Pro", page_icon="📈", layout="wide"
)

# --- Session State for Authentication (ලොක් වීම වළක්වන කොටස) ---
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

# Valid Access Keys
VALID_KEYS = ["KEY-USER1-8899", "KEY-USER2-5544", "VIP-SIGNAL-2026"]

# --- Lock / Authentication Screen ---
if not st.session_state.authenticated:
  st.markdown(
      "<h2 style='text-align: center; color: white;'>🔐 Enter Access Key to"
      " Unlock</h2>",
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
  st.stop()

# --- Main App Design (රූපයේ ඇති ආකාරයේ පෙනුම) ---

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

# Sidebar for Coin Selection
selected_coin = st.sidebar.selectbox("Select Coin", coins_100)

# Top Card Section (රූපයේ ඇති ආකාරයට UI සකස් කර ඇත)
st.markdown(
    """
    <style>
    .spot-card {
        background-color: #161a25;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2b313a;
    }
    </style>
""",
    unsafe_allow_html=True,
)

with st.container():
  st.markdown('<div class="spot-card">', unsafe_allow_html=True)

  top_col1, top_col2 = st.columns([2, 1])
  with top_col1:
    st.markdown(
        "<p style='color: #848e9c; margin-bottom: 0px; font-size: 14px;'>BINANCE"
        " SPOT</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<h1 style='color: #fcd535; margin-top: 0px;'>{selected_coin}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color: #f6465d; font-weight: bold;'>● Downtrend Structure"
        " (DOWN)</p>",
        unsafe_allow_html=True,
    )

  with top_col2:
    # SELL බොත්තම රූපයේ ඇති පරිදි
    st.markdown(
        "<br><div style='text-align: right;'><span style='background-color:"
        " #f6465d; color: white; padding: 12px 25px; border-radius: 6px; font-weight:"
        " bold; font-size: 18px;'>SELL 📉</span></div>",
        unsafe_allow_html=True,
    )

  st.markdown("<hr style='border-color: #2b313a;'>", unsafe_allow_html=True)

  # Live Price & Metrics
  p1, p2, p3, p4 = st.columns(4)
  p1.markdown(
      "<p style='color: #848e9c; margin-bottom: 2px;'>LIVE PRICE</p><h4"
      " style='color: white;'>$0.00</h4>",
      unsafe_allow_html=True,
  )
  p2.markdown(
      "<p style='color: #848e9c; margin-bottom: 2px;'>24H CHANGE</p><h4"
      " style='color: #f6465d;'>+0.00%</h4>",
      unsafe_allow_html=True,
  )
  p3.markdown(
      "<p style='color: #848e9c; margin-bottom: 2px;'>24H HIGH</p><h4"
      " style='color: white;'>$0.00</h4>",
      unsafe_allow_html=True,
  )
  p4.markdown(
      "<p style='color: #848e9c; margin-bottom: 2px;'>24H LOW</p><h4"
      " style='color: white;'>$0.00</h4>",
      unsafe_allow_html=True,
  )

  st.markdown("<br>", unsafe_allow_html=True)

  # TP සහ SL කොටු (Boxes)
  b1, b2, b3 = st.columns(3)
  with b1:
    st.markdown(
        "<div style='border: 1px solid #0ecb81; padding: 15px; border-radius:"
        " 8px; text-align: center;'><p style='color: #0ecb81; margin: 0;'>🎯 TP"
        " 1</p><h3 style='color: white; margin: 5px 0 0 0;'>$0.00</h3></div>",
        unsafe_allow_html=True,
    )
  with b2:
    st.markdown(
        "<div style='border: 1px solid #0ecb81; padding: 15px; border-radius:"
        " 8px; text-align: center;'><p style='color: #0ecb81; margin: 0;'>🎯 TP"
        " 2</p><h3 style='color: white; margin: 5px 0 0 0;'>$0.00</h3></div>",
        unsafe_allow_html=True,
    )
  with b3:
    st.markdown(
        "<div style='border: 1px solid #f6465d; padding: 15px; border-radius:"
        " 8px; text-align: center;'><p style='color: #f6465d; margin: 0;'>🛡️"
        " SL</p><h3 style='color: white; margin: 5px 0 0 0;'>$0.00</h3></div>",
        unsafe_allow_html=True,
    )

  st.markdown("</div>", unsafe_allow_html=True)

# --- TradingView Live Chart (වැඩ කරන නිවැරදි සංකේතය සමඟ) ---
st.markdown("<br>", unsafe_allow_html=True)

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
