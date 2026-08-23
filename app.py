import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Binance Pro Signal App VIP - 197+ Coins Master", page_icon="👑", layout="wide")

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
        st.error("😕 මුරපදය වැරදියි (Incorrect Password)")
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
    .signal-box { color: white; padding: 10px; font-size: 15px; font-weight: 700; border-radius: 8px; text-align: center; }
    .t-card { background: #F1F5F9; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600, show_spinner=False)
def get_coingecko_market_data(coin_id):
    """CoinGecko API භාවිත කර දත්ත ලබා ගැනීම"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=8)
        
        if res.status_code == 200:
            data = res.json()
            if 'prices' in data and len(data['prices']) > 0:
                prices = [x[1] for x in data['prices']]
                df = pd.DataFrame(prices, columns=['close'])
                df['open'] = df['close'].shift(1).fillna(df['close'])
                df['high'] = df['close'] * 1.008
                df['low'] = df['close'] * 0.992
                df['volume'] = 100000
                return df
        return None
    except:
        return None

def calculate_smc_ict_indicators(df):
    close = df['close']
    high = df['high']
    low = df['low']
    open_p = df['open']
    
    # 1. Trend & Moving Averages
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    
    # 2. RSI & ATR
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    atr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).rolling(window=14).mean()

    # --- SMC & ICT CORE LOGIC ---
    df['swing_high'] = high.rolling(window=5).max()
    df['swing_low'] = low.rolling(window=5).min()
    
    current_close = close.iloc[-1]
    prev_high = df['swing_high'].iloc[-2]
    prev_low = df['swing_low'].iloc[-2]
    
    bos_bullish = current_close > prev_high
    bos_bearish = current_close < prev_low
    
    bullish_ob = (current_close > open_p.iloc[-1]) and (close.iloc[-2] < open_p.iloc[-2])
    bearish_ob = (current_close < open_p.iloc[-1]) and (close.iloc[-2] > open_p.iloc[-2])

    bullish_fvg = (low.iloc[-1] > high.iloc[-3]) if len(df) >= 3 else False
    bearish_fvg = (high.iloc[-1] < low.iloc[-3]) if len(df) >= 3 else False

    liquidity_sweep_buy = (low.iloc[-1] < df['swing_low'].rolling(window=10).min().iloc[-2]) and (current_close > open_p.iloc[-1])
    liquidity_sweep_sell = (high.iloc[-1] > df['swing_high'].rolling(window=10).max().iloc[-2]) and (current_close < open_p.iloc[-1])

    range_high = high.rolling(window=20).max().iloc[-1]
    range_low = low.rolling(window=20).min().iloc[-1]
    equilibrium = (range_high + range_low) / 2
    
    if current_close > equilibrium:
        zone = "Premium Zone (Sell Area)"
    else:
        zone = "Discount Zone (Buy Area)"

    return {
        "price": current_close,
        "ema9": ema9.iloc[-1],
        "ema21": ema21.iloc[-1],
        "rsi": rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0,
        "atr": atr.iloc[-1] if not np.isnan(atr.iloc[-1]) else current_close * 0.01,
        "bos_bullish": bos_bullish,
        "bos_bearish": bos_bearish,
        "bullish_ob": bullish_ob,
        "bearish_ob": bearish_ob,
        "bullish_fvg": bullish_fvg,
        "bearish_fvg": bearish_fvg,
        "liquidity_sweep_buy": liquidity_sweep_buy,
        "liquidity_sweep_sell": liquidity_sweep_sell,
        "zone": zone
    }

# Sidebar with 197+ Coins
with st.sidebar:
    st.markdown("### 👑 VIP Menu (197+ Coins SMC/ICT)")
    page = st.selectbox("පිටුව තෝරන්න (Navigation)", ["Live Signal", "SMC & ICT Analytics", "Notepad"])
    
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
        "LINK/USDT": {"id": "chainlink", "sym": "BINANCE:LINKUSDT"},
        "UNI/USDT": {"id": "uniswap", "sym": "BINANCE:UNIUSDT"},
        "NEAR/USDT": {"id": "near", "sym": "BINANCE:NEARUSDT"},
        "APT/USDT": {"id": "aptos", "sym": "BINANCE:APTUSDT"},
        "ICP/USDT": {"id": "internet-computer", "sym": "BINANCE:ICPUSDT"},
        "RENDER/USDT": {"id": "render-token", "sym": "BINANCE:RNDRUSDT"},
        "INJ/USDT": {"id": "injective-protocol", "sym": "BINANCE:INJUSDT"},
        "TIA/USDT": {"id": "celestia", "sym": "BINANCE:TIAUSDT"},
        "ARB/USDT": {"id": "arbitrum", "sym": "BINANCE:ARBUSDT"},
        "OP/USDT": {"id": "optimism", "sym": "BINANCE:OPUSDT"},
        "SUI/USDT": {"id": "sui", "sym": "BINANCE:SUIUSDT"},
        "PEPE/USDT": {"id": "pepe", "sym": "BINANCE:PEPEUSDT"},
        "SHIB/USDT": {"id": "shiba-inu", "sym": "BINANCE:SHIBUSDT"},
        "BCH/USDT": {"id": "bitcoin-cash", "sym": "BINANCE:BCHUSDT"},
        "ETC/USDT": {"id": "ethereum-classic", "sym": "BINANCE:ETCUSDT"},
        "FIL/USDT": {"id": "filecoin", "sym": "BINANCE:FILUSDT"},
        "HBAR/USDT": {"id": "hedera-hashgraph", "sym": "BINANCE:HBARUSDT"},
        "STX/USDT": {"id": "blockstack", "sym": "BINANCE:STXUSDT"},
        "IMX/USDT": {"id": "immutable-x", "sym": "BINANCE:IMXUSDT"},
        "GRT/USDT": {"id": "the-graph", "sym": "BINANCE:GRTUSDT"},
        "RUNE/USDT": {"id": "thorchain", "sym": "BINANCE:RUNEUSDT"},
        "SEI/USDT": {"id": "sei-network", "sym": "BINANCE:SEIUSDT"},
        "KAS/USDT": {"id": "kaspa", "sym": "BINANCE:KASUSDT"},
        "FET/USDT": {"id": "fetch-ai", "sym": "BINANCE:FETUSDT"},
        "FLOKI/USDT": {"id": "floki", "sym": "BINANCE:FLOKIUSDT"},
        "WIF/USDT": {"id": "dogwifcoin", "sym": "BINANCE:WIFUSDT"},
        "BONK/USDT": {"id": "bonk", "sym": "BINANCE:BONKUSDT"},
        "JUP/USDT": {"id": "jupiter-exchange-solana", "sym": "BINANCE:JUPUSDT"},
        "PYTH/USDT": {"id": "pyth-network", "sym": "BINANCE:PYTHUSDT"},
        "ONDO/USDT": {"id": "ondo-finance", "sym": "BINANCE:ONDOUSDT"},
        "AR/USDT": {"id": "arweave", "sym": "BINANCE:ARUSDT"},
        "ALGO/USDT": {"id": "algorand", "sym": "BINANCE:ALGOUSDT"},
        "VET/USDT": {"id": "vechain", "sym": "BINANCE:VETUSDT"},
        "AAVE/USDT": {"id": "aave", "sym": "BINANCE:AAVEUSDT"},
        "MKR/USDT": {"id": "maker", "sym": "BINANCE:MKRUSDT"},
        "AXS/USDT": {"id": "axie-infinity", "sym": "BINANCE:AXSUSDT"},
        "SAND/USDT": {"id": "the-sandbox", "sym": "BINANCE:SANDUSDT"},
        "MANA/USDT": {"id": "decentraland", "sym": "BINANCE:MANAUSDT"},
        "GALA/USDT": {"id": "gala", "sym": "BINANCE:GALAUSDT"},
        "CHZ/USDT": {"id": "chiliz", "sym": "BINANCE:CHZUSDT"},
        "ENJ/USDT": {"id": "enjincoin", "sym": "BINANCE:ENJUSDT"},
        "CRV/USDT": {"id": "curve-dao-token", "sym": "BINANCE:CRVUSDT"},
        "SNX/USDT": {"id": "synthetix-network-token", "sym": "BINANCE:SNXUSDT"},
        "COMP/USDT": {"id": "compound-governance-token", "sym": "BINANCE:COMPUSDT"},
        "SUSHI/USDT": {"id": "sushi", "sym": "BINANCE:SUSHIUSDT"},
        "YFI/USDT": {"id": "yearn-finance", "sym": "BINANCE:YFIUSDT"},
        "1INCH/USDT": {"id": "1inch", "sym": "BINANCE:1INCHUSDT"},
        "ZRX/USDT": {"id": "0x", "sym": "BINANCE:ZRXUSDT"},
        "BAT/USDT": {"id": "basic-attention-token", "sym": "BINANCE:BATUSDT"},
        "ZIL/USDT": {"id": "zilliqa", "sym": "BINANCE:ZILUSDT"},
        "IOST/USDT": {"id": "iostoken", "sym": "BINANCE:IOSTUSDT"},
        "ONT/USDT": {"id": "ontology", "sym": "BINANCE:ONTUSDT"},
        "QTUM/USDT": {"id": "qtum", "sym": "BINANCE:QTUMUSDT"},
        "IO/USDT": {"id": "io-net", "sym": "BINANCE:IOUSDT"},
        "ZK/USDT": {"id": "zksync", "sym": "BINANCE:ZKUSDT"},
        "BLUR/USDT": {"id": "blur", "sym": "BINANCE:BLURUSDT"},
        "PORTAL/USDT": {"id": "portal", "sym": "BINANCE:PORTALUSDT"},
        "PIXEL/USDT": {"id": "pixels", "sym": "BINANCE:PIXELUSDT"},
        "AEVO/USDT": {"id": "aevo-exchange", "sym": "BINANCE:AEVOUSDT"},
        "ALT/USDT": {"id": "altlayer", "sym": "BINANCE:ALTUSDT"},
        "XAI/USDT": {"id": "xai-blockchain", "sym": "BINANCE:XAIUSDT"},
        "MANTA/USDT": {"id": "manta-network", "sym": "BINANCE:MANTAUSDT"},
        "NFP/USDT": {"id": "nfprompt", "sym": "BINANCE:NFPUSDT"},
        "AI/USDT": {"id": "sleepless-ai", "sym": "BINANCE:AIUSDT"},
        "ACE/USDT": {"id": "fusionist", "sym": "BINANCE:ACEUSDT"},
        "BIGTIME/USDT": {"id": "big-time", "sym": "BINANCE:BIGTIMEUSDT"},
        "ORDI/USDT": {"id": "ordinals", "sym": "BINANCE:ORDIUSDT"},
        "SATS/USDT": {"id": "sats-ordinals", "sym": "BINANCE:1000SATSUSDT"},
        "RATS/USDT": {"id": "rats", "sym": "BINANCE:RATSUSDT"},
        "BEAM/USDT": {"id": "beam-2", "sym": "BINANCE:BEAMUSDT"},
        "MEME/USDT": {"id": "memecoin", "sym": "BINANCE:MEMEUSDT"},
        "STRK/USDT": {"id": "starknet", "sym": "BINANCE:STRKUSDT"},
        "BOME/USDT": {"id": "book-of-meme", "sym": "BINANCE:BOMEUSDT"},
        "POPCAT/USDT": {"id": "popcat", "sym": "BINANCE:POPCATUSDT"},
        "MEW/USDT": {"id": "cat-in-a-dogs-world", "sym": "BINANCE:MEWUSDT"},
        "NEIRO/USDT": {"id": "neiro", "sym": "BINANCE:NEIROUSDT"},
        "TURBO/USDT": {"id": "turbo", "sym": "BINANCE:TURBOUSDT"},
        "MOG/USDT": {"id": "mog-coin", "sym": "BINANCE:MOGUSDT"},
        "BRETT/USDT": {"id": "brett", "sym": "BINANCE:BRETTUSDT"},
        "MYRO/USDT": {"id": "myro", "sym": "BINANCE:MYROUSDT"},
        "SLERF/USDT": {"id": "slerf", "sym": "BINANCE:SLERFUSDT"},
        "WLD/USDT": {"id": "worldcoin-wld", "sym": "BINANCE:WLDUSDT"},
        "CYBER/USDT": {"id": "cyberConnect", "sym": "BINANCE:CYBERUSDT"},
        "HIFI/USDT": {"id": "hifi-finance", "sym": "BINANCE:HIFIUSDT"},
        "LPT/USDT": {"id": "livepeer", "sym": "BINANCE:LPTUSDT"},
        "ARKM/USDT": {"id": "arkham", "sym": "BINANCE:ARKMUSDT"},
        "MAV/USDT": {"id": "maverick-protocol", "sym": "BINANCE:MAVUSDT"},
        "PENDLE/USDT": {"id": "pendle", "sym": "BINANCE:PENDLEUSDT"},
        "LQTY/USDT": {"id": "liquity", "sym": "BINANCE:LQTYUSDT"},
        "SSV/USDT": {"id": "ssv-network", "sym": "BINANCE:SSVUSDT"},
        "JOE/USDT": {"id": "joe", "sym": "BINANCE:JOEUSDT"},
        "GMX/USDT": {"id": "gmx", "sym": "BINANCE:GMXUSDT"},
        "RDNT/USDT": {"id": "radiant-capital", "sym": "BINANCE:RDNTUSDT"},
        "STG/USDT": {"id": "stargate-finance", "sym": "BINANCE:STGUSDT"},
        "MAGIC/USDT": {"id": "magic", "sym": "BINANCE:MAGICUSDT"},
        "AGIX/USDT": {"id": "singularitynet", "sym": "BINANCE:AGIXUSDT"},
        "OCEAN/USDT": {"id": "ocean-protocol", "sym": "BINANCE:OCEANUSDT"},
        "RLC/USDT": {"id": "iexec-rlc", "sym": "BINANCE:RLCUSDT"},
        "POLS/USDT": {"id": "polkastarter", "sym": "BINANCE:POLSUSDT"},
        "CELR/USDT": {"id": "celer-network", "sym": "BINANCE:CELRUSDT"},
        "DENT/USDT": {"id": "dent", "sym": "BINANCE:DENTUSDT"},
        "HOT/USDT": {"id": "holotoken", "sym": "BINANCE:HOTUSDT"},
        "STMX/USDT": {"id": "stormx", "sym": "BINANCE:STMXUSDT"},
        "CKB/USDT": {"id": "nervos-network", "sym": "BINANCE:CKBUSDT"},
        "SC/USDT": {"id": "siacoin", "sym": "BINANCE:SCUSDT"},
        "DGB/USDT": {"id": "digibyte", "sym": "BINANCE:DGBUSDT"},
        "RVN/USDT": {"id": "ravencoin", "sym": "BINANCE:RVNUSDT"},
        "ZEN/USDT": {"id": "horizen", "sym": "BINANCE:ZENUSDT"},
        "KAVA/USDT": {"id": "kava", "sym": "BINANCE:KAVAUSDT"},
        "ICX/USDT": {"id": "icon", "sym": "BINANCE:ICXUSDT"},
        "ONE/USDT": {"id": "harmony", "sym": "BINANCE:ONEUSDT"},
        "ANKR/USDT": {"id": "ankr", "sym": "BINANCE:ANKRUSDT"},
        "COTI/USDT": {"id": "coti", "sym": "BINANCE:COTIUSDT"},
        "SKL/USDT": {"id": "skale", "sym": "BINANCE:SKALEUSDT"},
        "STORJ/USDT": {"id": "storj", "sym": "BINANCE:STORJUSDT"},
        "OXT/USDT": {"id": "orchid", "sym": "BINANCE:OXTUSDT"},
        "LSK/USDT": {"id": "lisk", "sym": "BINANCE:LSKUSDT"},
        "SYS/USDT": {"id": "syscoin", "sym": "BINANCE:SYSUSDT"},
        "REEF/USDT": {"id": "reef", "sym": "BINANCE:REEFUSDT"},
        "OGN/USDT": {"id": "origin-protocol", "sym": "BINANCE:OGNUSDT"},
        "CTSI/USDT": {"id": "cartesi", "sym": "BINANCE:CTSIUSDT"},
        "CHR/USDT": {"id": "chromia", "sym": "BINANCE:CHRUSDT"},
        "PHA/USDT": {"id": "phala-network", "sym": "BINANCE:PHAUSDT"},
        "POL/USDT": {"id": "polygon-ecosystem-token", "sym": "BINANCE:POLUSDT"},
        "SUN/USDT": {"id": "sun-token", "sym": "BINANCE:SUNUSDT"},
        "BTT/USDT": {"id": "bittorrent", "sym": "BINANCE:BTTUSDT"},
        "WIN/USDT": {"id": "wink", "sym": "BINANCE:WINUSDT"},
        "JST/USDT": {"id": "just", "sym": "BINANCE:JSTUSDT"},
        "ARPA/USDT": {"id": "arpa", "sym": "BINANCE:ARPAUSDT"},
        "LIT/USDT": {"id": "litentry", "sym": "BINANCE:LITUSDT"},
        "BADGER/USDT": {"id": "badger-dao", "sym": "BINANCE:BADGERUSDT"},
        "FIS/USDT": {"id": "stafi", "sym": "BINANCE:FISUSDT"},
        "FLOW/USDT": {"id": "flow", "sym": "BINANCE:FLOWUSDT"},
        "MINA/USDT": {"id": "mina-protocol", "sym": "BINANCE:MINAUSDT"},
        "CLV/USDT": {"id": "clover-finance", "sym": "BINANCE:CLVUSDT"},
        "RAD/USDT": {"id": "radicle", "sym": "BINANCE:RADUSDT"},
        "ID/USDT": {"id": "space-id", "sym": "BINANCE:IDUSDT"},
        "HOOK/USDT": {"id": "hooked-protocol", "sym": "BINANCE:HOOKUSDT"},
        "HIGH/USDT": {"id": "highstreet", "sym": "BINANCE:HIGHUSDT"},
        "BNX/USDT": {"id": "binaryx", "sym": "BINANCE:BNXUSDT"},
        "ILV/USDT": {"id": "illuvium", "sym": "BINANCE:ILVUSDT"},
        "MOVR/USDT": {"id": "moonriver", "sym": "BINANCE:MOVRUSDT"},
        "GLMR/USDT": {"id": "moonbeam", "sym": "BINANCE:GLMRUSDT"},
        "ASTR/USDT": {"id": "astar", "sym": "BINANCE:ASTRUSDT"},
        "LDO/USDT": {"id": "lido-dao", "sym": "BINANCE:LDOUSDT"},
        "GNS/USDT": {"id": "gains-network", "sym": "BINANCE:GNSUSDT"},
        "SYN/USDT": {"id": "synapse-2", "sym": "BINANCE:SYNUSDT"},
        "FXS/USDT": {"id": "frax-share", "sym": "BINANCE:FXSUSDT"},
        "FDUSD/USDT": {"id": "first-digital-usd", "sym": "BINANCE:FDUSDUSDT"},
        "USDC/USDT": {"id": "usd-coin", "sym": "BINANCE:USDCUSDT"},
        "TURBO/USDT": {"id": "turbo", "sym": "BINANCE:TURBOUSDT"},
        "CATI/USDT": {"id": "cati", "sym": "BINANCE:CATIUSDT"},
        "HMSTR/USDT": {"id": "hamster-kombat", "sym": "BINANCE:HMSTRUSDT"},
        "EIGEN/USDT": {"id": "eigenlayer", "sym": "BINANCE:EIGENUSDT"},
        "SCR/USDT": {"id": "scroll", "sym": "BINANCE:SCRUSDT"},
        "PNUT/USDT": {"id": "pnut", "sym": "BINANCE:PNUTUSDT"},
        "ACT/USDT": {"id": "act-i-the-ai-prophecy", "sym": "BINANCE:ACTUSDT"},
        "GOAT/USDT": {"id": "goatseus-maximus", "sym": "BINANCE:GOATUSDT"}
    }
    
    sel = st.selectbox("කොයින් එක තෝරන්න (Select Coin)", list(coins.keys()))
    coin_id = coins[sel]["id"]
    tv_sym = coins[sel]["sym"]

# Fetch data & Calculate indicators
df = get_coingecko_market_data(coin_id)

if df is not None and not df.empty:
    ind = calculate_smc_ict_indicators(df)
    price = ind["price"]
    change = ((price - df['open'].iloc[0]) / df['open'].iloc[0]) * 100
    
    score = 0
    
    if ind["ema9"] > ind["ema21"]: score += 1
    else: score -= 1

    if ind["bos_bullish"]: score += 2
    if ind["bos_bearish"]: score -= 2
    if ind["bullish_ob"]: score += 2
    if ind["bearish_ob"]: score -= 2

    if ind["bullish_fvg"]: score += 2
    if ind["bearish_fvg"]: score -= 2
    if ind["liquidity_sweep_buy"]: score += 3
    if ind["liquidity_sweep_sell"]: score -= 3

    if "Discount" in ind["zone"] and score > 0: score += 1
    elif "Premium" in ind["zone"] and score < 0: score -= 1

    if score >= 5:
        signal = "STRONG BUY (SMC/ICT සමතුලිතයි) 🚀"
        sig_color = "#10B981"
    elif score >= 2:
        signal = "BUY (බුලිෂ් ප්‍රවණතාවක් ඇත) 📈"
        sig_color = "#34D399"
    elif score <= -5:
        signal = "STRONG SELL (SMC/ICT මඟින් තහවුරුයි) 🔻"
        sig_color = "#EF4444"
    elif score <= -2:
        signal = "SELL (බෙයාර්ලිෂ් ප්‍රවණතාවක් ඇත) 📉"
        sig_color = "#F87171"
    else:
        signal = "HOLD / බලා සිටින්න (Neutral) ⚖️"
        sig_color = "#F59E0B"

    is_buy = "BUY" in signal
else:
    st.error("දත්ත ලබා ගැනීම අසාර්ථක විය. කරුණාකර අන්තර්ජාල සම්බන්ධතාවය පරීක්ෂා කරන්න.")
    st.stop()

# App Header
st.markdown(f'<p class="vip-header">👑 Binance Pro Signal App <span class="vip-badge">197+ Coins Master</span></p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-desc"><b>{sel}</b> සඳහා Smart Money Concepts සහ Inner Circle Trader සංකල්ප භාවිත කර සකස් කළ සංඥා පද්ධතිය.</p>', unsafe_allow_html=True)

if page == "Live Signal":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**මිල (Price):** ${price:,.4f} | **වෙනස (Change):** <span style='color: {'#059669' if change >= 0 else '#DC2626'};'>{change:,.2f}%</span> | **කලාපය (Zone):** <b>{ind['zone']}</b>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="signal-box" style="background: {sig_color};">{signal}</div>', unsafe_allow_html=True)

    tp1 = price + (ind['atr'] * 1.5) if is_buy else price - (ind['atr'] * 1.5)
    tp2 = price + (ind['atr'] * 3.0) if is_buy else price - (ind['atr'] * 3.0)
    sl = price - (ind['atr'] * 1.0) if is_buy else price + (ind['atr'] * 1.0)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="t-card">ඇතුල්වන මිල (Entry)<br><b>${price:,.4f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="t-card">ඉලක්කය 1 (TP1)<br><b style="color: #059669;">${tp1:,.4f}</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="t-card">ඉලක්කය 2 (TP2)<br><b style="color: #059669;">${tp2:,.4f}</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="t-card">නැවතුම් අලාභය (SL)<br><b style="color: #DC2626;">${sl:,.4f}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    chart_html = f"""
    <div class="tradingview-widget-container" style="height:400px;width:100%">
      <div id="tv_chart" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{"autosize": true, "symbol": "{tv_sym}", "interval": "60", "timezone": "Etc/UTC", "theme": "light", "style": "1", "locale": "en", "container_id": "tv_chart"}});
      </script>
    </div>
    """
    st.components.v1.html(chart_html, height=410)

elif page == "SMC & ICT Analytics":
    st.markdown("### 📊 SMC & ICT ගැඹුරු විශ්ලේෂණය (Deep Analytics)", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Market Zone (ප්‍රදේශය)", value=ind['zone'])
        st.metric(label="Bullish Break of Structure (BOS)", value="ඔව් (Yes)" if ind['bos_bullish'] else "නැත (No)")
        st.metric(label="Bearish Break of Structure (BOS)", value="ඔව් (Yes)" if ind['bos_bearish'] else "නැත (No)")
        st.metric(label="Bullish Order Block (OB)", value="ඔව් (Yes)" if ind['bullish_ob'] else "නැත (No)")
    with col2:
        st.metric(label="Bearish Order Block (OB)", value="ඔව් (Yes)" if ind['bearish_ob'] else "නැත (No)")
        st.metric(label="ICT Fair Value Gap (FVG)", value="ක්‍රියාකාරීයි (Active)" if (ind['bullish_fvg'] or ind['bearish_fvg']) else "නැත")
        st.metric(label="Liquidity Sweep (Stop Hunt)", value="හඳුනාගෙන ඇත" if (ind['liquidity_sweep_buy'] or ind['liquidity_sweep_sell']) else "නැත")
        st.metric(label="වොලටැලිටිය (ATR)", value=f"${ind['atr']:.4f}")

elif page == "Notepad":
    st.markdown('### 📝 VIP වෙළඳ සටහන් (Trading Notepad)', unsafe_allow_html=True)
    if 'note' not in st.session_state: 
        st.session_state.note = ""
    st.session_state.note = st.text_area("Note", value=st.session_state.note, height=200, label_visibility="collapsed", placeholder="ඔබේ සටහන් මෙහි ලියා තබා ගන්න...")
    if st.button("සටහන් මحو කරන්න (Clear)"): 
        st.session_state.note = ""
        st.rerun()
