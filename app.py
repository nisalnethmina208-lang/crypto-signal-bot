import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="Binance Pro Trading Center",
    page_icon="📈",
    layout="wide"
)

# Studio Light Theme & Custom CSS (White Background & Black Text)
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    .main-title {
        font-size: 28px;
        font-weight: bold;
        color: #B28800;
        margin-bottom: 10px;
    }
    .trading-card {
        background-color: #F8F9FA;
        border: 1px solid #D1D5DB;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .ticker-title {
        font-size: 32px;
        font-weight: bold;
        color: #111827 !important;
    }
    .binance-spot {
        color: #4B5563;
        font-size: 12px;
        text-transform: uppercase;
    }
    .buy-btn {
        background-color: #10B981;
        color: white;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        text-align: center;
        float: right;
    }
    .sell-btn {
        background-color: #EF4444;
        color: white;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        text-align: center;
        float: right;
    }
    .trend-up { color: #059669 !important; font-weight: bold; }
    .trend-down { color: #DC2626 !important; font-weight: bold; }
    .stat-label { color: #4B5563; font-size: 13px; }
    .stat-val { color: #111827; font-size: 16px; font-weight: bold; }

    .stTextArea textarea {
        background-color: #F8F9FA !important;
        color: #000000 !important;
        border: 1px solid #D1D5DB !important;
    }
    
    /* Streamlit Sidebar adjustments for Light Theme */
    [data-testid="stSidebar"] {
        background-color: #F3F4F6;
        color: #000000;
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

# --- Sidebar (Settings) ---
with st.sidebar:
    st.markdown("## ⚙️ Binance Settings")
    
    # Expanded Coin Options (Coins 100+)
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
        "ATOM/USDT": {"id": "cosmos", "symbol": "BINANCE:ATOMUSDT"},
        "LTC/USDT": {"id": "litecoin", "symbol": "BINANCE:LTCUSDT"},
        "NEAR/USDT": {"id": "near", "symbol": "BINANCE:NEARUSDT"},
        "APT/USDT": {"id": "aptos", "symbol": "BINANCE:APTUSDT"},
        "FTM/USDT": {"id": "fantom", "symbol": "BINANCE:FTMUSDT"},
        "ICP/USDT": {"id": "internet-computer", "symbol": "BINANCE:ICPUSDT"},
        "RENDER/USDT": {"id": "render-token", "symbol": "BINANCE:RNDRUSDT"},
        "INJ/USDT": {"id": "injective-protocol", "symbol": "BINANCE:INJUSDT"},
        "TIA/USDT": {"id": "celestia", "symbol": "BINANCE:TIAUSDT"},
        "ARB/USDT": {"id": "arbitrum", "symbol": "BINANCE:ARBUSDT"},
        "OP/USDT": {"id": "optimism", "symbol": "BINANCE:OPUSDT"},
        "SUI/USDT": {"id": "sui", "symbol": "BINANCE:SUIUSDT"},
        "SEI/USDT": {"id": "sei-network", "symbol": "BINANCE:SEIUSDT"},
        "PEPE/USDT": {"id": "pepe", "symbol": "BINANCE:PEPEUSDT"},
        "SHIB/USDT": {"id": "shiba-inu", "symbol": "BINANCE:SHIBUSDT"},
        "FLOKI/USDT": {"id": "floki", "symbol": "BINANCE:FLOKIUSDT"},
        "BONK/USDT": {"id": "bonk", "symbol": "BINANCE:BONKUSDT"},
        "XLM/USDT": {"id": "stellar", "symbol": "BINANCE:XLMUSDT"},
        "BCH/USDT": {"id": "bitcoin-cash", "symbol": "BINANCE:BCHUSDT"},
        "ALGO/USDT": {"id": "algorand", "symbol": "BINANCE:ALGOUSDT"},
        "VET/USDT": {"id": "vechain", "symbol": "BINANCE:VETUSDT"},
        "GRT/USDT": {"id": "the-graph", "symbol": "BINANCE:GRTUSDT"},
        "SAND/USDT": {"id": "the-sandbox", "symbol": "BINANCE:SANDUSDT"},
        "MANA/USDT": {"id": "decentraland", "symbol": "BINANCE:MANAUSDT"},
        "AXS/USDT": {"id": "axie-infinity", "symbol": "BINANCE:AXSUSDT"},
        "THETA/USDT": {"id": "theta-token", "symbol": "BINANCE:THETAUSDT"},
        "EGLD/USDT": {"id": "elrond-erd-2", "symbol": "BINANCE:EGLDUSDT"},
        "KAS/USDT": {"id": "kaspa", "symbol": "BINANCE:KASUSDT"},
        "HBAR/USDT": {"id": "hedera-hashgraph", "symbol": "BINANCE:HBARUSDT"},
        "FLOW/USDT": {"id": "flow", "symbol": "BINANCE:FLOWUSDT"},
        "EOS/USDT": {"id": "eos", "symbol": "BINANCE:EOSUSDT"},
        "CRV/USDT": {"id": "curve-dao-token", "symbol": "BINANCE:CRVUSDT"},
        "AAVE/USDT": {"id": "aave", "symbol": "BINANCE:AAVEUSDT"},
        "MKR/USDT": {"id": "maker", "symbol": "BINANCE:MKRUSDT"},
        "SNX/USDT": {"id": "synthetix-network-token", "symbol": "BINANCE:SNXUSDT"},
        "COMP/USDT": {"id": "compound-governance-token", "symbol": "BINANCE:COMPUSDT"},
        "CHZ/USDT": {"id": "chiliz", "symbol": "BINANCE:CHZUSDT"},
        "ZIL/USDT": {"id": "zilliqa", "symbol": "BINANCE:ZILUSDT"},
        "ENJ/USDT": {"id": "enjincoin", "symbol": "BINANCE:ENJUSDT"},
        "BAT/USDT": {"id": "basic-attention-token", "symbol": "BINANCE:BATUSDT"},
        "ZRX/USDT": {"id": "0x", "symbol": "BINANCE:ZRXUSDT"},
        "GALA/USDT": {"id": "gala", "symbol": "BINANCE:GALAUSDT"},
        "ROSE/USDT": {"id": "oasis-network", "symbol": "BINANCE:ROSEUSDT"},
        "ICX/USDT": {"id": "icon", "symbol": "BINANCE:ICXUSDT"},
        "KAVA/USDT": {"id": "kava", "symbol": "BINANCE:KAVAUSDT"},
        "IOTX/USDT": {"id": "iotex", "symbol": "BINANCE:IOTXUSDT"},
        "STX/USDT": {"id": "blockstack", "symbol": "BINANCE:STXUSDT"},
        "CKB/USDT": {"id": "nervos-network", "symbol": "BINANCE:CKBUSDT"},
        "MINA/USDT": {"id": "mina-protocol", "symbol": "BINANCE:MINAUSDT"},
        "GLMR/USDT": {"id": "moonbeam", "symbol": "BINANCE:GLMRUSDT"},
        "ACH/USDT": {"id": "alchemy-pay", "symbol": "BINANCE:ACHUSDT"},
        "JASMY/USDT": {"id": "jasmycoin", "symbol": "BINANCE:JASMYUSDT"},
        "LDO/USDT": {"id": "lido-dao", "symbol": "BINANCE:LDOUSDT"},
        "SSV/USDT": {"id": "ssv-network", "symbol": "BINANCE:SSVUSDT"},
        "CFX/USDT": {"id": "conflux-token", "symbol": "BINANCE:CFXUSDT"},
        "MASK/USDT": {"id": "mask-network", "symbol": "BINANCE:MASKUSDT"},
        "AGIX/USDT": {"id": "singularitynet", "symbol": "BINANCE:AGIXUSDT"},
        "FET/USDT": {"id": "fetch-ai", "symbol": "BINANCE:FETUSDT"},
        "RLC/USDT": {"id": "iexec-rlc", "symbol": "BINANCE:RLCUSDT"},
        "BAND/USDT": {"id": "band-protocol", "symbol": "BINANCE:BANDUSDT"},
        "API3/USDT": {"id": "api3", "symbol": "BINANCE:API3USDT"},
        "SKL/USDT": {"id": "ankr-network", "symbol": "BINANCE:SKLUSDT"},
        "CTSI/USDT": {"id": "cartesi", "symbol": "BINANCE:CTSIUSDT"},
        "COTI/USDT": {"id": "coti", "symbol": "BINANCE:COTIUSDT"},
        "DGB/USDT": {"id": "digibyte", "symbol": "BINANCE:DGBUSDT"},
        "SC/USDT": {"id": "siacoin", "symbol": "BINANCE:SCUSDT"},
        "RVN/USDT": {"id": "ravencoin", "symbol": "BINANCE:RVNUSDT"},
        "IOST/USDT": {"id": "iostoken", "symbol": "BINANCE:IOSTUSDT"},
        "ONT/USDT": {"id": "ontology", "symbol": "BINANCE:ONTUSDT"},
        "ZEC/USDT": {"id": "zcash", "symbol": "BINANCE:ZECUSDT"},
        "DASH/USDT": {"id": "dash", "symbol": "BINANCE:DASHUSDT"},
        "XMR/USDT": {"id": "monero", "symbol": "BINANCE:XMRUSDT"},
        "ZEN/USDT": {"id": "horizen", "symbol": "BINANCE:ZENUSDT"},
        "QTUM/USDT": {"id": "qtum", "symbol": "BINANCE:QTUMUSDT"},
        "OMG/USDT": {"id": "omisego", "symbol": "BINANCE:OMGUSDT"},
        "NKN/USDT": {"id": "nkn", "symbol": "BINANCE:NKNUSDT"},
        "OGN/USDT": {"id": "origin-protocol", "symbol": "BINANCE:OGNUSDT"},
        "BAL/USDT": {"id": "balancer", "symbol": "BINANCE:BALUSDT"},
        "LRC/USDT": {"id": "loopring", "symbol": "BINANCE:LRCUSDT"},
        "SXP/USDT": {"id": "swipe", "symbol": "BINANCE:SXPUSDT"},
        "KNC/USDT": {"id": "kyber-network-crystal", "symbol": "BINANCE:KNCUSDT"},
        "STORJ/USDT": {"id": "storj", "symbol": "BINANCE:STORJUSDT"},
        "ANKR/USDT": {"id": "ankr", "symbol": "BINANCE:ANKRUSDT"}
    }
    
    selected_coin_display = st.selectbox("Select Market:", list(coin_options.keys()), index=0)
    coin_id = coin_options[selected_coin_display]["id"]
    tv_symbol = coin_options[selected_coin_display]["symbol"]
    
    chart_interval = st.selectbox("Chart Interval:", ["1", "15", "60", "D"], index=1, format_func=lambda x: {"1": "1m", "15": "15m", "60": "1H", "D": "1D"}[x])
    st.markdown("---")

# --- Main App Layout ---
st.markdown(f'<p class="main-title">📈 Binance Live Trading Center - {selected_coin_display}</p>', unsafe_allow_html=True)

# Fetch Live Stats
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
action_type = "BUY" if is_uptrend else "SELL"
btn_class = "buy-btn" if is_uptrend else "sell-btn"
change_icon = "▲" if is_uptrend else "▼"

# Top Row
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.markdown(f'<p class="binance-spot">BINANCE SPOT</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="ticker-title">{selected_coin_display}</p>', unsafe_allow_html=True)
with col_top2:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown(f'<div class="{btn_class}">{action_type} 🚀</div>', unsafe_allow_html=True)

# Stats Card
st.markdown(f"""
    <div class="trading-card">
        <table width="100%">
            <tr>
                <td><div class="stat-label">LIVE PRICE</div><div class="stat-val">${last_price:,.2f}</div></td>
                <td><div class="stat-label">24H CHANGE</div><div class="stat-val {trend_class}">{change_icon} {change_24h:,.2f}%</div></td>
                <td><div class="stat-label">24H HIGH</div><div class="stat-val">${high_24h:,.2f}</div></td>
                <td><div class="stat-label">24H LOW</div><div class="stat-val">${low_24h:,.2f}</div></td>
            </tr>
        </table>
    </div>
""", unsafe_allow_html=True)

# --- TradingView Live Chart Widget (Direct HTML Embed - Light Theme) ---
st.subheader("📊 Live Price Chart")

chart_html = f"""
<div class="tradingview-widget-container" style="height:500px;width:100%">
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
    "toolbar_bg": "#f8f9fa",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
st.components.v1.html(chart_html, height=520)

st.markdown("---")

# --- Notepad Section ---
st.subheader("📝 Trading Notepad")
if 'notepad_content' not in st.session_state:
    st.session_state.notepad_content = ""

note_text = st.text_area("Notes Area", value=st.session_state.notepad_content, height=120, label_visibility="collapsed")

col_n1, col_n2 = st.columns(2)
with col_n1:
    if st.button("Save Notes", use_container_width=True):
        st.session_state.notepad_content = note_text
        st.success("Notes saved successfully!")
with col_n2:
    if st.button("Clear Notes", use_container_width=True):
        st.session_state.notepad_content = ""
        st.rerun()
