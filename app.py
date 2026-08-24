import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# ============================================================
# AI NISAL BINANCE VIP PRO V3
# Binance USD-M Futures Market Analysis
# ============================================================

st.set_page_config(
    page_title="AI Nisal Binance VIP Pro V3",
    page_icon="👑",
    layout="wide"
)

BASE_URL = "https://fapi.binance.com"

# ------------------------------------------------------------
# PASSWORD
# ------------------------------------------------------------

APP_PASSWORD = st.secrets.get(
    "APP_PASSWORD",
    "1234Binance@"
)


def check_password():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.markdown(
        """
        <div style="text-align:center;padding:50px 0 20px;">
            <h1>👑 AI NISAL BINANCE</h1>
            <p>VIP PRO Futures Analysis</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    password = st.text_input(
        "VIP Password",
        type="password"
    )

    if st.button(
        "🔐 LOGIN",
        use_container_width=True
    ):

        if password == APP_PASSWORD:

            st.session_state.authenticated = True
            st.rerun()

        else:
            st.error("❌ Incorrect Password")

    return False


if not check_password():
    st.stop()


# ------------------------------------------------------------
# STYLE
# ------------------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color:#F8FAFC;
    }

    .title {
        font-size:30px;
        font-weight:900;
        color:#0F172A;
    }

    .subtitle {
        color:#64748B;
        margin-bottom:15px;
    }

    .signal {
        padding:20px;
        border-radius:16px;
        color:white;
        text-align:center;
        font-size:28px;
        font-weight:900;
    }

    .card {
        background:#FFFFFF;
        border:1px solid #E2E8F0;
        border-radius:14px;
        padding:15px;
        text-align:center;
    }

    .label {
        color:#64748B;
        font-size:12px;
    }

    .value {
        color:#0F172A;
        font-size:20px;
        font-weight:800;
    }

    .good {
        background:#DCFCE7;
        border:1px solid #22C55E;
        padding:12px;
        border-radius:10px;
        color:#166534;
    }

    .warning {
        background:#FEF3C7;
        border:1px solid #F59E0B;
        padding:12px;
        border-radius:10px;
        color:#92400E;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# BINANCE API
# ============================================================

def binance_get(endpoint, params=None):

    try:

        response = requests.get(
            BASE_URL + endpoint,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except Exception:
        return None


# ============================================================
# SYMBOLS
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def get_futures_symbols():

    data = binance_get(
        "/fapi/v1/exchangeInfo"
    )

    if not data:
        return [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "SOLUSDT",
            "XRPUSDT"
        ]

    result = []

    for item in data.get("symbols", []):

        if (
            item.get("status") == "TRADING"
            and item.get("contractType") == "PERPETUAL"
            and item.get("quoteAsset") == "USDT"
        ):
            result.append(item["symbol"])

    return sorted(result)


# ============================================================
# KLINES
# ============================================================

@st.cache_data(ttl=15, show_spinner=False)
def get_klines(
    symbol,
    interval,
    limit=500
):

    data = binance_get(
        "/fapi/v1/klines",
        {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
    )

    if not data:
        return None

    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "trades",
        "taker_buy_volume",
        "taker_buy_quote_volume",
        "ignore"
    ]

    df = pd.DataFrame(
        data,
        columns=columns
    )

    numeric = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_volume",
        "trades",
        "taker_buy_volume",
        "taker_buy_quote_volume"
    ]

    for col in numeric:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df["open_time"] = pd.to_datetime(
        df["open_time"],
        unit="ms"
    )

    return df


# ============================================================
# FUNDING / OI / MARK PRICE
# ============================================================

@st.cache_data(ttl=30, show_spinner=False)
def get_premium_data(symbol):

    data = binance_get(
        "/fapi/v1/premiumIndex",
        {
            "symbol": symbol
        }
    )

    if not data:
        return {
            "mark_price": 0.0,
            "index_price": 0.0,
            "funding": 0.0
        }

    return {
        "mark_price": float(
            data.get("markPrice", 0)
        ),
        "index_price": float(
            data.get("indexPrice", 0)
        ),
        "funding": float(
            data.get("lastFundingRate", 0)
        )
    }


@st.cache_data(ttl=30, show_spinner=False)
def get_open_interest(symbol):

    data = binance_get(
        "/fapi/v1/openInterest",
        {
            "symbol": symbol
        }
    )

    if not data:
        return 0.0

    return float(
        data.get("openInterest", 0)
    )


# ============================================================
# INDICATORS
# ============================================================

def add_indicators(df):

    df = df.copy()

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    # ---------------- EMA ----------------

    df["ema9"] = close.ewm(
        span=9,
        adjust=False
    ).mean()

    df["ema21"] = close.ewm(
        span=21,
        adjust=False
    ).mean()

    df["ema50"] = close.ewm(
        span=50,
        adjust=False
    ).mean()

    df["ema200"] = close.ewm(
        span=200,
        adjust=False
    ).mean()

    # ---------------- RSI ----------------

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / 14,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / 14,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    df["rsi"] = (
        100 -
        (100 / (1 + rs))
    )

    # ---------------- MACD ----------------

    ema12 = close.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False
    ).mean()

    df["macd"] = ema12 - ema26

    df["macd_signal"] = df[
        "macd"
    ].ewm(
        span=9,
        adjust=False
    ).mean()

    df["macd_hist"] = (
        df["macd"] -
        df["macd_signal"]
    )

    # ---------------- Bollinger ----------------

    df["bb_mid"] = close.rolling(
        20
    ).mean()

    std = close.rolling(
        20
    ).std()

    df["bb_upper"] = (
        df["bb_mid"] +
        2 * std
    )

    df["bb_lower"] = (
        df["bb_mid"] -
        2 * std
    )

    # ---------------- ATR ----------------

    tr1 = high - low

    tr2 = (
        high -
        close.shift(1)
    ).abs()

    tr3 = (
        low -
        close.shift(1)
    ).abs()

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    df["atr"] = tr.ewm(
        span=14,
        adjust=False
    ).mean()

    # ---------------- Volume ----------------

    df["volume_ma"] = volume.rolling(
        20
    ).mean()

    df["volume_ratio"] = (
        volume /
        df["volume_ma"].replace(
            0,
            np.nan
        )
    )

    # ---------------- VWAP ----------------

    typical = (
        high +
        low +
        close
    ) / 3

    cumulative_volume = volume.cumsum()

    df["vwap"] = (
        typical *
        volume
    ).cumsum() / cumulative_volume

    # ---------------- ADX ----------------

    up_move = high.diff()

    down_move = -low.diff()

    plus_dm = np.where(
        (up_move > down_move) &
        (up_move > 0),
        up_move,
        0
    )

    minus_dm = np.where(
        (down_move > up_move) &
        (down_move > 0),
        down_move,
        0
    )

    plus_dm = pd.Series(
        plus_dm,
        index=df.index
    )

    minus_dm = pd.Series(
        minus_dm,
        index=df.index
    )

    plus_di = (
        100 *
        plus_dm.ewm(
            span=14,
            adjust=False
        ).mean() /
        df["atr"].replace(
            0,
            np.nan
        )
    )

    minus_di = (
        100 *
        minus_dm.ewm(
            span=14,
            adjust=False
        ).mean() /
        df["atr"].replace(
            0,
            np.nan
        )
    )

    dx = (
        abs(
            plus_di -
            minus_di
        ) /
        (
            plus_di +
            minus_di
        ).replace(
            0,
            np.nan
        )
    ) * 100

    df["adx"] = dx.ewm(
        span=14,
        adjust=False
    ).mean()

    # ========================================================
    # MARKET STRUCTURE
    # ========================================================

    # Previous confirmed swing areas
    df["previous_swing_high"] = (
        high.shift(2)
        .rolling(5)
        .max()
    )

    df["previous_swing_low"] = (
        low.shift(2)
        .rolling(5)
        .min()
    )

    # BOS
    df["bullish_bos"] = (
        close >
        df["previous_swing_high"]
    )

    df["bearish_bos"] = (
        close <
        df["previous_swing_low"]
    )

    # ========================================================
    # LIQUIDITY SWEEPS
    # ========================================================

    df["bullish_liquidity_sweep"] = (
        (low < df["previous_swing_low"]) &
        (close > df["previous_swing_low"])
    )

    df["bearish_liquidity_sweep"] = (
        (high > df["previous_swing_high"]) &
        (close < df["previous_swing_high"])
    )

    # ========================================================
    # ORDER BLOCK PROXY
    # ========================================================

    previous_open = df["open"].shift(1)
    previous_close = df["close"].shift(1)
    previous_high = df["high"].shift(1)
    previous_low = df["low"].shift(1)

    bullish_displacement = (
        (close > high.shift(1)) &
        (close > open) &
        (volume > df["volume_ma"] * 1.2)
    )

    bearish_displacement = (
        (close < low.shift(1)) &
        (close < open) &
        (volume > df["volume_ma"] * 1.2)
    )

    df["bullish_ob_proxy"] = (
        (previous_close < previous_open) &
        bullish_displacement
    )

    df["bearish_ob_proxy"] = (
        (previous_close > previous_open) &
        bearish_displacement
    )

    # ========================================================
    # TREND
    # ========================================================

    df["bull_trend"] = (
        (df["ema9"] > df["ema21"]) &
        (df["ema21"] > df["ema50"]) &
        (df["ema50"] > df["ema200"])
    )

    df["bear_trend"] = (
        (df["ema9"] < df["ema21"]) &
        (df["ema21"] < df["ema50"]) &
        (df["ema50"] < df["ema200"])
    )

    return df


# ============================================================
# SINGLE TIMEFRAME ANALYSIS
# ============================================================

def analyze_timeframe(df):

    if df is None:
        return None

    if len(df) < 250:
        return None

    df = add_indicators(df)

    # Ignore currently forming candle
    x = df.iloc[-2]

    score = 0
    reasons = []

    # ========================================================
    # EMA TREND
    # ========================================================

    if x["ema9"] > x["ema21"]:

        score += 8
        reasons.append("EMA 9 > EMA 21")

    else:

        score -= 8
        reasons.append("EMA 9 < EMA 21")

    if x["ema21"] > x["ema50"]:

        score += 8

    else:

        score -= 8

    if x["ema50"] > x["ema200"]:

        score += 10
        reasons.append("Major trend bullish")

    else:

        score -= 10
        reasons.append("Major trend bearish")

    # ========================================================
    # RSI
    # ========================================================

    rsi = float(x["rsi"])

    if 52 <= rsi <= 68:

        score += 8
        reasons.append("RSI bullish zone")

    elif 32 <= rsi < 48:

        score -= 8
        reasons.append("RSI bearish zone")

    elif rsi > 75:

        score -= 5
        reasons.append("RSI overbought")

    elif rsi < 25:

        score += 5
        reasons.append("RSI oversold")

    # ========================================================
    # MACD
    # ========================================================

    if (
        x["macd"] >
        x["macd_signal"] and
        x["macd_hist"] > 0
    ):

        score += 10
        reasons.append("MACD bullish")

    elif (
        x["macd"] <
        x["macd_signal"] and
        x["macd_hist"] < 0
    ):

        score -= 10
        reasons.append("MACD bearish")

    # ========================================================
    # VWAP
    # ========================================================

    if x["close"] > x["vwap"]:

        score += 6
        reasons.append("Price above VWAP")

    else:

        score -= 6
        reasons.append("Price below VWAP")

    # ========================================================
    # VOLUME
    # ========================================================

    volume_ratio = float(
        x["volume_ratio"]
    )

    if volume_ratio >= 1.5:

        if x["close"] > x["open"]:

            score += 8
            reasons.append(
                "Strong bullish volume"
            )

        else:

            score -= 8
            reasons.append(
                "Strong bearish volume"
            )

    elif volume_ratio >= 1.15:

        if x["close"] > x["open"]:
            score += 3
        else:
            score -= 3

    # ========================================================
    # ADX
    # ========================================================

    adx = float(x["adx"])

    if adx >= 25:

        if x["ema9"] > x["ema21"]:

            score += 6
            reasons.append(
                "ADX confirms bullish trend"
            )

        else:

            score -= 6
            reasons.append(
                "ADX confirms bearish trend"
            )

    # ========================================================
    # BOS
    # ========================================================

    if bool(x["bullish_bos"]):

        score += 12
        reasons.append(
            "Bullish Break of Structure"
        )

    if bool(x["bearish_bos"]):

        score -= 12
        reasons.append(
            "Bearish Break of Structure"
        )

    # ========================================================
    # LIQUIDITY SWEEP
    # ========================================================

    if bool(x["bullish_liquidity_sweep"]):

        score += 12
        reasons.append(
            "Bullish liquidity sweep"
        )

    if bool(x["bearish_liquidity_sweep"]):

        score -= 12
        reasons.append(
            "Bearish liquidity sweep"
        )

    # ========================================================
    # ORDER BLOCK PROXY
    # ========================================================

    if bool(x["bullish_ob_proxy"]):

        score += 8
        reasons.append(
            "Bullish order-block proxy"
        )

    if bool(x["bearish_ob_proxy"]):

        score -= 8
        reasons.append(
            "Bearish order-block proxy"
        )

    # ========================================================
    # BOLLINGER
    # ========================================================

    if (
        x["close"] > x["bb_mid"] and
        x["close"] < x["bb_upper"]
    ):

        score += 3

    elif (
        x["close"] < x["bb_mid"] and
        x["close"] > x["bb_lower"]
    ):

        score -= 3

    # ========================================================
    # CLAMP
    # ========================================================

    score = int(
        max(
            -100,
            min(100, score)
        )
    )

    # ========================================================
    # SIGNAL
    # ========================================================

    if score >= 55:

        signal = "STRONG LONG 🟢"

    elif score >= 30:

        signal = "LONG 🟢"

    elif score <= -55:

        signal = "STRONG SHORT 🔴"

    elif score <= -30:

        signal = "SHORT 🔴"

    else:

        signal = "WAIT 🟡"

    return {
        "df": df,
        "score": score,
        "signal": signal,
        "price": float(x["close"]),
        "atr": float(x["atr"]),
        "rsi": rsi,
        "adx": adx,
        "volume_ratio": volume_ratio,
        "vwap": float(x["vwap"]),
        "reasons": reasons
    }


# ============================================================
# MULTI TIMEFRAME
# ============================================================

def get_multi_timeframe(symbol):

    configs = {
        "4H": ("4h", 0.35),
        "1H": ("1h", 0.30),
        "15M": ("15m", 0.20),
        "5M": ("5m", 0.15)
    }

    results = {}

    for tf, (interval, weight) in configs.items():

        df = get_klines(
            symbol,
            interval,
            500
        )

        results[tf] = {
            "analysis": analyze_timeframe(df),
            "weight": weight
        }

    return results


# ============================================================
# FINAL SIGNAL
# ============================================================

def calculate_final_signal(mtf):

    total = 0
    available_weight = 0

    for tf, data in mtf.items():

        analysis = data["analysis"]

        if analysis is not None:

            total += (
                analysis["score"] *
                data["weight"]
            )

            available_weight += data["weight"]

    if available_weight == 0:
        return 0, "WAIT 🟡", 0

    score = total / available_weight

    score = round(
        max(-100, min(100, score)),
        2
    )

    # Strong consensus requirement
    scores = []

    for data in mtf.values():

        if data["analysis"]:

            scores.append(
                data["analysis"]["score"]
            )

    bullish_count = sum(
        s >= 30 for s in scores
    )

    bearish_count = sum(
        s <= -30 for s in scores
    )

    if (
        score >= 55 and
        bullish_count >= 3
    ):

        signal = "STRONG LONG 🟢"

    elif (
        score >= 30 and
        bullish_count >= 2
    ):

        signal = "LONG 🟢"

    elif (
        score <= -55 and
        bearish_count >= 3
    ):

        signal = "STRONG SHORT 🔴"

    elif (
        score <= -30 and
        bearish_count >= 2
    ):

        signal = "SHORT 🔴"

    else:

        signal = "WAIT 🟡"

    confidence = int(
        min(99, abs(score))
    )

    return score, signal, confidence


# ============================================================
# ENTRY / TP / SL
# ============================================================

def calculate_trade_levels(
    signal,
    price,
    atr
):

    if atr <= 0:
        atr = price * 0.005

    if "LONG" in signal:

        entry = price

        sl = entry - (
            atr * 1.5
        )

        tp1 = entry + (
            atr * 1.5
        )

        tp2 = entry + (
            atr * 3.0
        )

        tp3 = entry + (
            atr * 4.5
        )

    elif "SHORT" in signal:

        entry = price

        sl = entry + (
            atr * 1.5
        )

        tp1 = entry - (
            atr * 1.5
        )

        tp2 = entry - (
            atr * 3.0
        )

        tp3 = entry - (
            atr * 4.5
        )

    else:

        entry = price
        sl = price
        tp1 = price
        tp2 = price
        tp3 = price

    if "LONG" in signal:

        risk = abs(
            entry - sl
        )

        reward = abs(
            tp2 - entry
        )

    elif "SHORT" in signal:

        risk = abs(
            sl - entry
        )

        reward = abs(
            entry - tp2
        )

    else:

        risk = 0
        reward = 0

    rr = (
        reward / risk
        if risk > 0
        else 0
    )

    return {
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "rr": rr
    }


# ============================================================
# SIMPLE HISTORICAL BACKTEST
# ============================================================

def run_backtest(
    df,
    threshold=30,
    forward_bars=12
):

    if df is None or len(df) < 300:
        return None

    df = add_indicators(
        df.copy()
    )

    trades = []

    start = 250
    end = len(df) - forward_bars - 2

    for i in range(start, end):

        x = df.iloc[i]

        score = 0

        # EMA
        score += (
            8 if x["ema9"] > x["ema21"]
            else -8
        )

        score += (
            8 if x["ema21"] > x["ema50"]
            else -8
        )

        score += (
            10 if x["ema50"] > x["ema200"]
            else -10
        )

        # RSI
        if 52 <= x["rsi"] <= 68:
            score += 8

        elif 32 <= x["rsi"] < 48:
            score -= 8

        # MACD
        if (
            x["macd"] >
            x["macd_signal"] and
            x["macd_hist"] > 0
        ):
            score += 10

        elif (
            x["macd"] <
            x["macd_signal"] and
            x["macd_hist"] < 0
        ):
            score -= 10

        # VWAP
        score += (
            6 if x["close"] > x["vwap"]
            else -6
        )

        # Volume
        if x["volume_ratio"] >= 1.5:

            score += (
                8 if x["close"] > x["open"]
                else -8
            )

        # Structure
        if x["bullish_bos"]:
            score += 12

        if x["bearish_bos"]:
            score -= 12

        # Liquidity
        if x["bullish_liquidity_sweep"]:
            score += 12

        if x["bearish_liquidity_sweep"]:
            score -= 12

        # OB
        if x["bullish_ob_proxy"]:
            score += 8

        if x["bearish_ob_proxy"]:
            score -= 8

        if score >= threshold:

            direction = "LONG"

        elif score <= -threshold:

            direction = "SHORT"

        else:
            continue

        entry = float(
            x["close"]
        )

        atr = float(
            x["atr"]
        )

        if atr <= 0:
            continue

        if direction == "LONG":

            sl = entry - atr * 1.5
            tp = entry + atr * 3

        else:

            sl = entry + atr * 1.5
            tp = entry - atr * 3

        future = df.iloc[
            i + 1:
            i + 1 + forward_bars
        ]

        result = "OPEN"

        for _, candle in future.iterrows():

            if direction == "LONG":

                hit_sl = (
                    candle["low"] <= sl
                )

                hit_tp = (
                    candle["high"] >= tp
                )

            else:

                hit_sl = (
                    candle["high"] >= sl
                )

                hit_tp = (
                    candle["low"] <= tp
                )

            # Conservative rule:
            # If TP and SL happen inside the
            # same candle, count SL first.
            if hit_sl:

                result = "LOSS"
                break

            if hit_tp:

                result = "WIN"
                break

        if result != "OPEN":

            trades.append(result)

    if not trades:
        return {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0
        }

    wins = trades.count("WIN")
    losses = trades.count("LOSS")
    total = len(trades)

    return {
        "trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round(
            wins / total * 100,
            2
        )
    }


# ============================================================
# SIDEBAR
# ============================================================

symbols = get_futures_symbols()

with st.sidebar:

    st.markdown("## 👑 VIP PRO")

    symbol = st.selectbox(
        "Binance Futures Pair",
        symbols
    )

    refresh = st.number_input(
        "Refresh interval (seconds)",
        min_value=10,
        max_value=300,
        value=30,
        step=10
    )

    page = st.radio(
        "Menu",
        [
            "Live Signal",
            "Backtest",
            "Signal History"
        ]
    )

    if st.button(
        "🔄 Refresh Market",
        use_container_width=True
    ):
        st.cache_data.clear()
        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="title">
        👑 AI NISAL BINANCE VIP PRO V3
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="subtitle">
        Binance USDⓈ-M Futures • {symbol}
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LIVE SIGNAL
# ============================================================

if page == "Live Signal":

    with st.spinner(
        "🔎 Analyzing Binance market..."
    ):

        mtf = get_multi_timeframe(
            symbol
        )

    if any(
        item["analysis"] is None
        for item in mtf.values()
    ):

        st.error(
            "Market data ලබාගැනීමට නොහැකි විය."
        )

        st.stop()

    final_score, final_signal, confidence = (
        calculate_final_signal(mtf)
    )

    # Use 5M for entry
    current = mtf["5M"]["analysis"]

    price = current["price"]
    atr = current["atr"]

    levels = calculate_trade_levels(
        final_signal,
        price,
        atr
    )

    premium = get_premium_data(
        symbol
    )

    open_interest = get_open_interest(
        symbol
    )

    # --------------------------------------------------------
    # SIGNAL COLOR
    # --------------------------------------------------------

    if "LONG" in final_signal:
        signal_color = "#059669"

    elif "SHORT" in final_signal:
        signal_color = "#DC2626"

    else:
        signal_color = "#F59E0B"

    # --------------------------------------------------------
    # SIGNAL
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="signal"
             style="background:{signal_color};">

            {final_signal}

            <div style="font-size:15px;margin-top:5px;">
                Signal Score: {final_score}/100
                &nbsp; • &nbsp;
                Confidence: {confidence}/100
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # TRADE LEVELS
    # --------------------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    cards = [
        ("ENTRY", levels["entry"]),
        ("TP 1", levels["tp1"]),
        ("TP 2", levels["tp2"]),
        ("TP 3", levels["tp3"]),
        ("STOP LOSS", levels["sl"])
    ]

    for col, (label, value) in zip(
        [c1, c2, c3, c4, c5],
        cards
    ):

        col.markdown(
            f"""
            <div class="card">
                <div class="label">
                    {label}
                </div>
                <div class="value">
                    ${value:,.6f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # MARKET DATA
    # --------------------------------------------------------

    st.markdown("### 📊 Live Futures Data")

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric(
        "Mark Price",
        f"${premium['mark_price']:,.4f}"
    )

    m2.metric(
        "Funding",
        f"{premium['funding'] * 100:.4f}%"
    )

    m3.metric(
        "Open Interest",
        f"{open_interest:,.0f}"
    )

    m4.metric(
        "ATR 5M",
        f"${atr:,.4f}"
    )

    m5.metric(
        "Risk / Reward",
        f"1 : {levels['rr']:.2f}"
    )

    # --------------------------------------------------------
    # MULTI TIMEFRAME
    # --------------------------------------------------------

    st.markdown(
        "### 🕐 Multi-Timeframe Confirmation"
    )

    table = []

    for tf in [
        "4H",
        "1H",
        "15M",
        "5M"
    ]:

        a = mtf[tf]["analysis"]

        table.append(
            {
                "Timeframe": tf,
                "Signal": a["signal"],
                "Score": a["score"],
                "RSI": round(
                    a["rsi"],
                    2
                ),
                "ADX": round(
                    a["adx"],
                    2
                ),
                "Volume ×": round(
                    a["volume_ratio"],
                    2
                )
            }
        )

    st.dataframe(
        pd.DataFrame(table),
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # INDICATORS
    # --------------------------------------------------------

    st.markdown(
        "### 📈 5M Indicators"
    )

    i1, i2, i3, i4, i5 = st.columns(5)

    i1.metric(
        "RSI",
        f"{current['rsi']:.2f}"
    )

    i2.metric(
        "ADX",
        f"{current['adx']:.2f}"
    )

    i3.metric(
        "Volume",
        f"{current['volume_ratio']:.2f}x"
    )

    i4.metric(
        "VWAP",
        f"${current['vwap']:,.4f}"
    )

    i5.metric(
        "ATR",
        f"${current['atr']:,.4f}"
    )

    # --------------------------------------------------------
    # SIGNAL REASONS
    # --------------------------------------------------------

    st.markdown(
        "### 🧠 Signal Analysis"
    )

    for reason in current["reasons"]:

        st.write(
            "✅",
            reason
        )

    # --------------------------------------------------------
    # RISK WARNING
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="warning">

        ⚠️ <b>Important:</b>

        This is an algorithmic market-analysis tool.
        It does not guarantee future price movement.

        A signal should be treated as a setup,
        not as a guaranteed trade.

        Always use position sizing and stop-loss
        management.

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # SAVE SIGNAL HISTORY
    # --------------------------------------------------------

    if (
        "LONG" in final_signal or
        "SHORT" in final_signal
    ):

        if "signal_history" not in st.session_state:

            st.session_state.signal_history = []

        record = {
            "Time": datetime.now(
                timezone.utc
            ).strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            ),
            "Symbol": symbol,
            "Signal": final_signal,
            "Score": final_score,
            "Entry": levels["entry"],
            "TP1": levels["tp1"],
            "TP2": levels["tp2"],
            "SL": levels["sl"]
        }

        # Avoid duplicate records
        if (
            not st.session_state.signal_history
            or
            st.session_state.signal_history[-1]["Time"]
            != record["Time"]
        ):

            st.session_state.signal_history.append(
                record
            )


# ============================================================
# BACKTEST
# ============================================================

elif page == "Backtest":

    st.markdown(
        "### 🧪 Historical Strategy Backtest"
    )

    st.info(
        "මෙය historical heuristic backtest එකක්. "
        "Fees, slippage සහ funding costs ඇතුළත් කරලා නැහැ."
    )

    interval = st.selectbox(
        "Backtest Timeframe",
        [
            "5m",
            "15m",
            "1h"
        ],
        index=1
    )

    bars = st.slider(
        "Historical candles",
        500,
        1500,
        1000,
        step=100
    )

    forward_bars = st.slider(
        "Maximum bars to evaluate trade",
        3,
        30,
        12
    )

    if st.button(
        "▶️ RUN BACKTEST",
        use_container_width=True
    ):

        with st.spinner(
            "Running historical test..."
        ):

            df = get_klines(
                symbol,
                interval,
                bars
            )

            result = run_backtest(
                df,
                threshold=30,
                forward_bars=forward_bars
            )

        if result is None:

            st.error(
                "Backtest සඳහා ප්‍රමාණවත් data නැහැ."
            )

        else:

            b1, b2, b3, b4 = st.columns(4)

            b1.metric(
                "Trades",
                result["trades"]
            )

            b2.metric(
                "Wins",
                result["wins"]
            )

            b3.metric(
                "Losses",
                result["losses"]
            )

            b4.metric(
                "Win Rate",
                f"{result['win_rate']}%"
            )

            st.markdown(
                """
                <div class="warning">

                ⚠️ Historical win rate එක future
                performance එකක් guarantee කරන්නේ නැහැ.

                Fees, spread, slippage, funding,
                execution delay වගේ real trading costs
                මේ simple backtest එකේ ඇතුළත් නොවේ.

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# SIGNAL HISTORY
# ============================================================

elif page == "Signal History":

    st.markdown(
        "### 📜 Signal History"
    )

    history = st.session_state.get(
        "signal_history",
        []
    )

    if not history:

        st.info(
            "මෙම session එකේ signal history එකක් නැහැ."
        )

    else:

        history_df = pd.DataFrame(
            history
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        if st.button(
            "🗑 Clear History"
        ):

            st.session_state.signal_history = []

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "AI Nisal Binance VIP Pro V3 • "
    "Market analysis only • "
    "No automatic order execution"
)
