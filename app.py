import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NISAL BINANCE SIGNALS",
    page_icon="📈",
    layout="wide"
)

BINANCE_BASE = "https://data-api.binance.vision"

PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]

TIMEFRAMES = ["5m", "15m", "1h", "4h"]

def get_json(path, params=None):
    hosts = [
        "https://data-api.binance.vision",
        "https://api1.binance.com",
        "https://api2.binance.com",
        "https://api3.binance.com",
        "https://api4.binance.com"
    ]

    last_error = None

    for host in hosts:
        try:
            response = requests.get(
                host + path,
                params=params,
                timeout=15,
                headers={
                    "User-Agent": "Nisal-Binance-Signals/1.0"
                }
            )

            response.raise_for_status()
            return response.json()

        except Exception as error:
            last_error = error

    raise RuntimeError(
        f"Unable to load market data: {last_error}"
    )


def get_price(symbol):
    data = get_json(
        "/api/v3/ticker/24hr",
        {"symbol": symbol}
    )

    return {
        "price": float(data["lastPrice"]),
        "change": float(data["priceChangePercent"]),
        "high": float(data["highPrice"]),
        "low": float(data["lowPrice"]),
        "volume": float(data["volume"])
    }


def get_klines(symbol, interval, limit=200):
    data = get_json(
        "/api/v3/klines",
        {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
    )

    columns = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "trades",
        "buy_volume",
        "buy_quote_volume",
        "ignore"
    ]

    df = pd.DataFrame(data, columns=columns)

    for column in [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]:
        df[column] = pd.to_numeric(df[column])

    return df


def calculate_signal(df):
    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)

    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()

    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()

    last = df.iloc[-1]

    score = 0

    if last["EMA20"] > last["EMA50"]:
        score += 1
    else:
        score -= 1

    if last["RSI"] > 50:
        score += 1
    else:
        score -= 1

    if last["MACD"] > last["MACD_SIGNAL"]:
        score += 1
    else:
        score -= 1

    if score >= 2:
        signal = "🟢 BUY"
    elif score <= -2:
        signal = "🔴 SELL"
    else:
        signal = "🟡 WAIT"

    confidence = min(95, 50 + abs(score) * 15)

    return signal, confidence, last


st.title("📈 NISAL BINANCE SIGNALS")

st.caption(
    "Live market data • Technical analysis • Mobile friendly"
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    symbol = st.selectbox(
        "Trading Pair",
        PAIRS
    )

with col2:
    timeframe = st.selectbox(
        "Timeframe",
        TIMEFRAMES,
        index=1
    )

if st.button(
    "🔄 Refresh Live Data",
    use_container_width=True
):

    try:
        price_data = get_price(symbol)

        df = get_klines(
            symbol,
            timeframe
        )

        signal, confidence, last = calculate_signal(df)

        st.success("Live market data loaded successfully.")

        st.subheader(f"{symbol} — {timeframe}")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Price",
            f"{price_data['price']:,.4f}"
        )

        c2.metric(
            "24h Change",
            f"{price_data['change']:.2f}%"
        )

        c3.metric(
            "24h High",
            f"{price_data['high']:,.4f}"
        )

        c4.metric(
            "24h Low",
            f"{price_data['low']:,.4f}"
        )

        st.divider()

        st.subheader("Signal")

        st.metric(
            "Current Signal",
            signal
        )

        st.write(
            f"Confidence: **{confidence}%**"
        )

        a, b, c = st.columns(3)

        a.metric(
            "RSI",
            f"{last['RSI']:.2f}"
        )

        b.metric(
            "EMA 20",
            f"{last['EMA20']:.4f}"
        )

        c.metric(
            "EMA 50",
            f"{last['EMA50']:.4f}"
        )

        st.subheader("MACD")

        st.write(
            f"MACD: **{last['MACD']:.6f}**"
        )

        st.write(
            f"Signal: **{last['MACD_SIGNAL']:.6f}**"
        )

        st.subheader("Recent Price Chart")

        chart = df.set_index("time")[["close"]].tail(100)

        st.line_chart(chart)

        st.info(
            "⚠️ This application provides technical analysis only. "
            "It does not guarantee profit and is not financial advice."
        )

    except Exception as error:

        st.error(
            "Live market data could not be loaded right now."
        )

        st.info(
            "Please wait a moment and press "
            "Refresh Live Data again."
        )

else:

    st.info(
        "Select a trading pair and timeframe, "
        "then press Refresh Live Data."
    )
