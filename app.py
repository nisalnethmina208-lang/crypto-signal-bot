import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(page_title="Binance Signal Center", layout="centered")

# Tabs
tab1, tab2 = st.tabs(["📊 Signals & Market", "⚙️ Settings"])

with tab1:
    st.markdown("<h2 style='color: #F0B90B;'>⚡ Binance Signal Center</h2>", unsafe_allow_html=True)
    
    # Popular Crypto Pairs Dropdown
    coin_list = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", 
        "XRP/USDT", "ADA/USDT", "DOGE/USDT", "PEPE/USDT", "AVAX/USDT"
    ]
    
    selected_pair = st.selectbox("Coin Pair එක තෝරන්න:", coin_list, index=0)
    
    # TradingView symbol format (e.g. BTCUSDT)
    tv_symbol = selected_pair.replace("/", "")
    
    st.markdown("---")

    # Pair Details
    st.markdown("<span style='color: #888; font-size: 14px;'>Selected Pair</span>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top:-5px; margin-bottom: 5px; font-weight: bold;'>{selected_pair}</h1>", unsafe_allow_html=True)
    st.markdown("<span style='background-color: #133E2B; color: #26A69A; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: bold;'>↑ Active Pair</span>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Signal Details
    st.markdown("<span style='color: #888; font-size: 14px;'>Current Signal</span>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin-top:-5px; margin-bottom: 5px; font-weight: bold;'>STRONG BUY 🟢</h1>", unsafe_allow_html=True)
    st.markdown("<span style='background-color: #133E2B; color: #26A69A; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: bold;'>↑ EMA 20/50 Cross</span>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Dynamic TradingView Chart Widget
    tradingview_code = f"""
    <div class="tradingview-widget-container" style="height:100%;width:100%">
      <div id="tradingview_chart" style="height:450px;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "BINANCE:{tv_symbol}",
        "interval": "15",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(tradingview_code, height=470)

with tab2:
    st.subheader("Settings")
    st.write("Settings configuration controls.")
