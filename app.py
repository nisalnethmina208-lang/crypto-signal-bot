import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Binance Pro Signal Center", 
    page_icon="⚡", 
    layout="centered"
)

# Initialize Session State safely
if "tp1_pct" not in st.session_state:
    st.session_state["tp1_pct"] = 2.0
if "tp2_pct" not in st.session_state:
    st.session_state["tp2_pct"] = 4.0
if "sl_pct" not in st.session_state:
    st.session_state["sl_pct"] = 2.0
if "timeframe" not in st.session_state:
    st.session_state["timeframe"] = "15"

# Fetch All Active USDT Pairs from Binance API (210+ Coins)
@st.cache_data(ttl=3600)
def get_binance_usdt_pairs():
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            symbols = [
                s['symbol'].replace('USDT', '/USDT') 
                for s in data['symbols'] 
                if s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING'
            ]
            if symbols:
                return sorted(symbols)
    except Exception:
        pass
    return [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
        "APT/USDT", "ADA/USDT", "DOGE/USDT", "PEPE/USDT", "AVAX/USDT",
        "LINK/USDT", "DOT/USDT", "NEAR/USDT", "SUI/USDT", "SHIB/USDT"
    ]

# Fetch Historical Candles safely
def fetch_binance_klines(symbol, interval="15m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                ])
                df['close'] = df['close'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['open'] = df['open'].astype(float)
                return df
    except Exception:
        pass
    return None

# Multi-API Live Data Fetcher safely
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

    return 100.0, 1.0, 105.0, 95.0

# ---------------------------------------------------------
# MAIN APP HEADER BANNER
# ---------------------------------------------------------
st.markdown("""
<div style="background: linear-gradient(135deg, #1E2329 0%, #0B0E11 100%); padding: 20px; border-radius: 16px; border: 1px solid #F0B90B; margin-bottom: 20px; text-align: center; box-shadow: 0px 4px 15px rgba(240, 185, 11, 0.15);">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
        <span style="font-size: 32px;">⚡</span>
        <h1 style="color: #F0B90B; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;">BINANCE PRO SIGNAL CENTER</h1>
    </div>
    <p style="color: #848E9C; margin: 6px 0 0 0; font-size: 13px; font-weight: 500;">210+ Crypto Pairs Live Analysis</p>
    <div style="margin-top: 10px;">
        <span style="background-color: rgba(14, 203, 129, 0.2); color: #0ECB81; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; border: 1px solid #0ECB81;">● STABLE ENGINE ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Interface Tabs
tab1, tab2 = st.tabs(["📊 Live Trading Center", "⚙️ Signal Settings"])

with tab1:
    all_coins = get_binance_usdt_pairs()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_pair = st.selectbox("Coin Pair එක තෝරන්න (210+ Available):", all_coins)
    with col2:
        custom_input = st.text_input("Coin එක Search කරන්න:", placeholder="eg: RUNE")
        
    if custom_input and custom_input.strip():
        custom_symbol = custom_input.upper().strip().replace("USDT", "") + "/USDT"
        if custom_symbol in all_coins:
            selected_pair = custom_symbol

    tv_symbol = selected_pair.replace("/", "")

    # Fetch Real-time Market Data & Candles safely
    current_price, price_change_pct, high_price, low_price = fetch_live_market_data(tv_symbol)
    df_candles = fetch_binance_klines(tv_symbol, interval=st.session_state['timeframe'] if st.session_state['timeframe'] in ["1", "5", "15", "60", "240", "D"] else "15")

    # Indicator Calculations safely
    last_rsi = 50.0
    ema_9 = current_price
    ema_21 = current_price

    if df_candles is not None and len(df_candles) > 30:
        try:
            delta = df_candles['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df_candles['RSI'] = 100 - (100 / (1 + rs))
            
            df_candles['EMA_9'] = df_candles['close'].ewm(span=9, adjust=False).mean()
            df_candles['EMA_21'] = df_candles['close'].ewm(span=21, adjust=False).mean()
            
            if not pd.isna(df_candles['RSI'].iloc[-1]):
                last_rsi = float(df_candles['RSI'].iloc[-1])
            ema_9 = float(df_candles['EMA_9'].iloc[-1])
            ema_21 = float(df_candles['EMA_21'].iloc[-1])
        except Exception:
            pass

    # Indicator Based Rules
    if ema_9 > ema_21 and last_rsi < 70:
        signal_badge, signal_bg = "STRONG BUY 🚀", "#0ECB81"
        trend_text, trend_color = f"EMA Bullish & RSI ({last_rsi:.1f})", "#0ECB81"
        is_buy = True
    elif ema_9 < ema_21 and last_rsi > 30:
        signal_badge, signal_bg = "STRONG SELL 🔻", "#F6465D"
        trend_text, trend_color = f"EMA Bearish & RSI ({last_rsi:.1f})", "#F6465D"
        is_buy = False
    else:
        if price_change_pct >= 0:
            signal_badge, signal_bg = "BUY 📈", "#26A69A"
            trend_text, trend_color = "Neutral Momentum (UP)", "#26A69A"
            is_buy = True
        else:
            signal_badge, signal_bg = "SELL 📉", "#E55656"
            trend_text, trend_color = "Neutral Momentum (DOWN)", "#E55656"
            is_buy = False

    # Targets Calculation based on Settings
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
<span style="color: #848E9C; font-size: 12px; font-weight: 600;">BINANCE SPOT + 210+ PAIRS</span>
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
<span style="color: #848E9C; font-size: 11px;">ENTRY / LIVE</span>
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
  "interval": "{st.session_state['timeframe']}",
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
    
    # Safe validation for timeframe selection
    if st.session_state["timeframe"] not in tf_options.values():
        st.session_state["timeframe"] = "15"
        
    current_tf_label = [k for k, v in tf_options.items() if v == st.session_state["timeframe"]][0]
    selected_tf_label = st.selectbox("Default Timeframe:", list(tf_options.keys()), index=list(tf_options.keys()).index(current_tf_label))
    st.session_state["timeframe"] = tf_options[selected_tf_label]
