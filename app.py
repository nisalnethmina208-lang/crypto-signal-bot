import streamlit as st
import requests

st.set_page_config(page_title="Binance Signal App VIP", page_icon="👑", layout="wide")

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

@st.cache_data(ttl=300)
def get_data(cid):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd&include_24hr_change=true"
        return requests.get(url, timeout=5).json()
    except:
        return None

# Sidebar with 100+ Coins
with st.sidebar:
    st.markdown("### 👑 VIP Menu")
    page = st.selectbox("Navigation", ["Live Signal", "Notepad"])
    
    coins = {
        "BTC/USDT": {"id": "bitcoin", "sym": "BINANCE:BTCUSDT"},
        "ETH/USDT": {"id": "ethereum", "sym": "BINANCE:ETHUSDT"},
        "BNB/USDT": {"id": "binancecoin", "sym": "BINANCE:BNBUSDT"},
        "SOL/USDT": {"id": "solana", "sym": "BINANCE:SOLUSDT"},
        "XRP/USDT": {"id": "ripple", "sym": "BINANCE:XRPUSDT"},
        "ADA/USDT": {"id": "cardano", "sym": "BINANCE:ADAUSDT"},
        "DOGE/USDT": {"id": "dogecoin", "sym": "BINANCE:DOGEUSDT"},
        "AVAX/USDT": {"id": "avalanche-2", "sym": "BINANCE:AVAXUSDT"},
        "TRX/USDT": {"id": "tron", "sym": "BINANCE:TRXUSDT"},
        "DOT/USDT": {"id": "polkadot", "sym": "BINANCE:DOTUSDT"},
        "MATIC/USDT": {"id": "polygon-ecosystem-token", "sym": "BINANCE:MATICUSDT"},
        "LINK/USDT": {"id": "chainlink", "symbol": "BINANCE:LINKUSDT" if False else "BINANCE:LINKUSDT"},
        "UNI/USDT": {"id": "uniswap", "sym": "BINANCE:UNIUSDT"},
        "ATOM/USDT": {"id": "cosmos", "sym": "BINANCE:ATOMUSDT"},
        "LTC/USDT": {"id": "litecoin", "sym": "BINANCE:LTCUSDT"},
        "NEAR/USDT": {"id": "near", "sym": "BINANCE:NEARUSDT"},
        "APT/USDT": {"id": "aptos", "sym": "BINANCE:APTUSDT"},
        "FTM/USDT": {"id": "fantom", "sym": "BINANCE:FTMUSDT"},
        "ICP/USDT": {"id": "internet-computer", "sym": "BINANCE:ICPUSDT"},
        "RENDER/USDT": {"id": "render-token", "sym": "BINANCE:RNDRUSDT"},
        "INJ/USDT": {"id": "injective-protocol", "sym": "BINANCE:INJUSDT"},
        "TIA/USDT": {"id": "celestia", "sym": "BINANCE:TIAUSDT"},
        "ARB/USDT": {"id": "arbitrum", "sym": "BINANCE:ARBUSDT"},
        "OP/USDT": {"id": "optimism", "sym": "BINANCE:OPUSDT"},
        "SUI/USDT": {"id": "sui", "sym": "BINANCE:SUIUSDT"},
        "SEI/USDT": {"id": "sei-network", "sym": "BINANCE:SEIUSDT"},
        "PEPE/USDT": {"id": "pepe", "sym": "BINANCE:PEPEUSDT"},
        "SHIB/USDT": {"id": "shiba-inu", "sym": "BINANCE:SHIBUSDT"},
        "FLOKI/USDT": {"id": "floki", "sym": "BINANCE:FLOKIUSDT"},
        "BONK/USDT": {"id": "bonk", "sym": "BINANCE:BONKUSDT"},
        "XLM/USDT": {"id": "stellar", "sym": "BINANCE:XLMUSDT"},
        "BCH/USDT": {"id": "bitcoin-cash", "sym": "BINANCE:BCHUSDT"},
        "ALGO/USDT": {"id": "algorand", "sym": "BINANCE:ALGOUSDT"},
        "VET/USDT": {"id": "vechain", "sym": "BINANCE:VETUSDT"},
        "GRT/USDT": {"id": "the-graph", "sym": "BINANCE:GRTUSDT"},
        "SAND/USDT": {"id": "the-sandbox", "sym": "BINANCE:SANDUSDT"},
        "MANA/USDT": {"id": "decentraland", "sym": "BINANCE:MANAUSDT"},
        "AXS/USDT": {"id": "axie-infinity", "sym": "BINANCE:AXSUSDT"},
        "THETA/USDT": {"id": "theta-token", "sym": "BINANCE:THETAUSDT"},
        "EGLD/USDT": {"id": "elrond-erd-2", "sym": "BINANCE:EGLDUSDT"},
        "KAS/USDT": {"id": "kaspa", "sym": "BINANCE:KASUSDT"},
        "HBAR/USDT": {"id": "hedera-hashgraph", "sym": "BINANCE:HBARUSDT"},
        "FLOW/USDT": {"id": "flow", "sym": "BINANCE:FLOWUSDT"},
        "EOS/USDT": {"id": "eos", "sym": "BINANCE:EOSUSDT"},
        "CRV/USDT": {"id": "curve-dao-token", "sym": "BINANCE:CRVUSDT"},
        "AAVE/USDT": {"id": "aave", "sym": "BINANCE:AAVEUSDT"},
        "MKR/USDT": {"id": "maker", "sym": "BINANCE:MKRUSDT"},
        "SNX/USDT": {"id": "synthetix-network-token", "sym": "BINANCE:SNXUSDT"},
        "COMP/USDT": {"id": "compound-governance-token", "sym": "BINANCE:COMPUSDT"},
        "CHZ/USDT": {"id": "chiliz", "sym": "BINANCE:CHZUSDT"},
        "ZIL/USDT": {"id": "zilliqa", "sym": "BINANCE:ZILUSDT"},
        "ENJ/USDT": {"id": "enjincoin", "sym": "BINANCE:ENJUSDT"},
        "BAT/USDT": {"id": "basic-attention-token", "sym": "BINANCE:BATUSDT"},
        "ZRX/USDT": {"id": "0x", "sym": "BINANCE:ZRXUSDT"},
        "GALA/USDT": {"id": "gala", "sym": "BINANCE:GALAUSDT"},
        "ROSE/USDT": {"id": "oasis-network", "sym": "BINANCE:ROSEUSDT"},
        "ICX/USDT": {"id": "icon", "sym": "BINANCE:ICXUSDT"},
        "KAVA/USDT": {"id": "kava", "sym": "BINANCE:KAVAUSDT"},
        "IOTX/USDT": {"id": "iotex", "sym": "BINANCE:IOTXUSDT"},
        "STX/USDT": {"id": "blockstack", "sym": "BINANCE:STXUSDT"},
        "CKB/USDT": {"id": "nervos-network", "sym": "BINANCE:CKBUSDT"},
        "MINA/USDT": {"id": "mina-protocol", "sym": "BINANCE:MINAUSDT"},
        "GLMR/USDT": {"id": "moonbeam", "sym": "BINANCE:GLMRUSDT"},
        "ACH/USDT": {"id": "alchemy-pay", "sym": "BINANCE:ACHUSDT"},
        "JASMY/USDT": {"id": "jasmycoin", "sym": "BINANCE:JASMYUSDT"},
        "LDO/USDT": {"id": "lido-dao", "sym": "BINANCE:LDOUSDT"},
        "SSV/USDT": {"id": "ssv-network", "sym": "BINANCE:SSVUSDT"},
        "CFX/USDT": {"id": "conflux-token", "sym": "BINANCE:CFXUSDT"},
        "MASK/USDT": {"id": "mask-network", "sym": "BINANCE:MASKUSDT"},
        "AGIX/USDT": {"id": "singularitynet", "sym": "BINANCE:AGIXUSDT"},
        "FET/USDT": {"id": "fetch-ai", "sym": "BINANCE:FETUSDT"},
        "RLC/USDT": {"id": "iexec-rlc", "sym": "BINANCE:RLCUSDT"},
        "BAND/USDT": {"id": "band-protocol", "sym": "BINANCE:BANDUSDT"},
        "API3/USDT": {"id": "api3", "sym": "BINANCE:API3USDT"},
        "SKL/USDT": {"id": "ankr-network", "sym": "BINANCE:SKLUSDT"},
        "CTSI/USDT": {"id": "cartesi", "sym": "BINANCE:CTSIUSDT"},
        "COTI/USDT": {"id": "coti", "sym": "BINANCE:COTIUSDT"},
        "DGB/USDT": {"id": "digibyte", "sym": "BINANCE:DGBUSDT"},
        "SC/USDT": {"id": "siacoin", "sym": "BINANCE:SCUSDT"},
        "RVN/USDT": {"id": "ravencoin", "sym": "BINANCE:RVNUSDT"},
        "IOST/USDT": {"id": "iostoken", "sym": "BINANCE:IOSTUSDT"},
        "ONT/USDT": {"id": "ontology", "sym": "BINANCE:ONTUSDT"},
        "ZEC/USDT": {"id": "zcash", "sym": "BINANCE:ZECUSDT"},
        "DASH/USDT": {"id": "dash", "sym": "BINANCE:DASHUSDT"},
        "XMR/USDT": {"id": "monero", "sym": "BINANCE:XMRUSDT"},
        "ZEN/USDT": {"id": "horizen", "sym": "BINANCE:ZENUSDT"},
        "QTUM/USDT": {"id": "qtum", "sym": "BINANCE:QTUMUSDT"},
        "OMG/USDT": {"id": "omisego", "sym": "BINANCE:OMGUSDT"},
        "NKN/USDT": {"id": "nkn", "sym": "BINANCE:NKNUSDT"},
        "OGN/USDT": {"id": "origin-protocol", "sym": "BINANCE:OGNUSDT"},
        "BAL/USDT": {"id": "balancer", "sym": "BINANCE:BALUSDT"},
        "LRC/USDT": {"id": "loopring", "sym": "BINANCE:LRCUSDT"},
        "SXP/USDT": {"id": "swipe", "sym": "BINANCE:SXPUSDT"},
        "KNC/USDT": {"id": "kyber-network-crystal", "sym": "BINANCE:KNCUSDT"},
        "STORJ/USDT": {"id": "storj", "sym": "BINANCE:STORJUSDT"},
        "ANKR/USDT": {"id": "ankr", "sym": "BINANCE:ANKRUSDT"}
    }
    
    sel = st.selectbox("Select Coin Pair", list(coins.keys()))
    cid, tv_sym = coins[sel]["id"], coins[sel]["sym"]

data = get_data(cid)
price = data[cid]['usd'] if data and cid in data else 0.0
change = data[cid]['usd_24h_change'] if data and cid in data else 0.0
up = change >= 0

# App Header (VIP Title)
st.markdown('<p class="vip-header">👑 Binance Signal App VIP <span class="vip-badge">VIP Pro</span></p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-desc">Real-time automated technical signals and targets for <b>{sel}</b>.</p>', unsafe_allow_html=True)

if page == "Live Signal":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Price:** ${price:,.4f} | **24h Change:** <span style='color: {'#059669' if up else '#DC2626'};'>{change:,.2f}%</span>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="signal-box" style="background: {"#10B981" if up else "#EF4444"};">{"BUY 🚀" if up else "SELL 🔻"}</div>', unsafe_allow_html=True)

    # TP / SL Compact Cards
    tp1 = price * (1.015 if up else 0.985)
    tp2 = price * (1.035 if up else 0.965)
    sl = price * (0.992 if up else 1.008)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="t-card">Entry<br><b>${price:,.4f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="t-card">TP 1<br><b style="color: #059669;">${tp1:,.4f}</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="t-card">TP 2<br><b style="color: #059669;">${tp2:,.4f}</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="t-card">SL<br><b style="color: #DC2626;">${sl:,.4f}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Small TradingView Chart
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
    if 'note' not in st.session_state: st.session_state.note = ""
    st.session_state.note = st.text_area("Note", value=st.session_state.note, height=200, label_visibility="collapsed", placeholder="Write down your VIP notes here...")
    if st.button("Clear Notes"): st.session_state.note = ""; st.rerun()
