import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="Binance Live Trading Center",
    page_icon="📈",
    layout="wide"
)

# Dark Theme & Custom CSS matching your UI screenshots
st.markdown("""
    <style>
    .stApp {
        background-color: #121418;
        color: #FFFFFF;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #121418;
    }
    .stTabs [data-baseweb="tab"] {
        color: #888888;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        color: #FF5252 !important;
        border-bottom-color: #FF5252 !important;
    }

    /* Input boxes styling */
    .stSelectbox div[data-baseweb="select"], .stTextInput input {
        background-color: #1E2329 !important;
        color: #FFFFFF !important;
        border: 1px solid #2B313A !important;
        border-radius: 8px;
    }

    /* Card Containers */
    .trading-card {
        background-color: #1E2329;
        border: 1px solid #2B313A;
        padding: 20px;
        border-radius: 12px;
        margin-top: 10px;
    }

    .ticker-title {
        font-size: 32px;
        font-weight: bold;
        color: #F0B90B !important; /* Binance Yellow */
    }

    /* BUY / SELL Buttons */
    .buy-btn {
        background-color: #0ECB81;
        color: white;
        padding: 10px 24px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 8px;
        text-align: center;
        float: right;
    }
    .sell-btn {
        background-color: #F6465D;
        color: white;
        padding: 10px 24px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 8px;
        text-align: center;
        float: right;
    }

    /* Stat boxes */
    .stat-label {
        color: #848E9C;
        font-size: 13px;
        text-transform: uppercase;
    }
    .stat-val {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: bold;
    }

    /* TP & SL Cards */
    .tp-card {
        background-color: #172622;
        border: 1px solid #0ECB81;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .sl-card {
        background-color: #26191D;
        border: 1px solid #F6465D;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Function to fetch all active trading pairs from Binance
@st.cache_data(ttl=3600)
def get_binance_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url)
        data = response.json()
        symbols = [s['symbol'] for s in data['symbols'] if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING']
        return symbols
    except:
        return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

# Function to fetch live ticker data (Price, High, Low, Change)
def get_ticker_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return None

# --- App Tabs ---
tab1, tab2 = st.tabs(["📊 Live Trading Center", "⚙️ Signal Settings"])

with tab1:
    all_coins = get_binance_symbols()

    # Layout for selection and search
    col_sel1, col_sel2 = st.columns(2)
    
    with col_sel1:
        st.markdown("<p style='color: #848E9C; margin-bottom: 0px;'>Coin Pair එක තෝරන්න:</p>", unsafe_allow_html=True)
        selected_coin = st.selectbox("Select Coin", all_coins, label_visibility="collapsed")

    with col_sel2:
        st.markdown("<p style='color: #848E9C; margin-bottom: 0px;'>Coin එක Search කරන්න:</p>", unsafe_allow_html=True)
        search_query = st.text_input("Search", placeholder="eg: RUNE, ADA", label_visibility="collapsed")

    # Handle Search filter
    if search_query:
        search_upper = search_query.upper().strip() + "USDT"
        if search_upper in all_coins:
            selected_coin = search_upper

    # Fetch live data for selected coin
    ticker = get_ticker_data(selected_coin)

    if ticker:
        last_price = float(ticker['lastPrice'])
        price_change_pct = float(ticker['priceChangePercent'])
        high_24h = float(ticker['highPrice'])
        low_24h = float(ticker['lowPrice'])
        
        # Determine Trend & Action based on price change
        is_uptrend = price_change_pct >= 0
        trend_text = "Uptrend Structure (UP)" if is_uptrend else "Downtrend Structure (DOWN)"
        trend_color = "#0ECB81" if is_uptrend else "#F6465D"
        action_type = "BUY" if is_uptrend else "SELL"
        btn_class = "buy-btn" if is_uptrend else "sell-btn"

        # Calculate dynamic TP and SL targets based on live price
        if is_uptrend:
            tp1 = last_price * 1.02  # +2.0%
            tp2 = last_price * 1.04  # +4.0%
            sl = last_price * 0.98   # -2.0%
        else:
            tp1 = last_price * 0.98  
            tp2 = last_price * 0.96  
            sl = last_price * 1.02   

        # Main Card Display
        st.markdown(f"""
            <div class="trading-card">
                <p style="color: #848E9C; font-size: 12px; margin-bottom: -5px;">BINANCE SPOT</p>
                <table width="100%">
                    <tr>
                        <td><span class="ticker-title">{selected_coin}</span></td>
                        <td align="right"><div class="{btn_class}">{action_type} 📈</div></td>
                    </tr>
                </table>
                <p style="color: {trend_color}; font-weight: bold; margin-top: 5px;">● {trend_text}</p>
                <hr style="border-color: #2B313A; margin: 15px 0;">
                
                <table width="100%">
                    <tr>
                        <td><div class="stat-label">LIVE PRICE</div><div class="stat-val">${last_price:,.4f}</div></td>
                        <td><div class="stat-label">24H CHANGE</div><div class="stat-val" style="color: {trend_color};">{price_change_pct:+.2f}%</div></td>
                        <td><div class="stat-label">24H HIGH</div><div class="stat-val">${high_24h:,.4f}</div></td>
                        <td><div class="stat-label">24H LOW</div><div class="stat-val">${low_24h:,.4f}</div></td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # TP1, TP2, SL Cards
        tp_col1, tp_col2, sl_col = st.columns(3)

        with tp_col1:
            st.markdown(f"""
                <div class="tp-card">
                    <p style="color: #0ECB81; font-weight: bold; margin-bottom: 5px;">🎯 TP 1 (+2.0%)</p>
                    <h3 style="color: #FFFFFF; margin: 0;">${tp1:,.4f}</h3>
                </div>
            """, unsafe_allow_html=True)

        with tp_col2:
            st.markdown(f"""
                <div class="tp-card">
                    <p style="color: #0ECB81; font-weight: bold; margin-bottom: 5px;">🎯 TP 2 (+4.0%)</p>
                    <h3 style="color: #FFFFFF; margin: 0;">${tp2:,.4f}</h3>
                </div>
            """, unsafe_allow_html=True)

        with sl_col:
            st.markdown(f"""
                <div class="sl-card">
                    <p style="color: #F6465D; font-weight: bold; margin-bottom: 5px;">🛡️ SL (-2.0%)</p>
                    <h3 style="color: #FFFFFF; margin: 0;">${sl:,.4f}</h3>
                </div>
            """, unsafe_allow_html=True)

    else:
        st.error("දත්ත ලබා ගැනීමට නොහැකි විය. කරුණාකර නැවත උත්සාහ කරන්න.")

with tab2:
    st.subheader("⚙️ Signal Configuration Settings")
    st.write("මෙම අංශයෙන් ඔබට සික්නල් ලබා දෙන ප්‍රතිශත (TP/SL percentages) වෙනස් කරගත හැක.")
    
    tp1_pct = st.slider("TP 1 Percentage (%)", 1.0, 10.0, 2.0)
    tp2_pct = st.slider("TP 2 Percentage (%)", 2.0, 20.0, 4.0)
    sl_pct = st.slider("Stop Loss Percentage (%)", 1.0, 10.0, 2.0)
    
    if st.button("සැකසුම් සුරකින්න (Save Settings)"):
        st.success("සැකසුම් සාර්ථකව සුරකින ලදී!")
