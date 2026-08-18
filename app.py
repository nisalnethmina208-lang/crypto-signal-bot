import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="Binance Pro Signal Terminal",
    page_icon="📈",
    layout="wide"
)

# Advanced Studio Light Theme & Signal UI CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    .main-title {
        font-size: 30px;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }
    .sub-title-desc {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 25px;
    }
    .trading-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .ticker-title {
        font-size: 36px;
        font-weight: 800;
        color: #0F172A !important;
        letter-spacing: -1px;
    }
    .binance-badge {
        background-color: #FEF3C7;
        color: #D97706;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 700;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .buy-signal-box {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 14px 20px;
        font-size: 18px;
        font-weight: 800;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    .sell-signal-box {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        padding: 14px 20px;
        font-size: 18px;
        font-weight: 800;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
    .trend-up { color: #059669 !important; font-weight: 700; }
    .trend-down { color: #DC2626 !important; font-weight: 700; }
    
    .stat-label { color: #64748B; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
    .stat-val { color: #0F172A; font-size: 18px; font-weight: 700; }

    /* Compact & Clean Target Cards */
    .target-card-buy {
        background-color: #ECFDF5;
        border: 1px solid #A7F3D0;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
    }
    .target-card-sell {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
    }
    .target-title { font-size: 11px; font-weight: 700; color: #4B5563; text-transform: uppercase; }
    .target-price { font-size: 18px; font-weight: 800; margin-top: 3px; }

    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# Function to fetch live data from CoinGecko
@st.cache_data(ttl=300)
def get_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_high=true&include_24hr_low=true"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

# --- Sidebar (Navigation & Settings) ---
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    app_page = st.selectbox("Select Page:", ["🏠 Live Signal Dashboard", "📝 Trading Notepad"])
    
    st.markdown("---")
    st.markdown("## ⚙️ Market Settings")
    
    coin_options = {
        "BTC/USDT": {"id": "bitcoin", "symbol": "BINANCE:BTCUSDT"},
        "ETH/USDT": {"id": "ethereum", "symbol": "BINANCE:ETHUSDT"},
        "BNB/USDT": {"id": "binancecoin", "symbol": "BINANCE:BNBUSDT"},
        "SOL/USDT": {"id": "solana", "symbol": "BINANCE:SOLUSDT"},
        "XRP/USDT": {"id": "ripple", "symbol": "BINANCE:XRPUSDT"},
        "ADA/USDT": {"id": "cardano", "symbol": "BINANCE:ADAUSDT"},
        "DOGE/USDT": {"id": "dogecoin", "symbol": "BINANCE:DOGEUSDT"},
        "AVAX/USDT": {"id": "avalanche-2", "symbol": "BINANCE:AVAXUSDT"},
        "TRX/USDT": {"id": "tron", "symbol": "BINANCE:TRXUSDT"},
        "DOT/USDT": {"id": "polkadot", "symbol": "BINANCE:DOTUSDT"},
        "MATIC/USDT": {"id": "polygon-ecosystem-token", "symbol": "BINANCE:MATICUSDT"},
        "LINK/USDT": {"id": "chainlink", "symbol": "BINANCE:LINKUSDT"},
        "UNI/USDT": {"id": "uniswap", "symbol": "BINANCE:UNIUSDT"},
        "NEAR/USDT": {"id": "near", "symbol": "BINANCE:NEARUSDT"},
        "APT/USDT": {"id": "aptos", "symbol": "BINANCE:APTUSDT"},
        "RENDER/USDT": {"id": "render-token", "symbol": "BINANCE:RNDRUSDT"},
        "INJ/USDT": {"id": "injective-protocol", "symbol": "BINANCE:INJUSDT"},
        "PEPE/USDT": {"id": "pepe", "symbol": "BINANCE:PEPEUSDT"},
        "SHIB/USDT": {"id": "shiba-inu", "symbol": "BINANCE:SHIBUSDT"}
    }
    
    selected_coin_display = st.selectbox("Select Market Pair:", list(coin_options.keys()), index=0)
    coin_id = coin_options[selected_coin_display]["id"]
    tv_symbol = coin_options[selected_coin_display]["symbol"]
    
    chart_interval = st.selectbox("Chart Timeframe:", ["1", "15", "60", "D"], index=1, format_func=lambda x: {"1": "1m", "15": "15m", "60": "1H", "D": "1D"}[x])
    st.markdown("---")
    st.caption("⚡ Binance & CoinGecko Powered")

# Fetch Live Stats for common use
data = get_coin_data(coin_id)
last_price = 0.0
change_24h = 0.0
high_24h = 0.0
low_24h = 0.0

if data and coin_id in data:
    price_data = data[coin_id]
    last_price = price_data.get('usd', 0.0)
    change_24h = price_data.get('usd_24h_change', 0.0)
    high_24h = price_data.get('usd_24h_high', last_price * 1.02)
    low_24h = price_data.get('usd_24h_low', last_price * 0.98)

is_uptrend = change_24h >= 0
trend_class = "trend-up" if is_uptrend else "trend-down"
signal_type = "LONG (BUY) 🚀" if is_uptrend else "SHORT (SELL) 🔻"
signal_box_class = "buy-signal-box" if is_uptrend else "sell-signal-box"
change_icon = "▲" if is_uptrend else "▼"

# Automated Target Calculations (TP1, TP2, SL)
if is_uptrend:
    entry_price = last_price
    tp1 = last_price * 1.015
    tp2 = last_price * 1.035
    sl = last_price * 0.992
    target_card_cls = "target-card-buy"
    target_color = "#059669"
else:
    entry_price = last_price
    tp1 = last_price * 0.985
    tp2 = last_price * 0.965
    sl = last_price * 1.008
    target_card_cls = "target-card-sell"
    target_color = "#DC2626"


# ================= PAGE 1: HOME / SIGNAL DASHBOARD =================
if app_page == "🏠 Live Signal Dashboard":
    st.markdown(f'<p class="main-title">📈 Pro Trading Signal Terminal</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title-desc">Real-time market analysis and calculated targets for <b>{selected_coin_display}</b>.</p>', unsafe_allow_html=True)

    # Top Ticker & Signal Status Row
    col_top1, col_top2 = st.columns([3, 1])
    with col_top1:
        st.markdown(f'<span class="binance-badge">Binance Spot Analysis</span>', unsafe_allow_html=True)
        st.markdown(f'<p class="ticker-title" style="margin-top: 8px;">{selected_coin_display}</p>', unsafe_allow_html=True)
    with col_top2:
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{signal_box_class}">{signal_type}</div>', unsafe_allow_html=True)

    # Modern Stats Overview Card
    st.markdown(f"""
        <div class="trading-card">
            <table width="100%">
                <tr>
                    <td><div class="stat-label">Live Price</div><div class="stat-val">${last_price:,.4f}</div></td>
                    <td><div class="stat-label">24h Change</div><div class="stat-val {trend_class}">{change_icon} {change_24h:,.2f}%</div></td>
                    <td><div class="stat-label">24h High</div><div class="stat-val" style="color: #059669;">${high_24h:,.4f}</div></td>
                    <td><div class="stat-label">24h Low</div><div class="stat-val" style="color: #DC2626;">${low_24h:,.4f}</div></td>
                </tr>
            </table>
        </div>
    """, unsafe_allow_html=True)

    # --- Compact & Clean Trade Targets (TP1, TP2, SL) ---
    st.markdown("### 🎯 Trade Targets & Setup")

    col_t1, col_t2, col_t3, col_t4 = st.columns(4)

    with col_t1:
        st.markdown(f"""
            <div class="{target_card_cls}">
                <div class="target-title">Entry Price</div>
                <div class="target-price" style="color: #0F172A;">${entry_price:,.4f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_t2:
        st.markdown(f"""
            <div class="{target_card_cls}">
                <div class="target-title">Take Profit 1 (TP1)</div>
                <div class="target-price" style="color: {target_color};">${tp1:,.4f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_t3:
        st.markdown(f"""
            <div class="{target_card_cls}">
                <div class="target-title">Take Profit 2 (TP2)</div>
                <div class="target-price" style="color: {target_color};">${tp2:,.4f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_t4:
        st.markdown(f"""
            <div class="{target_card_cls}">
                <div class="target-title">Stop Loss (SL)</div>
                <div class="target-price" style="color: #EF4444;">${sl:,.4f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TradingView Live Chart Widget ---
    st.markdown("### 📊 Advanced Price Chart")

    chart_html = f"""
    <div class="tradingview-widget-container" style="height:500px;width:100%; border-radius: 12px; overflow: hidden; border: 1px solid #E2E8F0;">
      <div id="tradingview_chart" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "{chart_interval}",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#FFFFFF",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    st.components.v1.html(chart_html, height=520)


# ================= PAGE 2: TRADING NOTEPAD =================
elif app_page == "📝 Trading Notepad":
    st.markdown(f'<p class="main-title">📝 Trading Notepad & Journal</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title-desc">Keep track of your strategies, market thoughts, and analysis notes.</p>', unsafe_allow_html=True)

    if 'notepad_content' not in st.session_state:
        st.session_state.notepad_content = ""

    note_text = st.text_area("Notes Area", value=st.session_state.notepad_content, height=250, label_visibility="collapsed", placeholder="Write down your trading notes, targets, or analysis here...")

    col_n1, col_n2, col_n3 = st.columns([1, 1, 4])
    with col_n1:
        if st.button("💾 Save Notes", use_container_width=True):
            st.session_state.notepad_content = note_text
            st.success("Notes saved successfully!")
    with col_n2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.notepad_content = ""
            st.rerun()
