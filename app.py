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
# MAIN APP HEADER BANNER
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
        "LINK/USDT", "DOT/USDT", "NEAR/USDT", "SUI/USDT", "SHIB/USDT",
        "MATIC/USDT", "UNI/USDT", "ICP/USDT", "RUNE/USDT", "RENDER/USDT",
        "FET/USDT", "INJ/USDT", "AR/USDT", "TIA/USDT", "SEI/USDT",
        "PENDLE/USDT", "OP/USDT", "ARB/USDT", "STRK/USDT", "MANTA/USDT",
        "ALT/USDT", "JUP/USDT", "PYTH/USDT", "WLD/USDT", "TIA/USDT",
        "ATOM/USDT", "NEAR/USDT", "FTM/USDT", "ALGO/USDT", "VET/USDT",
        "FIL/USDT", "GRT/USDT", "SAND/USDT", "MANA/USDT", "AXS/USDT",
        "THETA/USDT", "EGLD/USDT", "FLOW/USDT", "CHZ/USDT", "CRV/USDT",
        "LDO/USDT", "SNX/USDT", "MKR/USDT", "AAVE/USDT", "COMP/USDT",
        "FXS/USDT", "GMX/USDT", "DYDX/USDT", "GNS/USDT", "JOE/USDT",
        "CAKE/USDT", "SUSHI/USDT", "1INCH/USDT", "ZRX/USDT", "BAL/USDT",
        "RSR/USDT", "OCEAN/USDT", "AGIX/USDT", "RLC/USDT", "NMR/USDT",
        "TRB/USDT", "API3/USDT", "TRU/USDT", "ID/USDT", "GAL/USDT",
        "HOOK/USDT", "HIGH/USDT", "PERP/USDT", "LINA/USDT", "STG/USDT",
        "RDNT/USDT", "STMX/USDT", "KEY/USDT", "DOCK/USDT", "PHB/USDT",
        "OXT/USDT", "SKL/USDT", "CTSI/USDT", "COTI/USDT", "CHR/USDT",
        "TLM/USDT", "BAKE/USDT", "BURGER/USDT", "DODO/USDT", "UNFI/USDT",
        "BEL/USDT", "WING/USDT", "LIT/USDT", "SFP/USDT", "HARD/USDT",
        "REEF/USDT", "OM/USDT", "BAKE/USDT", "ALPHA/USDT", "BETA/USDT",
        "CREAM/USDT", "QUICK/USDT", "SUPER/USDT", "MDT/USDT", "PNT/USDT",
        "PROM/USDT", "ORN/USDT", "MBOX/USDT", "GHST/USDT", "PERL/USDT",
        "LRC/USDT", "ENJ/USDT", "STORJ/USDT", "ANKR/USDT", "KNC/USDT",
        "BAT/USDT", "ZEN/USDT", "IOST/USDT", "ONT/USDT", "ZIL/USDT",
        "ICX/USDT", "ONT/USDT", "QTUM/USDT", "NKN/USDT", "WAVES/USDT",
        "OMG/USDT", "DGB/USDT", "RVN/USDT", "SC/USDT", "STMX/USDT",
        "HBAR/USDT", "ONE/USDT", "HOT/USDT", "ZIL/USDT", "IOST/USDT",
        "KAVA/USDT", "KSM/USDT", "ARPA/USDT", "CTK/USDT", "SUN/USDT",
        "JST/USDT", "WIN/USDT", "BTT/USDT", "POLS/USDT", "MASK/USDT",
        "C98/USDT", "QNT/USDT", "MINA/USDT", "RAY/USDT", "FIDA/USDT",
        "MAPS/USDT", "BICO/USDT", "GLMR/USDT", "MOVR/USDT", "ACA/USDT",
        "ASTR/USDT", "ENS/USDT", "IMX/USDT", "PEOPLE/USDT", "GALA/USDT",
        "POWR/USDT", "VGX/USDT", "BIFI/USDT", "TKO/USDT", "ATA/USDT",
        "C98/USDT", "LPT/USDT", "AUDIO/USDT", "FOR/USDT", "AKRO/USDT",
        "DIABO/USDT", "DEXE/USDT", "AUCTION/USDT", "FORTH/USDT", "POLYX/USDT",
        "BOME/USDT", "WIF/USDT", "BONK/USDT", "FLOKI/USDT", "MEME/USDT",
        "ORDI/USDT", "SATS/USDT", "RATS/USDT", "BNX/USDT", "POL/USDT"
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

    # Compact Vertical Boxes (පොඩියට සාදා ඇත)
    signal_card_html = f"""
<div style="background: #181A20; padding: 18px; border-radius: 14px; border: 1px solid #2B313A; color: white;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<span style="color: #848E9C; font-size: 11px; font-weight: 600;">BINANCE SPOT</span>
<h2 style="margin: 2px 0 0 0; color: #F0B90B; font-size: 26px; font-weight: 800;">{selected_pair}</h2>
<p style="margin: 2px 0 0 0; color: {trend_color}; font-weight: 600; font-size: 12px;">● {trend_text}</p>
</div>
<div>
<div style="background: {signal_bg}; color: white; padding: 10px 18px; border-radius: 8px; font-weight: 800; font-size: 16px; text-align: center;">
{signal_badge}
</div>
</div>
</div>

<div style="text-align: center; margin: 12px 0;">
<span style="color: #848E9C; font-size: 11px; font-weight: 600;">Price: ${current_price:,.4f} | Change: {price_change_pct:+.2f}% | Zone: Premium Zone</span>
</div>

<!-- Compact Vertical Boxes -->
<div style="background: #1E2329; padding: 6px 10px; border-radius: 6px; text-align: center; margin-bottom: 6px;">
<span style="color: #848E9C; font-size: 10px; font-weight: 600; display: block;">Entry</span>
<h4 style="margin: 1px 0 0 0; color: #FFFFFF; font-size: 14px; font-weight: 700;">${current_price:,.4f}</h4>
</div>

<div style="background: #1E2329; padding: 6px 10px; border-radius: 6px; text-align: center; margin-bottom: 6px;">
<span style="color: #0ECB81; font-size: 10px; font-weight: 600; display: block;">TP 1</span>
<h4 style="margin: 1px 0 0 0; color: #0ECB81; font-size: 14px; font-weight: 700;">${tp1:,.4f}</h4>
</div>

<div style="background: #1E2329; padding: 6px 10px; border-radius: 6px; text-align: center; margin-bottom: 6px;">
<span style="color: #0ECB81; font-size: 10px; font-weight: 600; display: block;">TP 2</span>
<h4 style="margin: 1px 0 0 0; color: #0ECB81; font-size: 14px; font-weight: 700;">${tp2:,.4f}</h4>
</div>

<div style="background: #1E2329; padding: 6px 10px; border-radius: 6px; text-align: center;">
<span style="color: #F6465D; font-size: 10px; font-weight: 600; display: block;">SL</span>
<h4 style="margin: 1px 0 0 0; color: #F6465D; font-size: 14px; font-weight: 700;">${sl:,.4f}</h4>
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
  "interval": "{st.session_state['timeframe']}" if "{st.session_state['timeframe']}".isdigit() else "1D",
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
