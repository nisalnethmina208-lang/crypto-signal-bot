import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Binance Pro Signal & Forecast Center", 
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

# Fetch All Active USDT Pairs from Binance API (210+ Coins)
@st.cache_data(ttl=3600)
def get_binance_usdt_pairs():
    try:
        url = "https://api1.binance.com/api/v3/exchangeInfo"
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

# Fetch Historical Candles for Advanced Indicator Calculation
def fetch_binance_klines(symbol, interval="15", limit=100):
    urls = [
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}m&limit={limit}",
        f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval={interval}m&limit={limit}",
        f"https://api3.binance.com/api/v3/klines?symbol={symbol}&interval={interval}m&limit={limit}"
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=4)
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
            continue
    return None

# Fetch Real Live Market Data
def fetch_live_market_data(symbol):
    urls = [
        f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}",
        f"https://api1.binance.com/api/v3/ticker/24hr?symbol={symbol}",
        f"https://api3.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                return float(data["lastPrice"]), float(data["priceChangePercent"]), float(data["highPrice"]), float(data["lowPrice"])
        except Exception:
            continue
    return 0.0, 0.0, 0.0, 0.0

# UI Header Banner
st.markdown("""
<div style="background: linear-gradient(135deg, #1E2329 0%, #0B0E11 100%); padding: 20px; border-radius: 16px; border: 1px solid #F0B90B; margin-bottom: 20px; text-align: center; box-shadow: 0px 4px 15px rgba(240, 185, 11, 0.15);">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
        <span style="font-size: 32px;">⚡</span>
        <h1 style="color: #F0B90B; margin: 0; font-size: 24px; font-weight: 800;">BINANCE PRO SIGNAL & FORECAST CENTER</h1>
    </div>
    <p style="color: #848E9C; margin: 6px 0 0 0; font-size: 13px;">210+ Live Crypto Pairs & Predictive Technical Indicators (RSI, EMA, MACD)</p>
</div>
""", unsafe_allow_html=True)

# Tabs Interface
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

    # Fetch Real-time Market Data & Candles
    current_price, price_change_pct, high_price, low_price = fetch_live_market_data(tv_symbol)
    df_candles = fetch_binance_klines(tv_symbol, interval=st.session_state['timeframe'], limit=100)

    # Advanced Indicator Calculations (RSI, EMA 9/21, MACD & Bollinger Bands)
    last_rsi = 50.0
    ema_9 = current_price
    ema_21 = current_price
    macd_val = 0.0
    macd_signal = 0.0
    bb_upper = current_price * 1.02
    bb_lower = current_price * 0.98

    if df_candles is not None and len(df_candles) > 35:
        try:
            # RSI Calculation
            delta = df_candles['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df_candles['RSI'] = 100 - (100 / (1 + rs))
            
            # EMA Calculations
            df_candles['EMA_9'] = df_candles['close'].ewm(span=9, adjust=False).mean()
            df_candles['EMA_21'] = df_candles['close'].ewm(span=21, adjust=False).mean()
            
            # MACD Calculation for Trend Prediction
            exp1 = df_candles['close'].ewm(span=12, adjust=False).mean()
            exp2 = df_candles['close'].ewm(span=26, adjust=False).mean()
            df_candles['MACD'] = exp1 - exp2
            df_candles['MACD_Signal'] = df_candles['MACD'].ewm(span=9, adjust=False).mean()

            # Bollinger Bands Calculation
            df_candles['BB_Mid'] = df_candles['close'].rolling(window=20).mean()
            bb_std = df_candles['close'].rolling(window=20).std()
            df_candles['BB_Upper'] = df_candles['BB_Mid'] + (bb_std * 2)
            df_candles['BB_Lower'] = df_candles['BB_Mid'] - (bb_std * 2)

            last_rsi = float(df_candles['RSI'].iloc[-1])
            ema_9 = float(df_candles['EMA_9'].iloc[-1])
            ema_21 = float(df_candles['EMA_21'].iloc[-1])
            macd_val = float(df_candles['MACD'].iloc[-1])
            macd_signal = float(df_candles['MACD_Signal'].iloc[-1])
            bb_upper = float(df_candles['BB_Upper'].iloc[-1])
            bb_lower = float(df_candles['BB_Lower'].iloc[-1])
        except Exception:
            pass

    # Fallback if live price is 0
    if current_price == 0.0 and df_candles is not None:
        current_price = float(df_candles['close'].iloc[-1])
        high_price = float(df_candles['high'].max())
        low_price = float(df_candles['low'].min())

    # Predictive Market Movement Logic based on Multi-Indicators
    forecast_text = "Market is consolidating. Wait for breakout."
    forecast_color = "#F0B90B"
    
    if ema_9 > ema_21 and macd_val > macd_signal and last_rsi < 68:
        signal_badge, signal_bg = "STRONG BUY 🚀", "#0ECB81"
        trend_text = "Bullish Trend Continuation Expected"
        trend_color = "#0ECB81"
        forecast_text = "ඉහළට යාමේ ප්‍රබල ප්‍රවණතාවක් පවතී (Bullish Momentum). මිල වැඩිදුරටත් ඉහළ යාමට ඉඩ ඇත."
        is_buy = True
    elif ema_9 < ema_21 and macd_val < macd_signal and last_rsi > 32:
        signal_badge, signal_bg = "STRONG SELL 🔻", "#F6465D"
        trend_text = "Bearish Trend Continuation Expected"
        trend_color = "#F6465D"
        forecast_text = "පහළට වැටීමේ ප්‍රබල පීඩනයක් ඇත (Bearish Pressure). තවදුරටත් මිල අඩුවිය හැක."
        is_buy = False
    elif last_rsi < 30:
        signal_badge, signal_bg = "REVERSAL BUY 📈", "#0ECB81"
        trend_text = "Oversold Zone - Potential Upward Reversal"
        trend_color = "#0ECB81"
        forecast_text = "කොයින් එක Oversold (අධික ලෙස විකුණා ඇති) මට්ටමක ඇත. ළඟදීම ඉහළට හැරීමේ (Reversal) වැඩි ඉඩක් ඇත."
        is_buy = True
    elif last_rsi > 70:
        signal_badge, signal_bg = "REVERSAL SELL 📉", "#F6465D"
        trend_text = "Overbought Zone - Potential Downward Reversal"
        trend_color = "#F6465D"
        forecast_text = "කොයින් එක Overbought (අධික ලෙස මිලදී ගත්) මට්ටමක ඇත. ළඟදීම පහළට correction එකක් ඒමට ඉඩ ඇත."
        is_buy = False
    else:
        if ema_9 >= ema_21:
            signal_badge, signal_bg = "BUY 📈", "#26A69A"
            trend_text = "Short-term Bullish Wave"
            trend_color = "#26A69A"
            forecast_text = "කෙටිකාලීන මිල ඉහළ නැගීමක් පෙන්නුම් කරයි."
            is_buy = True
        else:
            signal_badge, signal_bg = "SELL 📉", "#E55656"
            trend_text = "Short-term Bearish Wave"
            trend_color = "#E55656"
            forecast_text = "කෙටිකාලීන මිල පහළ යාමේ අවදානමක් ඇත."
            is_buy = False

    # Targets Calculation
    tp1_ratio = st.session_state["tp1_pct"] / 100.0
    tp2_ratio = st.session_state["tp2_pct"] / 100.0
    sl_ratio = st.session_state["sl_pct"] / 100.0

    if is_buy:
        tp1 = current_price * (1 + tp1_ratio)
        tp2 = current_price * (1 + tp2_ratio)
        sl = current_price * (1 - sl_ratio)
        tp_l1, tp_l2, sl_l = f"TP 1 (+{st.session_state['tp1_pct']}%)", f"TP 2 (+{st.session_state['tp2_pct']}%)", f"SL (-{st.session_state['sl_pct']}%)"
    else:
        tp1 = current_price * (1 - tp1_ratio)
        tp2 = current_price * (1 - tp2_ratio)
        sl = current_price * (1 + sl_ratio)
        tp_l1, tp_l2, sl_l = f"TP 1 (-{st.session_state['tp1_pct']}%)", f"TP 2 (-{st.session_state['tp2_pct']}%)", f"SL (+{st.session_state['sl_pct']}%)"

    # Signal Card UI with Forecast Insight
    signal_card_html = f"""
<div style="background: #181A20; padding: 22px; border-radius: 14px; border: 1px solid #2B313A; color: white;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="color: #848E9C; font-size: 12px; font-weight: 600;">BINANCE SPOT + 210+ PAIRS</span>
            <h2 style="margin: 2px 0 0 0; color: #F0B90B; font-size: 28px; font-weight: 800;">{selected_pair}</h2>
            <p style="margin: 4px 0 0 0; color: {trend_color}; font-weight: 600; font-size: 13px;">● {trend_text}</p>
        </div>
        <div style="background: {signal_bg}; color: white; padding: 12px 20px; border-radius: 10px; font-weight: 800; font-size: 16px; text-align: center;">
            {signal_badge}
        </div>
    </div>
    <hr style="border: 0.5px solid #2B313A; margin: 18px 0;">
    <div style="background: rgba(240, 185, 11, 0.08); border-left: 4px solid #F0B90B; padding: 10px 14px; border-radius: 4px; margin-bottom: 18px;">
        <span style="color: #F0B90B; font-size: 12px; font-weight: 700;">🔮 AI Indicator Market Forecast:</span>
        <p style="margin: 4px 0 0 0; color: #EAECEE; font-size: 13px;">{forecast_text}</p>
    </div>
    <div style="display: flex; justify-content: space-between; text-align: center;">
        <div>
            <span style="color: #848E9C; font-size: 11px;">LIVE PRICE</span>
            <h3 style="margin: 4px 0 0 0; font-size: 16px; font-weight: 700;">${current_price:,.4f}</h3>
        </div>
        <div>
            <span style="color: #848E9C; font-size: 11px;">RSI (14)</span>
            <h3 style="margin: 4px 0 0 0; font-size: 16px; font-weight: 700;">{last_rsi:.1f}</h3>
        </div>
        <div>
            <span style="color: #848E9C; font-size: 11px;">BB UPPER</span>
            <h3 style="margin: 4px 0 0 0; font-size: 16px; font-weight: 700;">${bb_upper:,.4f}</h3>
        </div>
        <div>
            <span style="color: #848E9C; font-size: 11px;">BB LOWER</span>
            <h3 style="margin: 4px 0 0 0; font-size: 16px; font-weight: 700;">${bb_lower:,.4f}</h3>
        </div>
    </div>
    <hr style="border: 0.5px solid #2B313A; margin: 18px 0;">
    <div style="display: flex; justify-content: space-between; gap: 10px;">
        <div style="background: rgba(14, 203, 129, 0.12); border: 1px solid #0ECB81; padding: 10px; border-radius: 10px; flex: 1; text-align: center;">
            <span style="color: #0ECB81; font-size: 11px; font-weight: 700;">🎯 {tp_l1}</span>
            <h4 style="margin: 4px 0 0 0; color: #FFFFFF; font-size: 15px; font-weight: 700;">${tp1:,.4f}</h4>
        </div>
        <div style="background: rgba(14, 203, 129, 0.12); border: 1px solid #0ECB81; padding: 10px; border-radius: 10px; flex: 1; text-align: center;">
            <span style="color: #0ECB81; font-size: 11px; font-weight: 700;">🎯 {tp_l2}</span>
            <h4 style="margin: 4px 0 0 0; color: #FFFFFF; font-size: 15px; font-weight: 700;">${tp2:,.4f}</h4>
        </div>
        <div style="background: rgba(246, 70, 93, 0.12); border: 1px solid #F6465D; padding: 10px; border-radius: 10px; flex: 1; text-align: center;">
            <span style="color: #F6465D; font-size: 11px; font-weight: 700;">🛡️ {sl_l}</span>
            <h4 style="margin: 4px 0 0 0; color: #FFFFFF; font-size: 15px; font-weight: 700;">${sl:,.4f}</h4>
        </div>
    </div>
</div>
"""
    st.markdown(signal_card_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # TradingView Technical Analysis Meter Widget
    st.markdown("### 📊 Live Technical Analysis Meter")
    tv_tf_map = {"1": "1m", "5": "5m", "15": "15m", "60": "1h", "240": "4h", "D": "1D"}
    widget_interval = tv_tf_map.get(st.session_state['timeframe'], "15m")
    
    ta_widget_code = f"""
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
  {{
  "interval": "{widget_interval}",
  "width": "100%",
  "isTransparent": false,
  "height": 420,
  "symbol": "BINANCE:{tv_symbol}",
  "showIntervalTabs": true,
  "locale": "en",
  "colorTheme": "dark"
}}
  </script>
</div>
"""
    components.html(ta_widget_code, height=430)

    # TradingView Interactive Chart Widget
    st.markdown("### 📈 Live Interactive Chart")
    chart_code = f"""
<div class="tradingview-widget-container" style="height:100%;width:100%">
<div id="tradingview_chart" style="height:480px;width:100%"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
"autosize": true,
"symbol": "BINANCE:{tv_symbol}",
"interval": "{st.session_state['timeframe']}",
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
    
    if st.session_state["timeframe"] not in tf_options.values():
        st.session_state["timeframe"] = "15"
        
    current_tf_label = [k for k, v in tf_options.items() if v == st.session_state["timeframe"]][0]
    selected_tf_label = st.selectbox("Default Timeframe:", list(tf_options.keys()), index=list(tf_options.keys()).index(current_tf_label))
    st.session_state["timeframe"] = tf_options[selected_tf_label]
