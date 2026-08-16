import streamlit as st
import requests
from streamlit_cookies_controller import CookieController

# 1. Page Configuration
st.set_page_config(page_title="Binance Pro Signal Center", page_icon="⚡", layout="centered")

# 2. Cookie Controller setup
controller = CookieController()

# 3. Activation Logic
VALID_KEYS = ["KEY-USER1-8899", "KEY-USER2-7711", "KEY-VIP-TRADER", "MY-SECRET-PASS"]

if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False

# Cookie එක පරීක්ෂා කිරීම
saved_key = controller.get("app_activation_key")
if saved_key in VALID_KEYS:
    st.session_state["is_authenticated"] = True

if not st.session_state["is_authenticated"]:
    st.markdown("<h2 style='text-align: center; color: #F0B90B;'>🔐 APP ACTIVATION REQUIRED</h2>", unsafe_allow_html=True)
    user_key = st.text_input("Activation Key එක ඇතුළත් කරන්න:", type="password")
    if st.button("Activate & Lock Access 🔓"):
        if user_key.strip() in VALID_KEYS:
            controller.set("app_activation_key", user_key.strip(), max_age=31536000)
            st.session_state["is_authenticated"] = True
            st.rerun()
        else:
            st.error("වැරදි Key එකකි!")
    st.stop()

# 4. App Content (Logged In)
with st.sidebar:
    if st.button("Logout 🚪"):
        controller.remove("app_activation_key")
        st.session_state["is_authenticated"] = False
        st.rerun()

# 5. Main Logic
if "tp1_pct" not in st.session_state: st.session_state["tp1_pct"] = 2.0
if "tp2_pct" not in st.session_state: st.session_state["tp2_pct"] = 4.0
if "sl_pct" not in st.session_state: st.session_state["sl_pct"] = 2.0
if "timeframe" not in st.session_state: st.session_state["timeframe"] = "15"

def fetch_live_market_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            return float(data["lastPrice"]), float(data["priceChangePercent"]), float(data["highPrice"]), float(data["lowPrice"])
    except:
        return 0.0, 0.0, 0.0, 0.0

# UI
st.title("BINANCE PRO SIGNAL CENTER")
popular_coins = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]
selected_pair = st.selectbox("Coin Pair එක තෝරන්න:", popular_coins)
tv_symbol = selected_pair.replace("/", "")

current_price, pct, high, low = fetch_live_market_data(tv_symbol)
st.metric(label="Current Price", value=f"${current_price:,.2f}", delta=f"{pct}%")
