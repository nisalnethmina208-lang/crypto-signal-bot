import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Binance Signal App VIP Pro", page_icon="👑", layout="wide")

# --- Password Protection Function ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234Binance@":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("## 👑 VIP App Login")
        st.text_input("Enter Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("## 👑 VIP App Login")
        st.text_input("Enter Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        st.error("😕 Incorrect Password")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Compact & VIP Styled CSS
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; color: #0F172A; }
    .vip-header { font-size: 26px; font-weight: 900; color: #1E293B; margin-bottom: 2px; letter-spacing: -0.5px; }
    .vip-badge { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 2px 8px; font-size: 10px; font-weight: 800; border-radius: 4px; text-transform: uppercase; vertical-align: middle; margin-left: 8px; }
    .sub-desc { color: #64748B; font-size: 13px; margin-bottom: 20px; }
    .card { background: #FFFFFF; border: 1px solid #E2E8F0; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
    .signal-box { color: white; padding: 10px; font-size: 16px; font-weight: 700; border-radius: 8px; text-align: center; }
    .t-card { background: #F1F5F9; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- Binance API Fetcher (Updated & Fixed) ---
@st.cache_data(ttl=30)
def get_binance_data(symbol):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        ticker_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        t_res = requests.get(ticker_url, headers=headers, timeout=10)
        
        if t_res.status_code != 200:
            return None, None, None
            
        t_data = t_res.json()
        price = float(t_data['lastPrice'])
        change = float(t_data['priceChangePercent'])
        
        klines_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=50"
        k_res = requests.get(klines_url, headers=headers, timeout=10).json()
        
        df = pd.DataFrame(k_res, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        return price, change, current_rsi
    except Exception as e:
        return None, None, None

# Sidebar with 150+ Coins List
with st.sidebar:
    st.markdown("### 👑 VIP Menu")
    page = st.selectbox("Navigation", ["Live Signal", "Notepad"])
    
    coins = {
        # --- Major Coins ---
        "BTC/USDT": "BTCUSDT", "ETH/USDT": "ETHUSDT", "BNB/USDT": "BNBUSDT", "SOL/USDT": "SOLUSDT",
        "XRP/USDT": "XRPUSDT", "ADA/USDT": "ADAUSDT", "DOGE/USDT": "DOGEUSDT", "AVAX/USDT": "AVAXUSDT",
        "TRX/USDT": "TRXUSDT", "DOT/USDT": "DOTUSDT", "LINK/USDT": "LINKUSDT", "UNI/USDT": "UNIUSDT",
        "MATIC/USDT": "MATICUSDT", "NEAR/USDT": "NEARUSDT", "APT/USDT": "APTUSDT", "FTM/USDT": "FTMUSDT",
        "ICP/USDT": "ICPUSDT", "RENDER/USDT": "RENDERUSDT", "INJ/USDT": "INJUSDT", "TIA/USDT": "TIAUSDT",
        "ARB/USDT": "ARBUSDT", "OP/USDT": "OPUSDT", "SUI/USDT": "SUIUSDT", "PEPE/USDT": "PEPEUSDT",
        "SHIB/USDT": "SHIBUSDT", "FLOKI/USDT": "FLOKIUSDT", "BONK/USDT": "BONKUSDT", "WIF/USDT": "WIFUSDT",
        "JUP/USDT": "JUPUSDT", "ONDO/USDT": "ONDOUSDT", "PENDLE/USDT": "PENDLEUSDT", "FET/USDT": "FETUSDT",
        
        # --- Layer 1 & Layer 2 ---
        "ATOM/USDT": "ATOMUSDT", "LTC/USDT": "LTCUSDT", "XLM/USDT": "XLMUSDT", "BCH/USDT": "BCHUSDT",
        "ALGO/USDT": "ALGOUSDT", "VET/USDT": "VETUSDT", "GRT/USDT": "GRTUSDT", "HBAR/USDT": "HBARUSDT",
        "STX/USDT": "STXUSDT", "SEI/USDT": "SEIUSDT", "KAS/USDT": "KASUSDT", "MINA/USDT": "MINAUSDT",
        "CFX/USDT": "CFXUSDT", "ROSE/USDT": "ROSEUSDT", "EGLD/USDT": "EGLDUSDT", "FLOW/USDT": "FLOWUSDT",
        "EOS/USDT": "EOSUSDT", "XTZ/USDT": "XTZUSDT", "KAVA/USDT": "KAVAUSDT", "RLC/USDT": "RLCUSDT",
        "ZIL/USDT": "ZILUSDT", "ICX/USDT": "ICXUSDT", "IOST/USDT": "IOSTUSDT", "ONT/USDT": "ONTUSDT",
        "QTUM/USDT": "QTUMUSDT", "ZEC/USDT": "ZECUSDT", "DASH/USDT": "DASHUSDT", "XMR/USDT": "XMRUSDT",
        
        # --- DeFi & Governance ---
        "AAVE/USDT": "AAVEUSDT", "MKR/USDT": "MKRUSDT", "SNX/USDT": "SNXUSDT", "CRV/USDT": "CRVUSDT",
        "COMP/USDT": "COMPUSDT", "SUSHI/USDT": "SUSHIUSDT", "CAKE/USDT": "CAKEUSDT", "1INCH/USDT": "1INCHUSDT",
        "LDO/USDT": "LDOUSDT", "FXS/USDT": "FXSUSDT", "GMX/USDT": "GMXUSDT", "DYDX/USDT": "DYDXUSDT",
        "PERP/USDT": "PERPUSDT", "BAL/USDT": "BALUSDT", "LRC/USDT": "LRCUSDT", "KNC/USDT": "KNCUSDT",
        "ZRX/USDT": "ZRXUSDT", "BAT/USDT": "BATUSDT", "ENJ/USDT": "ENJUSDT", "CHZ/USDT": "CHZUSDT",
        
        # --- Metaverse, Gaming & NFT ---
        "SAND/USDT": "SANDUSDT", "MANA/USDT": "MANAUSDT", "AXS/USDT": "AXSUSDT", "GALA/USDT": "GALAUSDT",
        "APE/USDT": "APEUSDT", "ILV/USDT": "ILVUSDT", "YGG/USDT": "YGGUSDT", "HIGH/USDT": "HIGHUSDT",
        "MAGIC/USDT": "MAGICUSDT", "TLM/USDT": "TLMUSDT", "ALICE/USDT": "ALICEUSDT", "VOXEL/USDT": "VOXELUSDT",
        
        # --- AI & Big Data ---
        "AGIX/USDT": "AGIXUSDT", "OCEAN/USDT": "OCEANUSDT", "RNDR/USDT": "RNDRUSDT", "NMR/USDT": "NMRUSDT",
        "CTSI/USDT": "CTSIUSDT", "API3/USDT": "API3USDT", "ID/USDT": "IDUSDT", "AI/USDT": "AIUSDT",
        "WLD/USDT": "WLDUSDT", "NFP/USDT": "NFPUSDT", "PORTAL/USDT": "PORTALUSDT", "CYBER/USDT": "CYBERUSDT",
        
        # --- Meme & Community ---
        "MEME/USDT": "MEMEUSDT", "BOME/USDT": "BOMEUSDT", "SLP/USDT": "SLPUSDT", "DOGS/USDT": "DOGSUSDT",
        "CATI/USDT": "CATIUSDT", "HMSTR/USDT": "HMSTRUSDT", "NEIRO/USDT": "NEIROUSDT", "TURBO/USDT": "TURBOUSDT",
        
        # --- Launchpool & New Tokens ---
        "STRK/USDT": "STRKUSDT", "PIXEL/USDT": "PIXELUSDT", "PORT3/USDT": "PORT3USDT", "MANTA/USDT": "MANTAUSDT",
        "ALT/USDT": "ALTUSDT", "DYM/USDT": "DYMUSDT", "MAV/USDT": "MAVUSDT", "RDNT/USDT": "RDNTUSDT",
        "ARKM/USDT": "ARKMUSDT", "POLYX/USDT": "POLYXUSDT", "SSV/USDT": "SSVUSDT", "ACH/USDT": "ACHUSDT",
        
        # --- Infrastructure & Others ---
        "THETA/USDT": "THETAUSDT", "STORJ/USDT": "STORJUSDT", "ANKR/USDT": "ANKRUSDT", "PYTH/USDT": "PYTHUSDT",
        "ZRO/USDT": "ZROUSDT", "BLUR/USDT": "BLURUSDT", "ACE/USDT": "ACEUSDT", "XAI/USDT": "XAIUSDT",
        "COMBO/USDT": "COMBOUSDT", "STG/USDT": "STGUSDT", "LQTY/USDT": "LQTYUSDT", "AGLD/USDT": "AGLDUSDT",
        "SYS/USDT": "SYSUSDT", "LSK/USDT": "LSKUSDT", "HIVE/USDT": "HIVEUSDT", "POWR/USDT": "POWRUSDT",
        "BLZ/USDT": "BLZUSDT", "SUPER/USDT": "SUPERUSDT", "BAKE/USDT": "BAKEUSDT", "TKO/USDT": "TKOUSDT",
        "PUNDIX/USDT": "PUNDIXUSDT", "SUN/USDT": "SUNUSDT", "JST/USDT": "JSTUSDT", "REEF/USDT": "REEFUSDT",
        "AR/USDT": "ARUSDT", "WOO/USDT": "WOOUSDT", "GNO/USDT": "GNOUSDT", "CVX/USDT": "CVXUSDT",
        "PEOPLE/USDT": "PEOPLEUSDT", "SPELL/USDT": "SPELLUSDT", "JOE/USDT": "JOEUSDT", "IMX/USDT": "IMXUSDT"
    }
    
    sel = st.selectbox("Select Coin Pair", list(coins.keys()))
    binance_sym = coins[sel]
    tv_sym = f"BINANCE:{binance_sym}"

price, change, rsi = get_binance_data(binance_sym)

if price is None:
    st.warning("⚠️ Binance API එකෙන් දත්ත ලබාගැනීමේදී බාධාවක් ඇති විය. කරුණාකර මොහොතකින් නැවත උත්සාහ කරන්න හෝ Refresh කරන්න.")
    price, change, rsi = 0.0, 0.0, 50.0

# Smart Signal Logic based on RSI
if rsi < 42:
    signal_type = "STRONG BUY 🚀"
    signal_color = "#10B981"
elif rsi > 58:
    signal_type = "STRONG SELL 🔻"
    signal_color = "#EF4444"
else:
    signal_type = "NEUTRAL / HOLD ⚖️"
    signal_color = "#F59E0B"

# App Header
st.markdown('<p class="vip-header">👑 Binance Signal App VIP <span class="vip-badge">Pro RSI Engine</span></p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-desc">Advanced technical signals powered by <b>Binance Live API & RSI Indicator</b> for <b>{sel}</b>.</p>', unsafe_allow_html=True)

if page == "Live Signal":
    col1, col2 = st.columns([3, 1])
    with col1:
        up = change >= 0
        st.markdown(f"**Price:** ${price:,.4f} | **24h Change:** <span style='color: {'#059669' if up else '#DC2626'};'>{change:,.2f}%</span> | **RSI (14):** <b>{rsi:.1f}</b>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="signal-box" style="background: {signal_color};">{signal_type}</div>', unsafe_allow_html=True)

    # Dynamic TP / SL Calculations
    if "BUY" in signal_type:
        tp1 = price * 1.015
        tp2 = price * 1.030
        sl = price * 0.988
    elif "SELL" in signal_type:
        tp1 = price * 0.985
        tp2 = price * 0.970
        sl = price * 1.012
    else:
        tp1 = price * 1.010
        tp2 = price * 1.020
        sl = price * 0.990

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="t-card">Entry<br><b>${price:,.4f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="t-card">TP 1<br><b style="color: #059669;">${tp1:,.4f}</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="t-card">TP 2<br><b style="color: #059669;">${tp2:,.4f}</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="t-card">SL<br><b style="color: #DC2626;">${sl:,.4f}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Live TradingView Chart
    chart_html = f"""
    <div class="tradingview-widget-container" style="height:350px;width:100%">
      <div id="tv_chart" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{"autosize": true, "symbol": "{tv_sym}", "interval": "15", "timezone": "Etc/UTC", "theme": "light", "style": "1", "locale": "en", "container_id": "tv_chart"}});
      </script>
    </div>
    """
    st.components.v1.html(chart_html, height=360)

elif page == "Notepad":
    st.markdown('### 📝 VIP Trading Notepad', unsafe_allow_html=True)
    if 'note' not in st.session_state: 
        st.session_state.note = ""
    st.session_state.note = st.text_area("Note", value=st.session_state.note, height=200, label_visibility="collapsed", placeholder="Write down your VIP notes here...")
    if st.button("Clear Notes"): 
        st.session_state.note = ""
        st.rerun()
