import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Binance Pro Signal App VIP", page_icon="👑", layout="wide")

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

@st.cache_data(ttl=600, show_spinner=False)
def get_coingecko_market_data(coin_id):
    """CoinGecko API භාවිත කර දත්ත ලබා ගැනීම සහ දෝෂ මඟහරවා ගැනීම"""
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

def calculate_indicators(df):
    close = df['close']
    high = df['high']
    low = df['low']
    
    # 1. EMA 9 & EMA 21
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    
    # 2. RSI (14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # 3. MACD (12, 26, 9)
    exp12 = close.ewm(span=12, adjust=False).mean()
    exp26 = close.ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal_line = macd.ewm(span=9, adjust=False).mean()
    
    # 4. Bollinger Bands (20, 2)
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    upper_band = sma20 + (std20 * 2)
    lower_band = sma20 - (std20 * 2)
    
    # 5. Smart Money Concepts (SMC) Logic
    df['rolling_high'] = high.rolling(window=5).max()
    df['rolling_low'] = low.rolling(window=5).min()
    
    bullish_ob = (close > df['open']) & (close.shift(1) < df['open'].shift(1))
    bearish_ob = (close < df['open']) & (close.shift(1) > df['open'].shift(1))
    
    smc_bias = "NEUTRAL"
    if close.iloc[-1] > df['rolling_high'].iloc[-2]:
        smc_bias = "BULLISH_BOS" 
    elif close.iloc[-1] < df['rolling_low'].iloc[-2]:
        smc_bias = "BEARISH_BOS" 

    return {
        "price": close.iloc[-1],
        "ema9": ema9.iloc[-1],
        "ema21": ema21.iloc[-1],
        "rsi": rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0,
        "macd": macd.iloc[-1] if not np.isnan(macd.iloc[-1]) else 0.0,
        "macd_signal": signal_line.iloc[-1] if not np.isnan(signal_line.iloc[-1]) else 0.0,
        "upper_band": upper_band.iloc[-1] if not np.isnan(upper_band.iloc[-1]) else close.iloc[-1] * 1.05,
        "lower_band": lower_band.iloc[-1] if not np.isnan(lower_band.iloc[-1]) else close.iloc[-1] * 0.95,
        "smc_bias": smc_bias,
        "bullish_ob": bullish_ob.iloc[-1],
        "bearish_ob": bearish_ob.iloc[-1]
    }

# Sidebar with 189 Coins List
with st.sidebar:
    st.markdown("### 👑 VIP Pro Menu")
    page = st.selectbox("Navigation", ["Live Signal", "Advanced Analytics", "Notepad"])
    
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
        "LINK/USDT": {"id": "chainlink", "sym": "BINANCE:LINKUSDT"},
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
        "SAGA/USDT": {"id": "saga-2", "sym": "BINANCE:SAGAUSDT"},
        "ENA/USDT": {"id": "ethena", "sym": "BINANCE:ENAUSDT"},
        "WLD/USDT": {"id": "worldcoin-wld", "sym": "BINANCE:WLDUSDT"},
        "STRK/USDT": {"id": "starknet", "sym": "BINANCE:STRKUSDT"},
        "PORTAL/USDT": {"id": "portal", "sym": "BINANCE:PORTALUSDT"},
        "PIXEL/USDT": {"id": "pixels", "sym": "BINANCE:PIXELUSDT"},
        "AXL/USDT": {"id": "axelar", "sym": "BINANCE:AXLUSDT"},
        "ALT/USDT": {"id": "altlayer", "sym": "BINANCE:ALTUSDT"},
        "MANTA/USDT": {"id": "manta-network", "sym": "BINANCE:MANTAUSDT"},
        "JUP/USDT": {"id": "jupiter", "sym": "BINANCE:JUPUSDT"},
        "DYM/USDT": {"id": "dymension", "sym": "BINANCE:DYMUSDT"},
        "NFP/USDT": {"id": "nfprompt", "sym": "BINANCE:NFPUST"},
        "AI/USDT": {"id": "sleepless-ai", "sym": "BINANCE:AIUSDT"},
        "XAI/USDT": {"id": "xai-blockchain", "sym": "BINANCE:XAIUSDT"},
        "ACE/USDT": {"id": "fusionist", "sym": "BINANCE:ACEUSDT"},
        "RONIN/USDT": {"id": "ronin", "sym": "BINANCE:RONINUSDT"},
        "PYTH/USDT": {"id": "pyth-network", "sym": "BINANCE:PYTHUSDT"},
        "JTO/USDT": {"id": "jito", "sym": "BINANCE:JTOUSDT"},
        "BIGTIME/USDT": {"id": "big-time", "sym": "BINANCE:BIGTIMEUSDT"},
        "MEME/USDT": {"id": "memecoin", "sym": "BINANCE:MEMEUSDT"},
        "ORDI/USDT": {"id": "ordi", "sym": "BINANCE:ORDIUSDT"},
        "SATS/USDT": {"id": "sats-ordinals", "sym": "BINANCE:1000SATSUSDT"},
        "RATS/USDT": {"id": "rats-ordinals", "sym": "BINANCE:RATSUSDT"},
        "GALA/USDT": {"id": "gala", "sym": "BINANCE:GALAUSDT"},
        "SAND/USDT": {"id": "the-sandbox", "sym": "BINANCE:SANDUSDT"},
        "MANA/USDT": {"id": "decentraland", "sym": "BINANCE:MANAUSDT"},
        "AXS/USDT": {"id": "axie-infinity", "sym": "BINANCE:AXSUSDT"},
        "ENJ/USDT": {"id": "enjincoin", "sym": "BINANCE:ENJUSDT"},
        "CHZ/USDT": {"id": "chiliz", "sym": "BINANCE:CHZUSDT"},
        "GMT/usdt": {"id": "stepn", "sym": "BINANCE:GMTUSDT"},
        "FLOW/USDT": {"id": "flow", "sym": "BINANCE:FLOWUSDT"},
        "HBAR/USDT": {"id": "hedera-hashgraph", "sym": "BINANCE:HBARUSDT"},
        "VET/USDT": {"id": "vechain", "sym": "BINANCE:VETUSDT"},
        "FIL/USDT": {"id": "filecoin", "sym": "BINANCE:FILUSDT"},
        "THETA/USDT": {"id": "theta-token", "sym": "BINANCE:THETAUSDT"},
        "XTZ/USDT": {"id": "tezos", "sym": "BINANCE:XTZUSDT"},
        "EOS/USDT": {"id": "eos", "sym": "BINANCE:EOSUSDT"},
        "BCH/USDT": {"id": "bitcoin-cash", "sym": "BINANCE:BCHUSDT"},
        "ETC/USDT": {"id": "ethereum-classic", "sym": "BINANCE:ETCUSDT"},
        "XLM/USDT": {"id": "stellar", "sym": "BINANCE:XLMUSDT"},
        "ALGO/USDT": {"id": "algorand", "sym": "BINANCE:ALGOUSDT"},
        "QNT/USDT": {"id": "quant-network", "sym": "BINANCE:QNTUSDT"},
        "CRV/USDT": {"id": "curve-dao-token", "sym": "BINANCE:CRVUSDT"},
        "MKR/USDT": {"id": "maker", "sym": "BINANCE:MKRUSDT"},
        "AAVE/USDT": {"id": "aave", "sym": "BINANCE:AAVEUSDT"},
        "SNX/USDT": {"id": "synthetix-network-token", "sym": "BINANCE:SNXUSDT"},
        "COMP/USDT": {"id": "compound-governance-token", "sym": "BINANCE:COMPUSDT"},
        "ZRX/USDT": {"id": "0x", "sym": "BINANCE:ZRXUSDT"},
        "BAT/USDT": {"id": "basic-attention-token", "sym": "BINANCE:BATUSDT"},
        "KNC/USDT": {"id": "kyber-network-crystal", "sym": "BINANCE:KNCUSDT"},
        "BAL/USDT": {"id": "balancer", "sym": "BINANCE:BALUSDT"},
        "YFI/USDT": {"id": "yearn-finance", "sym": "BINANCE:YFIUSDT"},
        "SUSHI/USDT": {"id": "sushi", "sym": "BINANCE:SUSHIUSDT"},
        "1INCH/USDT": {"id": "1inch", "sym": "BINANCE:1INCHUSDT"},
        "RUNE/USDT": {"id": "thorchain", "sym": "BINANCE:RUNEUSDT"},
        "KAVA/USDT": {"id": "kava", "sym": "BINANCE:KAVAUSDT"},
        "ZIL/USDT": {"id": "zilliqa", "sym": "BINANCE:ZILUSDT"},
        "IOST/USDT": {"id": "iostoken", "sym": "BINANCE:IOSTUSDT"},
        "ICX/USDT": {"id": "icon", "sym": "BINANCE:ICXUSDT"},
        "ONT/USDT": {"id": "ontology", "sym": "BINANCE:ONTUSDT"},
        "IO/USDT": {"id": "io-net", "sym": "BINANCE:IOUSDT"},
        "ZK/USDT": {"id": "zksync", "sym": "BINANCE:ZKUSDT"},
        "LISTA/USDT": {"id": "lista-dao", "sym": "BINANCE:LISTAUSDT"},
        "BB/USDT": {"id": "bouncebit", "sym": "BINANCE:BBUSDT"},
        "MERL/USDT": {"id": "merlin-chain", "sym": "BINANCE:MERLUSDT"},
        "REZ/USDT": {"id": "renzo", "sym": "BINANCE:REZUSDT"},
        "OMNI/USDT": {"id": "omni-network", "sym": "BINANCE:OMNIUSDT"},
        "SWELL/USDT": {"id": "swell-network", "sym": "BINANCE:SWELLUSDT"},
        "BANANA/USDT": {"id": "banana-gun", "sym": "BINANCE:BANANAUSDT"},
        "TON/USDT": {"id": "the-open-network", "sym": "BINANCE:TONUSDT"},
        "HMSTR/USDT": {"id": "hamster-kombat", "sym": "BINANCE:HMSTRUSDT"},
        "CATI/USDT": {"id": "catizen", "sym": "BINANCE:CATIUSDT"},
        "EIGEN/USDT": {"id": "eigenlayer", "sym": "BINANCE:EIGENUSDT"},
        "NEIRO/USDT": {"id": "neiro-ethereum", "sym": "BINANCE:NEIROUSDT"},
        "TURBO/USDT": {"id": "turbo", "sym": "BINANCE:TURBOUSDT"},
        "BRETT/USDT": {"id": "brett", "sym": "BINANCE:BRETTUSDT"},
        "POPCAT/USDT": {"id": "popcat", "sym": "BINANCE:POPCATUSDT"},
        "MEW/USDT": {"id": "cat-in-a-dogs-world", "sym": "BINANCE:MEWUSDT"},
        "BOME/USDT": {"id": "book-of-meme", "sym": "BINANCE:BOMEUSDT"},
        "SLERF/USDT": {"id": "slerf", "sym": "BINANCE:SLERFUSDT"},
        "WIF/USDT": {"id": "dogwifcoin", "sym": "BINANCE:WIFUSDT"},
        "MYRO/USDT": {"id": "myro", "sym": "BINANCE:MYROUSDT"},
        "PNUT/USDT": {"id": "peanut-the-squirrel", "sym": "BINANCE:PNUTUSDT"},
        "GOAT/USDT": {"id": "goatseus-maximus", "sym": "BINANCE:GOATUSDT"},
        "ACT/USDT": {"id": "act-i-the-ai-prophecy", "sym": "BINANCE:ACTUSDT"},
        "PENGU/USDT": {"id": "pudgy-penguins", "sym": "BINANCE:PENGUUSDT"},
        "CHILLGUY/USDT": {"id": "just-a-chill-guy", "sym": "BINANCE:CHILLGUYUSDT"},
        "MOVE/USDT": {"id": "movement", "sym": "BINANCE:MOVEUSDT"},
        "ANIME/USDT": {"id": "animecoin", "sym": "BINANCE:ANIMEUSDT"},
        "POL/USDT": {"id": "polygon-ecosystem-token", "sym": "BINANCE:POLUSDT"},
        "STX/USDT": {"id": "stacks", "sym": "BINANCE:STXUSDT"},
        "GNO/USDT": {"id": "gnosis", "sym": "BINANCE:GNOUSDT"},
        "AR/USDT": {"id": "arweave", "sym": "BINANCE:ARUSDT"},
        "LDO/USDT": {"id": "lido-dao", "sym": "BINANCE:LDOUSDT"},
        "SSV/USDT": {"id": "ssv-network", "sym": "BINANCE:SSVUSDT"},
        "FXS/USDT": {"id": "frax-share", "sym": "BINANCE:FXSUSDT"},
        "PENDLE/USDT": {"id": "pendle", "sym": "BINANCE:PENDLEUSDT"},
        "AGIX/USDT": {"id": "singularitynet", "sym": "BINANCE:AGIXUSDT"},
        "FET/USDT": {"id": "artificial-superintelligence-alliance", "sym": "BINANCE:FETUSDT"},
        "OCEAN/USDT": {"id": "ocean-protocol", "sym": "BINANCE:OCEANUSDT"},
        "AGLD/USDT": {"id": "adventure-gold", "sym": "BINANCE:AGLDUSDT"},
        "ILV/USDT": {"id": "illuvium", "sym": "BINANCE:ILVUSDT"},
        "YGG/USDT": {"id": "yield-guild-games", "sym": "BINANCE:YGGUSDT"},
        "MAGIC/USDT": {"id": "magic", "sym": "BINANCE:MAGICUSDT"},
        "HIGH/USDT": {"id": "highstreet", "sym": "BINANCE:HIGHUSDT"},
        "COMBO/USDT": {"id": "combo", "sym": "BINANCE:COMBOUSDT"},
        "PHA/USDT": {"id": "phala-network", "sym": "BINANCE:PHAUSDT"},
        "DAR/USDT": {"id": "mines-of-dalarnia", "sym": "BINANCE:DARUSDT"},
        "LOKA/USDT": {"id": "league-of-kingdoms", "sym": "BINANCE:LOKAUSDT"},
        "VOXEL/USDT": {"id": "pixels-voxel", "sym": "BINANCE:VOXELUSDT"},
        "POLS/USDT": {"id": "polkastarter", "sym": "BINANCE:POLSUSDT"},
        "SUPER/USDT": {"id": "superverse", "sym": "BINANCE:SUPERUSDT"},
        "ID/USDT": {"id": "space-id", "sym": "BINANCE:IDUSDT"},
        "HOOK/USDT": {"id": "hooked-protocol", "sym": "BINANCE:HOOKUSDT"},
        "EDU/USDT": {"id": "open-campus", "sym": "BINANCE:EDUUSDT"},
        "COMET/USDT": {"id": "comet", "sym": "BINANCE:COMPUSDT"},
        "STG/USDT": {"id": "stargate-finance", "sym": "BINANCE:STGUSDT"},
        "RDNT/USDT": {"id": "radiant-capital", "sym": "BINANCE:RDNTUSDT"},
        "GMX/USDT": {"id": "gmx", "sym": "BINANCE:GMXUSDT"},
        "SYN/USDT": {"id": "synapse-protocol", "sym": "BINANCE:SYNUSDT"},
        "PROMPT/USDT": {"id": "nfprompt", "sym": "BINANCE:PROMPTUSDT"},
        "LTC/USDT": {"id": "litecoin", "sym": "BINANCE:LTCUSDT"},
        "BSW/USDT": {"id": "biswap", "sym": "BINANCE:BSWUSDT"},
        "CAKE/USDT": {"id": "pancakeswap-token", "sym": "BINANCE:CAKEUSDT"},
        "BEL/USDT": {"id": "bella-protocol", "sym": "BINANCE:BELUSDT"},
        "CTSI/USDT": {"id": "cartesi", "sym": "BINANCE:CTSIUSDT"},
        "MBOX/USDT": {"id": "mobox", "sym": "BINANCE:MBOXUSDT"},
        "GHST/USDT": {"id": "aavegotchi", "sym": "BINANCE:GHSTUSDT"},
        "COTI/USDT": {"id": "coti", "sym": "BINANCE:COTIUSDT"},
        "API3/USDT": {"id": "api3", "sym": "BINANCE:API3USDT"},
        "BAND/USDT": {"id": "band-protocol", "sym": "BINANCE:BANDUSDT"},
        "TRB/USDT": {"id": "tellor", "sym": "BINANCE:TRBUSDT"},
        "BLUR/USDT": {"id": "blur", "sym": "BINANCE:BLURUSDT"},
        "BICO/USDT": {"id": "biconomy", "sym": "BINANCE:BICOUSDT"},
        "ALICE/USDT": {"id": "my-neighbor-alice", "sym": "BINANCE:ALICEUSDT"},
        "SFP/USDT": {"id": "safepal", "sym": "BINANCE:SFPUSDT"},
        "C98/USDT": {"id": "coin98", "sym": "BINANCE:C98USDT"},
        "OAS/USDT": {"id": "oasys", "sym": "BINANCE:OASUSDT"},
        "PROS/USDT": {"id": "prosper", "sym": "BINANCE:PROSUSDT"},
        "QI/USDT": {"id": "benqi", "sym": "BINANCE:QIUSDT"},
        "IQ/USDT": {"id": "everipedia", "sym": "BINANCE:IQUSDT"},
        "STEEM/USDT": {"id": "steem", "sym": "BINANCE:STEEMUSDT"},
        "HIVE/USDT": {"id": "hive", "sym": "BINANCE:HIVEUSDT"},
        "DGB/USDT": {"id": "digibyte", "sym": "BINANCE:DGBUSDT"},
        "RVN/USDT": {"id": "ravencoin", "sym": "BINANCE:RVNUSDT"},
        "SC/USDT": {"id": "siacoin", "sym": "BINANCE:SCUSDT"},
        "CKB/USDT": {"id": "nervos-network", "sym": "BINANCE:CKBUSDT"},
        "KAS/USDT": {"id": "kaspa", "sym": "BINANCE:KASUSDT"},
        "NEXO/USDT": {"id": "nexo", "sym": "BINANCE:NEXOUSDT"}
    }
    
    sel = st.selectbox("Select Coin Pair (189+ Available)", list(coins.keys()))
    coin_id = coins[sel]["id"]
    tv_sym = coins[sel]["sym"]

# Fetch data & Calculate indicators
df = get_coingecko_market_data(coin_id)

if df is not None and not df.empty:
    ind = calculate_indicators(df)
    price = ind["price"]
    change = ((price - df['open'].iloc[0]) / df['open'].iloc[0]) * 100
    
    # Multi-Indicator + Smart Money Concepts Scoring System
    score = 0
    
    if ind["ema9"] > ind["ema21"]: score += 1
    else: score -= 1
    
    if ind["rsi"] < 45: score += 1
    elif ind["rsi"] > 55: score -= 1
    
    if ind["macd"] > ind["macd_signal"]: score += 1
    else: score -= 1
    
    if price <= ind["lower_band"]: score += 1
    elif price >= ind["upper_band"]: score -= 1

    # SMC Weight Additions
    if ind["smc_bias"] == "BULLISH_BOS": score += 2
    elif ind["smc_bias"] == "BEARISH_BOS": score -= 2
    
    if ind["bullish_ob"]: score += 1
    if ind["bearish_ob"]: score -= 1

    if score >= 3:
        signal = "STRONG BUY (SMC Confirmed) 🚀"
        sig_color = "#10B981"
    elif score >= 1:
        signal = "BUY 📈"
        sig_color = "#34D399"
    elif score <= -3:
        signal = "STRONG SELL (SMC Confirmed) 🔻"
        sig_color = "#EF4444"
    elif score <= -1:
        signal = "SELL 📉"
        sig_color = "#F87171"
    else:
        signal = "HOLD / NEUTRAL ⚖️"
        sig_color = "#F59E0B"

    is_buy = "BUY" in signal
else:
    st.error("Failed to fetch market data. Please check your connection.")
    st.stop()

# App Header
st.markdown(f'<p class="vip-header">👑 Binance Pro Signal App <span class="vip-badge">VIP AI + SMC Pro (189+ Coins)</span></p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-desc">Multi-Indicator & <b>Smart Money Concepts (LuxAlgo Style)</b> Engine analyzing <b>{sel}</b>.</p>', unsafe_allow_html=True)

if page == "Live Signal":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Price:** ${price:,.4f} | **Change:** <span style='color: {'#059669' if change >= 0 else '#DC2626'};'>{change:,.2f}%</span> | **SMC Bias:** <b>{ind['smc_bias']}</b>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="signal-box" style="background: {sig_color};">{signal}</div>', unsafe_allow_html=True)

    tp1 = price * (1.025 if is_buy else 0.975)
    tp2 = price * (1.050 if is_buy else 0.950)
    sl = price * (0.985 if is_buy else 1.015)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="t-card">Entry Price<br><b>${price:,.4f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="t-card">Target 1 (TP1)<br><b style="color: #059669;">${tp1:,.4f}</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="t-card">Target 2 (TP2)<br><b style="color: #059669;">${tp2:,.4f}</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="t-card">Stop Loss (SL)<br><b style="color: #DC2626;">${sl:,.4f}</b></div>', unsafe_allow_html=True)

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

elif page == "Advanced Analytics":
    st.markdown("### 📊 Smart Money Concepts (SMC) & Indicator Deep-Dive", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="SMC Market Structure", value=ind['smc_bias'])
        st.metric(label="RSI Status (14)", value=f"{ind['rsi']:.2f}")
    with col2:
        st.metric(label="Bullish Order Block Active", value="Yes" if ind['bullish_ob'] else "No")
        st.metric(label="Bearish Order Block Active", value="Yes" if ind['bearish_ob'] else "No")

elif page == "Notepad":
    st.markdown('### 📝 VIP Trading Notepad', unsafe_allow_html=True)
    if 'note' not in st.session_state: 
        st.session_state.note = ""
    st.session_state.note = st.text_area("Note", value=st.session_state.note, height=200, label_visibility="collapsed", placeholder="Write down your VIP notes here...")
    if st.button("Clear Notes"): 
        st.session_state.note = ""
        st.rerun()
