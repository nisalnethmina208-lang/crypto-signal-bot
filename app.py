import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="Binance Live Trading Center",
    page_icon="📈",
    layout="wide"
)

# Dark Theme & Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #121418;
        color: #FFFFFF;
    }
    .trading-card {
        background-color: #1E2329;
        border: 1px solid #2B313A;
        padding: 20px;
        border-radius: 12px;
        margin-top: 10px;
    }
    .ticker-title {
        font-size: 32px;
        font-weight: bold;
        color: #F0B90B;
    }
    .buy-btn {
        background-color: #0ECB81;
        color: white;
        padding: 8px 20px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        text-align: center;
        float: right;
    }
    .sell-btn {
        background-color: #F6465D;
        color: white;
        padding: 8px 20px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        text-align: center;
        float: right;
    }
    .stat-label {
        color: #848E9C;
        font-size: 13px;
    }
    .stat-val {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: bold;
    }
    .tp-card {
        background-color: #172622;
        border: 1px solid #0ECB81;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .sl-card {
        background-color: #26191D;
        border: 1px solid #F6465D;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title
st.markdown("<h2 style='color: #F0B90B;'>📊 Binance Live Trading Center</h2>", unsafe_allow_html=True)

# Popular Coins mapping with CoinGecko IDs for reliable fetching
coins_data = {
    "BTCUSDT": {"id": "bitcoin", "name": "BTC/USDT"},
    "ETHUSDT": {"id": "ethereum", "name": "ETH/USDT"},
    "BNBUSDT": {"id": "binancecoin", "name": "BNB/USDT"},
    "SOLUSDT": {"id": "solana", "name": "SOL/USDT"},
    "XRPUSDT": {"id": "ripple", "name": "XRP/USDT"},
    "ADAUSDT": {"id": "cardano", "name": "ADA/USDT"},
    "DOGEUSDT": {"id": "dogecoin", "name": "DOGE/USDT"},
    "DOTUSDT": {"id": "polkadot", "name": "DOT/USDT"},
    "MATICUSDT": {"id": "polygon", "name": "MATIC/USDT"},
    "LINKUSDT": {"id": "chainlink", "name": "LINK/USDT"}
}

selected_coin = st.selectbox("Coin Pair එක තෝරන්න:", list(coins_data.keys()))

# Fetch live market data securely
coin_id = coins_data[selected_coin]["id"]
url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_high=true&include_24hr_low=true"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if coin_id in data:
        coin_info = data[coin_id]
        last_price = float(coin_info['usd'])
        price_change_pct = float(coin_info.get('usd_24h_change', 0.0))
        high_24h = last_price * (1 + abs(price_change_pct)/100 * 0.5) # Estimated high/low if not provided directly
        low_24h = last_price * (1 - abs(price_change_pct)/100 * 0.5)
        
        # Trend and Action
        is_uptrend = price_change_pct >= 0
        trend_text = "Uptrend Structure (UP)" if is_uptrend else "Downtrend Structure (DOWN)"
        trend_color = "#0ECB81" if is_uptrend else "#F6465D"
        action_type = "BUY" if is_uptrend else "SELL"
        btn_class = "buy-btn" if is_uptrend else "sell-btn"

        # Targets Calculation
        if is_uptrend:
            tp1 = last_price * 1.02
            tp2 = last_price * 1.04
            sl = last_price * 0.98
        else:
            tp1 = last_price * 0.98
            tp2 = last_price * 0.96
            sl = last_price * 1.02

        # Display Card
        st.markdown(f"""
            <div class="trading-card">
                <p style="color: #848E9C; font-size: 12px; margin-bottom: -5px;">BINANCE SPOT</p>
                <table width="100%">
                    <tr>
                        <td><span class="ticker-title">{selected_coin}</span></td>
                        <td align="right"><div class="{btn_class}">{action_type} 📈</div></td>
                    </tr>
                </table>
                <p style="color: {trend_color}; font-weight: bold; margin-top: 5px;">● {trend_text}</p>
                <hr style="border-color: #2B313A; margin: 15px 0;">
                
                <table width="100%">
                    <tr>
                        <td><div class="stat-label">LIVE PRICE</div><div class="stat-val">${last_price:,.4f}</div></td>
                        <td><div class="stat-label">24H CHANGE</div><div class="stat-val" style="color: {trend_color};">{price_change_pct:+.2f}%</div></td>
                        <td><div class="stat-label">EST. HIGH</div><div class="stat-val">${high_24h:,.4f}</div></td>
                        <td><div class="stat-label">EST. LOW</div><div class="stat-val">${low_24h:,.4f}</div></td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # TP1, TP2, SL Cards
        tp_col1, tp_col2, sl_col = st.columns(3)

        with tp_col1:
            st.markdown(f"""
                <div class="tp-card">
                    <p style="color: #0ECB81; font-weight: bold; margin-bottom: 5px;">🎯 TP 1 (+2.0%)</p>
                    <h3 style="color: #FFFFFF; margin: 0;">${tp1:,.4f}</h3>
                </div>
            """, unsafe_allow_html=True)

        with tp_col2:
            st.markdown(f"""
                <div class="tp-card">
                    <p style="color: #0ECB81; font-weight: bold; margin-bottom: 5px;">🎯 TP 2 (+4.0%)</p>
                    <h3 style="color: #FFFFFF; margin: 0;">${tp2:,.4f}</h3>
                </div>
            """, unsafe_allow_html=True)

        with sl_col:
            st.markdown(f"""
                <div class="sl-card">
                    <p style="color: #F6465D; font-weight: bold; margin-bottom: 5px;">🛡️ SL (-2.0%)</p>
                    <h3 style="color: #FFFFFF; margin: 0;">${sl:,.4f}</h3>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("දත්ත සොයා ගැනීමට නොහැකි විය.")

except Exception as e:
    st.error(f"දත්ත ලබා ගැනීමේ දෝෂයක් මතු විය: {e}")
