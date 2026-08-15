import streamlit as st
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="Crypto Signal & Market",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Streamlit Branding එක Hide කිරීම සහ Mobile Theme එක සකස් කිරීම
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
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
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

# Navigation Tabs (Pages 2)
tab_main, tab_settings = st.tabs(["📊 Signals & Market", "⚙️ Settings"])

# ----------------- PAGE 1: SIGNALS & MARKET -----------------
with tab_main:
    st.markdown("<h3 style='text-align: center; color: #F0B90B; margin-bottom: 15px;'>⚡ Binance Signal Center</h3>", unsafe_allow_html=True)
    
    # Top Live Indicators / Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Pair", value="BTC/USDT", delta="+1.45% (24h)")
    with col2:
        st.metric(label="Current Signal", value="STRONG BUY 🟢", delta="EMA 20/50 Cross")
    
    st.write("")
    
    # Interactive Binance TradingView Chart (Real-time Zoom & Indicators)
    tradingview_html = """
    <div class="tradingview-widget-container" style="height:480px;width:100%;">
      <div id="tradingview_chart" style="height:100%;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({
          "autosize": true,
          "symbol": "BINANCE:BTCUSDT",
          "interval": "15",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "enable_publishing": false,
          "hide_side_toolbar": false,
          "allow_symbol_change": true,
          "details": true,
          "container_id": "tradingview_chart"
      });
      </script>
    </div>
    """
    components.html(tradingview_html, height=480)

# ----------------- PAGE 2: SETTINGS -----------------
with tab_settings:
    st.markdown("<h3 style='color: #F0B90B;'>⚙️ App Settings</h3>", unsafe_allow_html=True)
    
    st.subheader("API Connections")
    st.text_input("Binance API Key", type="password")
    st.text_input("Binance Secret Key", type="password")
    
    st.subheader("Signal Configuration")
    st.selectbox("Default Timeframe", ["1m", "5m", "15m", "1h", "4h", "1D"], index=2)
    st.slider("RSI Overbought Threshold", 60, 80, 70)
    st.slider("RSI Oversold Threshold", 20, 40, 30)
    
    st.checkbox("Enable Sound Alerts", value=True)
    st.checkbox("Enable Push Notifications", value=True)
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")
