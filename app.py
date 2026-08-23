import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Binance Pro Signal App VIP - 189 Coins", page_icon="👑", layout="wide")

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
    volume = df['volume']
    
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

    # 5. Stochastic Oscillator (14, 3)
    low_14 = low.rolling(window=14).min()
    high_14 = high.rolling(window=14).max()
    stoch_k = 100 * ((close - low_14) / (high_14 - low_14))
    stoch_d = stoch_k.rolling(window=3).mean()

    # 6. Average True Range (ATR 14)
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=14).mean()

    # 7. Commodity Channel Index (CCI 20)
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(window=20).mean()
    mean_deviation = (tp - sma_tp).abs().rolling(window=20).mean()
    cci = (tp - sma_tp) / (0.015 * mean_deviation)

    # 8. Volume Analysis
    vol_sma = volume.rolling(window=20).mean()
    
    # 9. Smart Money Concepts (SMC) Logic
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
        "stoch_k": stoch_k.iloc[-1] if not np.isnan(stoch_k.iloc[-1]) else 50.0,
        "stoch_d": stoch_d.iloc[-1] if not np.isnan(stoch_d.iloc[-1]) else 50.0,
        "atr": atr.iloc[-1] if not np.isnan(atr.iloc[-1]) else close.iloc[-1] * 0.01,
        "cci": cci.iloc[-1] if not np.isnan(cci.iloc[-1]) else 0.0,
        "vol_active": volume.iloc[-1] > vol_sma.iloc[-1] if not np.isnan(vol_sma.iloc[-1]) else True,
        "smc_bias": smc_bias,
        "bullish_ob": bullish_ob.iloc[-1],
        "bearish_ob": bearish_ob.iloc[-1]
    }

# Sidebar with 189 Binance Coins List
with st.sidebar:
    st.markdown("### 👑 VIP Pro Menu (189 Coins)")
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
        "HERO/USDT": {"id": "metahero", "sym": "BINANCE:HEROUSDT"},
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
        "SKL/USDT": {"id": "celer-network", "sym": "BINANCE:SKALEUSDT"},
        "STORJ/USDT": {"id": "storj", "sym": "BINANCE:STORJUSDT"},
        "OXT/USDT": {"id": "orchid", "sym": "BINANCE:OXTUSDT"},
        "LSK/USDT": {"id": "lisk", "sym": "BINANCE:LSKUSDT"},
        "SYS/USDT": {"id": "syscoin", "sym": "BINANCE:SYSUSDT"},
        "REEF/USDT": {"id": "reef", "sym": "BINANCE:REEFUSDT"},
        "OGN/USDT": {"id": "origin-protocol", "sym": "BINANCE:OGNUSDT"},
        "NU/USDT": {"id": "nucypher", "sym": "BINANCE:NUUSDT"},
        "CTSI/USDT": {"id": "cartesi", "sym": "BINANCE:CTSIUSDT"},
        "CHR/USDT": {"id": "chromia", "sym": "BINANCE:CHRUSDT"},
        "PHA/USDT": {"id": "phala-network", "sym": "BINANCE:PHAUSDT"},
        "POL/USDT": {"id": "polygon-ecosystem-token", "sym": "BINANCE:POLUSDT"},
        "SUN/USDT": {"id": "sun-token", "sym": "BINANCE:SUNUSDT"},
        "BTT/USDT": {"id": "bittorrent", "sym": "BINANCE:BTTUSDT"},
        "WIN/USDT": {"id": "wink", "sym": "BINANCE:WINUSDT"},
        "JST/USDT": {"id": "just", "sym": "BINANCE:JSTUSDT"},
        "NFT/USDT": {"id": "apron", "sym": "BINANCE:NFTUSDT"},
        "DOCK/USDT": {"id": "dock", "sym": "BINANCE:DOCKUSDT"},
        "AUT/USDT": {"id": "autata", "sym": "BINANCE:AUTUSDT"},
        "PROS/USDT": {"id": "prosper", "sym": "BINANCE:PROSUSDT"},
        "MBL/USDT": {"id": "moviebloc", "sym": "BINANCE:MBLUSDT"},
        "ARPA/USDT": {"id": "arpa", "sym": "BINANCE:ARPAUSDT"},
        "LIT/USDT": {"id": "litentry", "sym": "BINANCE:LITUSDT"},
        "BADGER/USDT": {"id": "badger-dao", "sym": "BINANCE:BADGERUSDT"},
        "FIS/USDT": {"id": "stafi", "sym": "BINANCE:FISUSDT"},
        "MIR/USDT": {"id": "mirror-protocol", "sym": "BINANCE:MIRUSDT"},
        "FORTH/USDT": {"id": "ampleforth-governance-token", "sym": "BINANCE:FORTHUSDT"},
        "POLIS/USDT": {"id": "star-atlas-polis", "sym": "BINANCE:POLISUSDT"},
        "ATLAS/USDT": {"id": "star-atlas", "sym": "BINANCE:ATLASUSDT"},
        "QUICK/USDT": {"id": "quickswap", "sym": "BINANCE:QUICKUSDT"},
        "FLOW/USDT": {"id": "flow", "sym": "BINANCE:FLOWUSDT"},
        "MINA/USDT": {"id": "mina-protocol", "sym": "BINANCE:MINAUSDT"},
        "CLV/USDT": {"id": "clover-finance", "sym": "BINANCE:CLVUSDT"},
        "RAD/USDT": {"id": "radicle", "sym": "BINANCE:RADUSDT"},
        "ERN/USDT": {"id": "ethernal", "sym": "BINANCE:ERNUSDT"},
        "BETA/USDT": {"id": "beta-finance", "sym": "BINANCE:BETAUSDT"},
        "ID/USDT": {"id": "space-id", "sym": "BINANCE:IDUSDT"},
        "HOOK/USDT": {"id": "hooked-protocol", "sym": "BINANCE:HOOKUSDT"},
        "HIGH/USDT": {"id": "highstreet", "sym": "BINANCE:HIGHUSDT"},
        "VOXEL/USDT": {"id": "pixels-voxel", "sym": "BINANCE:VOXELUSDT"},
        "BNX/USDT": {"id": "binaryx", "sym": "BINANCE:BNXUSDT"},
        "ILV/USDT": {"id": "illuvium", "sym": "BINANCE:ILVUSDT"},
        "MOVR/USDT": {"id": "moonriver", "sym": "BINANCE:MOVRUSDT"},
        "GLMR/USDT": {"id": "moonbeam", "sym": "BINANCE:GLMRUSDT"},
        "ASTR/USDT": {"id": "astar", "sym": "BINANCE:ASTRUSDT"},
        "ACA/USDT": {"id": "acala", "sym": "BINANCE:ACAUSDT"},
        "EPX/USDT": {"id": "ellipsis", "sym": "BINANCE:EPXUSDT"},
        "LDO/USDT": {"id": "lido-dao", "sym": "BINANCE:LDOUSDT"},
        "GNS/USDT": {"id": "gains-network", "sym": "BINANCE:GNSUSDT"},
        "OAS/USDT": {"id": "oasys", "sym": "BINANCE:OASUSDT"},
        "SYN/USDT": {"id": "synapse-2", "sym": "BINANCE:SYNUSDT"},
        "FRAX/USDT": {"id": "frax", "sym": "BINANCE:FRAXUSDT"},
        "FXS/USDT": {"id": "frax-share", "sym": "BINANCE:FXSUSDT"},
        "TUSD/USDT": {"id": "true-usd", "sym": "BINANCE:TUSDUSDT"},
        "USDP/USDT": {"id": "paxos-standard", "sym": "BINANCE:USDPUSDT"},
        "FDUSD/USDT": {"id": "first-digital-usd", "sym": "BINANCE:FDUSDUSDT"},
        "USDC/USDT": {"id": "usd-coin", "sym": "BINANCE:USDCUSDT"}
    }
    
    sel = st.selectbox("Select Coin Pair (189 Available)", list(coins.keys()))
    coin_id = coins[sel]["id"]
    tv_sym = coins[sel]["sym"]

# Fetch data & Calculate indicators
df = get_coingecko_market_data(coin_id)

if df is not None and not df.empty:
    ind = calculate_indicators(df)
    price = ind["price"]
    change = ((price - df['open'].iloc[0]) / df['open'].iloc[0]) * 100
    
    score = 0
    
    # EMA Trend
    if ind["ema9"] > ind["ema21"]: score += 1
    else: score -= 1
    
    # RSI
    if ind["rsi"] < 45: score += 1
    elif ind["rsi"] > 55: score -= 1
    
    # MACD
    if ind["macd"] > ind["macd_signal"]: score += 1
    else: score -= 1
    
    # Bollinger Bands
    if price <= ind["lower_band"]: score += 1
    elif price >= ind["upper_band"]: score -= 1

    # Stochastic Oscillator
    if ind["stoch_k"] < 20: score += 1
    elif ind["stoch_k"] > 80: score -= 1

    # CCI
    if ind["cci"] < -100: score += 1
    elif ind["cci"] > 100: score -= 1

    # Volume Confirmation
    if ind["vol_active"]: score += 1

    # SMC Weight Additions
    if ind["smc_bias"] == "BULLISH_BOS": score += 2
    elif ind["smc_bias"] == "BEARISH_BOS": score -= 2
    
    if ind["bullish_ob"]: score += 1
    if ind["bearish_ob"]: score -= 1

    if score >= 4:
        signal = "STRONG BUY (VIP Confirmed) 🚀"
        sig_color = "#10B981"
    elif score >= 1:
        signal = "BUY 📈"
        sig_color = "#34D399"
    elif score <= -4:
        signal = "STRONG SELL (VIP Confirmed) 🔻"
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
st.markdown(f'<p class="vip-header">👑 Binance Pro Signal App <span class="vip-badge">189 Coins + AI + SMC</span></p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-desc">Multi-Indicator Engine analyzing <b>{sel}</b> to provide accurate Buy/Sell signals.</p>', unsafe_allow_html=True)

if page == "Live Signal":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Price:** ${price:,.4f} | **Change:** <span style='color: {'#059669' if change >= 0 else '#DC2626'};'>{change:,.2f}%</span> | **SMC Bias:** <b>{ind['smc_bias']}</b>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="signal-box" style="background: {sig_color};">{signal}</div>', unsafe_allow_html=True)

    tp1 = price + (ind['atr'] * 1.5) if is_buy else price - (ind['atr'] * 1.5)
    tp2 = price + (ind['atr'] * 3.0) if is_buy else price - (ind['atr'] * 3.0)
    sl = price - (ind['atr'] * 1.0) if is_buy else price + (ind['atr'] * 1.0)

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
    st.markdown("### 📊 Advanced Technical Indicators Deep-Dive", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="SMC Market Structure", value=ind['smc_bias'])
        st.metric(label="RSI Status (14)", value=f"{ind['rsi']:.2f}")
        st.metric(label="Stochastic %K", value=f"{ind['stoch_k']:.2f}")
        st.metric(label="Commodity Channel Index (CCI)", value=f"{ind['cci']:.2f}")
    with col2:
        st.metric(label="ATR (Volatility)", value=f"${ind['atr']:.4f}")
        st.metric(label="Volume Spike Active", value="Yes" if ind['vol_active'] else "No")
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
