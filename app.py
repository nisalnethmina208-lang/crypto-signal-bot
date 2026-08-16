
import html
import math
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NISAL BINANCE SIGNALS",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# CONFIG
# -----------------------------
BINANCE_BASE = "https://api.binance.com"
DEFAULT_KEYS = ["KEY-USER1-8899", "KEY-USER2-5544", "VIP-SIGNAL-2026"]

# For a public deployment, move these keys to Streamlit Secrets.
try:
    SECRET_KEYS = list(st.secrets.get("ACCESS_KEYS", DEFAULT_KEYS))
except Exception:
    SECRET_KEYS = DEFAULT_KEYS

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# -----------------------------
# GLOBAL MOBILE-FIRST CSS
# -----------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #171a21 0%, #0b0d10 45%, #070809 100%);
}
[data-testid="stHeader"] { background: transparent; }
.block-container {
    max-width: 1180px;
    padding: 1rem 1rem 3rem 1rem;
}
.hero {
    background: linear-gradient(135deg, #181c24, #0d0f13);
    border: 1px solid #2a2f38;
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,.28);
}
.hero h1 { margin: 0; color: #fcd535; font-size: 2rem; }
.hero p { margin: 6px 0 0; color: #aeb4bf; }
.signal-card {
    background: linear-gradient(145deg, #151922, #0d0f14);
    border: 1px solid #292e38;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 12px 30px rgba(0,0,0,.25);
}
.badge-buy, .badge-sell, .badge-wait {
    display:inline-block; padding:8px 16px; border-radius:999px;
    font-weight:800; font-size:.95rem;
}
.badge-buy { background:#0ecb81; color:#06150f; }
.badge-sell { background:#f6465d; color:#fff; }
.badge-wait { background:#f0b90b; color:#17120a; }
.stat {
    background:#10131a; border:1px solid #272c35; border-radius:14px;
    padding:13px; min-height:76px;
}
.stat .label { color:#8d95a3; font-size:.75rem; text-transform:uppercase; }
.stat .value { color:#fff; font-size:1.1rem; font-weight:800; margin-top:5px; }
.level {
    text-align:center; padding:12px; border-radius:14px; background:#10131a;
    border:1px solid #272c35;
}
.level.tp { border-color:#0ecb81; }
.level.sl { border-color:#f6465d; }
.small { color:#8d95a3; font-size:.82rem; }
.conf {
    font-size:2.1rem; font-weight:900; color:#fcd535; line-height:1;
}
.disclaimer {
    color:#7f8794; font-size:.75rem; margin-top:14px;
}
@media (max-width: 700px) {
    .block-container { padding: .6rem .65rem 2rem .65rem; }
    .hero { padding:16px; border-radius:17px; }
    .hero h1 { font-size:1.45rem; }
    .signal-card { padding:14px; border-radius:16px; }
    h2 { font-size:1.15rem !important; }
    .stButton button { min-height:46px; border-radius:12px; }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPERS
# -----------------------------
def fmt_price(x):
    if x is None or not math.isfinite(float(x)):
        return "$0.00"
    x = float(x)
    if x >= 1000:
        return f"${x:,.2f}"
    if x >= 1:
        return f"${x:,.4f}"
    if x >= 0.01:
        return f"${x:,.5f}"
    return f"${x:,.8f}"

@st.cache_data(ttl=20, show_spinner=False)
def get_json(path, params=None):
    r = requests.get(BINANCE_BASE + path, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=60, show_spinner=False)
def get_symbols():
    data = get_json("/api/v3/exchangeInfo")
    symbols = []
    for s in data.get("symbols", []):
        if s.get("status") == "TRADING" and s.get("quoteAsset") == "USDT":
            symbols.append(s["symbol"])
    return sorted(symbols)

@st.cache_data(ttl=15, show_spinner=False)
def get_market(symbol):
    ticker = get_json("/api/v3/ticker/24hr", {"symbol": symbol})
    return {
        "price": float(ticker["lastPrice"]),
        "change": float(ticker["priceChangePercent"]),
        "high": float(ticker["highPrice"]),
        "low": float(ticker["lowPrice"]),
        "volume": float(ticker["quoteVolume"]),
    }

@st.cache_data(ttl=15, show_spinner=False)
def get_klines(symbol, interval="15m", limit=200):
    rows = get_json("/api/v3/klines", {
        "symbol": symbol, "interval": interval, "limit": limit
    })
    cols = [
        "open_time","open","high","low","close","volume","close_time",
        "quote_volume","trades","taker_buy_base","taker_buy_quote","ignore"
    ]
    df = pd.DataFrame(rows, columns=cols)
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    return df

def indicators(df):
    d = df.copy()

    d["ema9"] = d["close"].ewm(span=9, adjust=False).mean()
    d["ema21"] = d["close"].ewm(span=21, adjust=False).mean()
    d["ema50"] = d["close"].ewm(span=50, adjust=False).mean()

    delta = d["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    d["rsi"] = 100 - (100 / (1 + rs))

    ema12 = d["close"].ewm(span=12, adjust=False).mean()
    ema26 = d["close"].ewm(span=26, adjust=False).mean()
    d["macd"] = ema12 - ema26
    d["macd_signal"] = d["macd"].ewm(span=9, adjust=False).mean()

    prev_close = d["close"].shift(1)
    tr = pd.concat([
        d["high"] - d["low"],
        (d["high"] - prev_close).abs(),
        (d["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    d["atr"] = tr.ewm(span=14, adjust=False).mean()

    return d

def make_signal(df):
    d = indicators(df)
    last = d.iloc[-1]
    price = float(last["close"])
    atr = max(float(last["atr"]), price * 0.002)

    score = 0
    reasons = []

    if last["ema9"] > last["ema21"]:
        score += 1
        reasons.append("EMA 9 > EMA 21")
    else:
        score -= 1
        reasons.append("EMA 9 < EMA 21")

    if last["close"] > last["ema50"]:
        score += 1
        reasons.append("Price above EMA 50")
    else:
        score -= 1
        reasons.append("Price below EMA 50")

    if last["macd"] > last["macd_signal"]:
        score += 1
        reasons.append("MACD bullish")
    else:
        score -= 1
        reasons.append("MACD bearish")

    rsi = float(last["rsi"]) if pd.notna(last["rsi"]) else 50
    if 50 <= rsi <= 70:
        score += 1
        reasons.append("RSI supports bullish momentum")
    elif 30 <= rsi < 50:
        score -= 1
        reasons.append("RSI supports bearish momentum")
    elif rsi > 70:
        reasons.append("RSI is overbought")
    else:
        reasons.append("RSI is oversold")

    if score >= 3:
        side = "BUY"
        confidence = 70 + min(score - 3, 2) * 5
        entry = price
        tp1 = price + atr * 1.0
        tp2 = price + atr * 2.0
        sl = price - atr * 1.0
    elif score <= -3:
        side = "SELL"
        confidence = 70 + min(abs(score) - 3, 2) * 5
        entry = price
        tp1 = price - atr * 1.0
        tp2 = price - atr * 2.0
        sl = price + atr * 1.0
    else:
        side = "WAIT"
        confidence = 50 + abs(score) * 4
        entry = price
        tp1 = price + atr
        tp2 = price + atr * 2
        sl = price - atr

    return {
        "side": side, "confidence": int(min(confidence, 85)),
        "entry": entry, "tp1": tp1, "tp2": tp2, "sl": sl,
        "rsi": rsi, "atr": atr, "score": score, "reasons": reasons
    }

# -----------------------------
# AUTH
# -----------------------------
if not st.session_state.authenticated:
    st.markdown("""
    <div class="hero" style="max-width:620px;margin:8vh auto 0;">
      <h1>📈 NISAL BINANCE SIGNALS</h1>
      <p>Professional mobile-first crypto market dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        key = st.text_input("🔐 Access Key", type="password", placeholder="Enter your access key")
        if st.button("Unlock App", use_container_width=True):
            if key in SECRET_KEYS:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid access key.")
    st.stop()

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class="hero">
  <h1>📈 NISAL BINANCE SIGNALS</h1>
  <p>Live market data • Technical analysis • Mobile friendly</p>
</div>
""", unsafe_allow_html=True)

tab_signal, tab_history, tab_notes, tab_settings = st.tabs(
    ["📊 Signals", "🕘 Analysis", "📝 Notes", "⚙️ Settings"]
)

with tab_signal:
    try:
        symbols = get_symbols()
    except Exception:
        symbols = [
            "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
            "ADAUSDT","DOGEUSDT","AVAXUSDT","TRXUSDT","LINKUSDT"
        ]

    popular = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT"]
    available_popular = [x for x in popular if x in symbols]
    options = available_popular + [x for x in symbols if x not in available_popular]

    c1, c2 = st.columns([2, 1])
    with c1:
        selected_coin = st.selectbox("Trading Pair", options, index=0)
    with c2:
        interval = st.selectbox("Timeframe", ["5m","15m","1h","4h"], index=1)

    refresh = st.button("🔄 Refresh Live Data", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.rerun()

    try:
        market = get_market(selected_coin)
        candles = get_klines(selected_coin, interval)
        sig = make_signal(candles)

        side = sig["side"]
        badge_class = {"BUY":"badge-buy", "SELL":"badge-sell", "WAIT":"badge-wait"}[side]
        emoji = {"BUY":"🟢", "SELL":"🔴", "WAIT":"🟡"}[side]

        st.markdown(f"""
        <div class="signal-card">
          <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;">
            <div>
              <div class="small">{selected_coin} • {interval}</div>
              <h2 style="margin:4px 0;color:white;">{fmt_price(market["price"])}</h2>
              <div class="small">24H {market["change"]:+.2f}%</div>
            </div>
            <div style="text-align:right;">
              <div class="{badge_class}">{emoji} {side}</div>
              <div class="small" style="margin-top:8px;">Confidence</div>
              <div class="conf">{sig["confidence"]}%</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("PRICE", fmt_price(market["price"]))
        m2.metric("24H CHANGE", f'{market["change"]:+.2f}%')
        m3.metric("24H HIGH", fmt_price(market["high"]))
        m4.metric("24H LOW", fmt_price(market["low"]))

        st.write("")
        l1,l2,l3,l4 = st.columns(4)
        l1.markdown(f'<div class="level"><div class="small">ENTRY</div><b>{fmt_price(sig["entry"])}</b></div>', unsafe_allow_html=True)
        l2.markdown(f'<div class="level tp"><div class="small">TP 1</div><b>{fmt_price(sig["tp1"])}</b></div>', unsafe_allow_html=True)
        l3.markdown(f'<div class="level tp"><div class="small">TP 2</div><b>{fmt_price(sig["tp2"])}</b></div>', unsafe_allow_html=True)
        l4.markdown(f'<div class="level sl"><div class="small">STOP LOSS</div><b>{fmt_price(sig["sl"])}</b></div>', unsafe_allow_html=True)

        st.write("")
        r1,r2,r3,r4 = st.columns(4)
        r1.metric("RSI", f'{sig["rsi"]:.1f}')
        r2.metric("EMA 9", fmt_price(float(candles["close"].ewm(span=9, adjust=False).mean().iloc[-1])))
        r3.metric("EMA 21", fmt_price(float(candles["close"].ewm(span=21, adjust=False).mean().iloc[-1])))
        r4.metric("Score", f'{sig["score"]:+d}/4')

        with st.expander("🧠 Why this signal?"):
            for reason in sig["reasons"]:
                st.write("• " + reason)

        tv_symbol = f"BINANCE:{selected_coin}"
        st.components.v1.html(
            f"""
            <div style="width:100%;height:480px;">
              <div class="tradingview-widget-container" style="height:100%;width:100%;">
                <div id="tv_chart" style="height:100%;width:100%;"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                  new TradingView.widget({{
                    "width":"100%","height":"100%",
                    "symbol":"{html.escape(tv_symbol)}",
                    "interval":"{html.escape(interval)}",
                    "timezone":"Asia/Colombo",
                    "theme":"dark","style":"1","locale":"en",
                    "enable_publishing":false,"hide_top_toolbar":false,
                    "allow_symbol_change":true,"container_id":"tv_chart"
                  }});
                </script>
              </div>
            </div>
            """,
            height=490,
        )

        st.markdown(
            '<div class="disclaimer">⚠️ This is an educational technical-analysis signal. '
            'It is not financial advice and does not guarantee profit. Always manage risk.</div>',
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error("Live market data could not be loaded right now.")
        st.caption(str(e))

with tab_history:
    st.subheader("🕘 Current Market Analysis")
    st.info("This version calculates the signal from the selected timeframe using EMA, RSI, MACD and ATR. A persistent signal-history database can be added next.")

with tab_notes:
    st.subheader("📝 Trading Notes")
    note = st.text_area(
        "Write your plan",
        height=260,
        placeholder="Coin, entry idea, risk plan, reminders..."
    )
    if st.button("Save Note", use_container_width=True):
        st.session_state.saved_note = note
        st.success("Note saved for this session.")
    if st.session_state.get("saved_note"):
        st.caption("Saved note")
        st.write(st.session_state.saved_note)

with tab_settings:
    st.subheader("⚙️ Settings")
    st.write("NISAL BINANCE SIGNALS")
    st.caption("Mobile-first Streamlit version")
    if st.button("🔒 Lock App", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
