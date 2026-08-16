import streamlit as st
import streamlit.components.v1 as components
import requests

# Page Configuration (Browser Tab එකේ නම සහ Icon එක)
st.set_page_config(
    page_title="Binance Pro Signal Center", 
    page_icon="⚡", 
    layout="centered"
)

# Initialize Session State
if "tp1_pct" not in st.session_state:
    st.session_state["tp1_pct"] = 2.0
if "tp2_pct" not in st.session_state:
    st.session_state["tp2_pct"] = 4.0
if "sl_pct" not in st.session_state:
    st.session_state["sl_pct"] = 2.0
if "timeframe" not in st.session_state:
    st.session_state["timeframe"] = "15"

# Multi-API Live Data Fetcher
def fetch_live_market_data(symbol):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # 1. Binance Global API
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            data = res.json()
            return float(data["lastPrice"]), float(data["priceChangePercent"]), float(data["highPrice"]), float(data["lowPrice"])
    except Exception:
        pass

    # 2. Binance US API
    try:
        url = f"https://api.binance.us/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            data = res.json()
            return float(data["lastPrice"]), float(data["priceChangePercent"]), float(data["highPrice"]), float(data["lowPrice"])
    except Exception:
        pass

    # 3. CryptoCompare API
    try:
        coin = symbol.replace("USDT", "")
        url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={coin}&tsyms=USDT"
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            d = res.json()["RAW"][coin]["USDT"]
            return float(d["PRICE"]), float(d["CHANGEPCT24HOUR"]), float(d["HIGH24HOUR"]), float(d["LOW24HOUR"])
    except Exception:
        pass

    return 0.0, 0.0, 0.0, 0.0


# ---------------------------------------------------------
# MAIN APP HEADER BANNER (App එකට එද්දිම උඩින්ම වැටෙන කොටස)
# ---------------------------------------------------------
st.markdown("""
<div style="background: linear-gradient(135deg, #1E2329 0%, #0B0E11 100%); padding: 20px; border-radius: 16px; border: 1px solid #F0B90B; margin-bottom: 20px; text-align: center; box-shadow: 0px 4px 15px rgba(240, 185, 11, 0.15);">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
        <span style="font-size: 32px;">⚡</span>
        <h1 style="color: #F0B90B; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;">BINANCE PRO SIGNAL CENTER</h1>
    </div>
    <p style="color: #848E9C; margin: 6px 0 0 0; font-size: 13px; font-weight: 500;">Real-Time Crypto Signals & Technical Analysis Dashboard</p>
    <div style="margin-top: 10px;">
        <span style="background-color: rgba(14, 203, 129, 0.2); color: #0ECB81; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; border: 1px solid #0ECB81;">● LIVE API CONNECTED</span>
    </div>
</div>
""", unsafe_allow_html=True)


# Interface Tabs
tab1, tab2 = st.tabs(["📊 Live Trading Center", "⚙️ Signal Settings"])

with tab1:
    popular_coins = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
        "APT/USDT", "ADA/USDT", "DOGE/USDT", "PEPE/USDT", "AVAX/USDT",
        "LINK/USDT", "DOT/USDT", "NEAR/USDT", "SUI/USDT", "SHIB/USDT"
    ]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_pair = st.selectbox("Coin Pair එක තෝරන්න:", popular_coins)
    with col2:
        custom_input = st.text_input("Coin එක Search කරන්න:", placeholder="eg: RUNE")
        
    if custom_input.strip():
        custom_symbol = custom_input.upper().strip().replace("USDT", "")
        selected_pair = f"{custom_symbol}/USDT"

    tv_symbol = selected_pair.replace("/", "")

    # Fetch Real-time Market Data
    current_price, price_change_pct, high_price, low_price = fetch_live_market_data(tv_symbol)

    # Technical Signal Rules
    if price_change_pct >= 2.0:
        signal_badge, signal_bg = "STRONG BUY 🚀", "#0ECB81"
        trend_text, trend_color = "Bullish Momentum (Strong UP)", "#0ECB81"
        is_buy = True
    elif price_change_pct > 0:
        signal_badge, signal_bg = "BUY 📈", "#26A69A"
        trend_text, trend_color = "Uptrend Structure (UP)", "#26A69A"
        is_buy = True
    elif price_change_pct <= -2.0:
        signal_badge, signal_bg = "STRONG SELL 🔻", "#F6465D"
        trend_text, trend_color = "Bearish Pressure (Strong DOWN)", "#F6465D"
        is_buy = False
    else:
        signal_badge, signal_bg = "SELL 📉", "#E55656"
        trend_text, trend_color = "Downtrend Structure (DOWN)", "#E55656"
        is_buy = False

    # Targets Calculation
    tp1_ratio = st.session_state["tp1_pct"] / 100.0
    tp2_ratio = st.session_state["tp2_pct"] / 100.0
    sl_ratio = st.session_state["sl_pct"] / 100.0

    if current_price > 0:
        if is_buy:
            tp1, tp2, sl = current_price * (1 + tp1_ratio), current_price * (1 + tp2_ratio), current_price * (1 - sl_ratio)
            tp_l1, tp_l2, sl_l = f"TP 1 (+{st.session_state['tp1_pct']}%)", f"TP 2 (+{st.session_state['tp2_pct']}%)", f"SL (-{st.session_state['sl_pct']}%)"
        else:
            tp1, tp2, sl = current_price * (1 - tp1_ratio), current_price * (1 - tp2_ratio), current_price * (1 + sl_ratio)
            tp_l1, tp_l2, sl_l = f"TP 1 (-{st.session_state['tp1_pct']}%)", f"TP 2 (-{st.session_state['tp2_pct']}%)", f"SL (+{st.session_state['sl_pct']}%)"
    else:
        tp1 = tp2 = sl = 0.0
        tp_l1 = tp_l2 = sl_l = "-"

    # Professional Signal Card Container
    signal_card_html = f"""
<div style="background: #181A20; padding: 22px; border-radius: 14px; border: 1px solid #2B313A; color: white;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<span style="color: #848E9C; font-size: 12px; font-weight: 600;">BINANCE SPOT</span>
<h2 style="margin: 2px 0 0 0; color: #F0B90B; font-size: 30px; font-weight: 800;">{selected_pair}</h2>
<p style="margin: 4px 0 0 0; color: {trend_color}; font-weight: 600; font-size: 13px;">● {trend_text}</p>
</div>
<div>
<div style="background: {signal_bg}; color: white; padding: 12px 22px; border-radius: 10px; font-weight: 800; font-size: 18px; text-align: center; letter-spacing: 0.5px;">
{signal_badge}
</div>
</div>
</div>
<hr style="border: 0.5px solid #2B313A; margin: 18px 0;">
<div style="display: flex; justify-content: space-between; text-align: center;">
<div>
<span style="color: #848E9C; font-size: 11px;">LIVE PRICE</span>
<h3 style="margin: 4px 0 0 0; font-size: 18px; font-weight: 700;">${current_price:,.4f}</h3>
</div>
<div>
<span style="color: #848E9C; font-size: 11px;">24H CHANGE</span>
<h3 style="margin: 4px 0 0 0; color: {trend_color}; font-size: 18px; font-weight: 700;">{price_change_pct:+.2f}%</h3>
</div>
<div>
<span style="color: #848E9C; font-size: 11px;">24H HIGH</span>
<h3 style="margin: 4px 0 0 0; font-size: 18px; font-weight: 700;">${high_price:,.4f}</h3>
</div>
<div>
<span style="color: #848E9C; font-size: 11px;">24H LOW</span>
<h3 style="margin: 4px 0 0 0; font-size: 18px; font-weight: 700;">${low_price:,.4f}</h3>
</div>
</div>
<hr style="border: 0.5px solid #2B313A; margin: 18px 0;">
<div style="display: flex; justify-content: space-between; gap: 10px;">
<div style="background: rgba(14, 203, 129, 0.12); border: 1px solid #0ECB81; padding: 12px; border-radius: 10px; flex: 1; text-align: center;">
<span style="color: #0ECB81; font-size: 11px; font-weight: 700;">🎯 {tp_l1}</span>
<h4 style="margin: 4px 0 0 0; color: #FFFFFF; font-size: 16px; font-weight: 700;">${tp1:,.4f}</h4>
</div>
<div style="background: rgba(14, 203, 129, 0.12); border: 1px solid #0ECB81; padding: 12px; border-radius: 10px; flex: 1; text-align: center;">
<span style="color: #0ECB81; font-size: 11px; font-weight: 700;">🎯 {tp_l2}</span>
<h4 style="margin: 4px 0 0 0; color: #FFFFFF; font-size: 16px; font-weight: 700;">${tp2:,.4f}</h4>
</div>
<div style="background: rgba(246, 70, 93, 0.12); border: 1px solid #F6465D; padding: 12px; border-radius: 10px; flex: 1; text-align: center;">
<span style="color: #F6465D; font-size: 11px; font-weight: 700;">🛡️ {sl_l}</span>
<h4 style="margin: 4px 0 0 0; color: #FFFFFF; font-size: 16px; font-weight: 700;">${sl:,.4f}</h4>
</div>
</div>
</div>
"""
    st.markdown(signal_card_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # TradingView Pro Technical Analysis Meter Widget
    st.markdown("### 📊 Live Technical Analysis Meter")
    ta_widget_code = f"""
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
  {{
  "interval": "{st.session_state['timeframe']}m" if "{st.session_state['timeframe']}".isdigit() else "1D",
  "width": "100%",
  "isTransparent": false,
  "height": 430,
  "symbol": "BINANCE:{tv_symbol}",
  "showIntervalTabs": true,
  "locale": "en",
  "colorTheme": "dark"
}}
  </script>
</div>
"""
    components.html(ta_widget_code, height=440)

    # TradingView Chart Widget
    st.markdown("### 📈 Live Interactive Chart")
    selected_tf = st.session_state["timeframe"]
    chart_code = f"""
<div class="tradingview-widget-container" style="height:100%;width:100%">
<div id="tradingview_chart" style="height:480px;width:100%"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
"autosize": true,
"symbol": "BINANCE:{tv_symbol}",
"interval": "{selected_tf}",
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
    components.html(chart_code, height=500)

with tab2:
    st.subheader("⚙️ Signal Configuration Controls")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.session_state["tp1_pct"] = st.number_input("TP 1 (%)", 0.5, 20.0, st.session_state["tp1_pct"], 0.5)
    with col_s2:
        st.session_state["tp2_pct"] = st.number_input("TP 2 (%)", 1.0, 30.0, st.session_state["tp2_pct"], 0.5)
    with col_s3:
        st.session_state["sl_pct"] = st.number_input("Stop Loss (%)", 0.5, 15.0, st.session_state["sl_pct"], 0.5)

    st.markdown("---")
    tf_options = {"1 Min": "1", "5 Min": "5", "15 Min": "15", "1 Hour": "60", "4 Hour": "240", "1 Day": "D"}
    current_tf_label = [k for k, v in tf_options.items() if v == st.session_state["timeframe"]][0]
    selected_tf_label = st.selectbox("Default Timeframe:", list(tf_options.keys()), index=list(tf_options.keys()).index(current_tf_label))
    st.session_state["timeframe"] = tf_options[selected_tf_label]
