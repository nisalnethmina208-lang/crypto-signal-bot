import streamlit as st
import streamlit.components.v1 as components
import requests

# Page Configuration
st.set_page_config(page_title="Binance Signal Center", layout="centered")

# Tabs
tab1, tab2 = st.tabs(["📊 Signals & Market", "⚙️ Settings"])

with tab1:
    st.markdown("<h2 style='color: #F0B90B;'>⚡ Binance Signal Center</h2>", unsafe_allow_html=True)
    
    # 1. Expanded Coin List + Custom Search Box
    popular_coins = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
        "ADA/USDT", "DOGE/USDT", "PEPE/USDT", "AVAX/USDT", "LINK/USDT",
        "DOT/USDT", "NEAR/USDT", "SUI/USDT", "SHIB/USDT", "LTC/USDT",
        "FET/USDT", "WIF/USDT", "FLOKI/USDT", "TRX/USDT", "TON/USDT",
        "BCH/USDT", "APT/USDT", "RENDER/USDT", "TIA/USDT", "INJ/USDT"
    ]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_pair = st.selectbox("Coin Pair එක තෝරන්න:", popular_coins)
    with col2:
        custom_input = st.text_input("වෙනත් Coin එකක් Type කරන්න:", placeholder="eg: RUNE")
        
    if custom_input.strip():
        custom_symbol = custom_input.upper().strip().replace("USDT", "")
        selected_pair = f"{custom_symbol}/USDT"

    tv_symbol = selected_pair.replace("/", "")

    # 2. Fetch Live Market Data from Binance API
    current_price = 0.0
    price_change_pct = 0.0
    high_price = 0.0
    low_price = 0.0

    try:
        res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={tv_symbol}", timeout=3)
        if res.status_code == 200:
            data = res.json()
            current_price = float(data.get("lastPrice", 0))
            price_change_pct = float(data.get("priceChangePercent", 0))
            high_price = float(data.get("highPrice", 0))
            low_price = float(data.get("lowPrice", 0))
    except Exception:
        pass

    # 3. Dynamic Buy/Sell Signal Logic
    if price_change_pct >= 2.0:
        signal_badge = "STRONG BUY 🚀"
        signal_bg = "#0ECB81"
        trend_text = "Market එක සීඝ්‍රයෙන් උඩට යයි (Strong UP) ⬆️"
        trend_color = "#0ECB81"
        is_buy = True
    elif price_change_pct > 0:
        signal_badge = "BUY 📈"
        signal_bg = "#26A69A"
        trend_text = "Market එක උඩට යයි (UP Trend) ↗️"
        trend_color = "#26A69A"
        is_buy = True
    elif price_change_pct <= -2.0:
        signal_badge = "STRONG SELL 🔻"
        signal_bg = "#F6465D"
        trend_text = "Market එක සීඝ්‍රයෙන් පහලට යයි (Strong DOWN) ⬇️"
        trend_color = "#F6465D"
        is_buy = False
    else:
        signal_badge = "SELL 📉"
        signal_bg = "#E55656"
        trend_text = "Market එක පහලට යයි (DOWN Trend) ↘️"
        trend_color = "#E55656"
        is_buy = False

    # 4. TP / SL Targets Calculation Logic
    if current_price > 0:
        if is_buy:
            tp1 = current_price * 1.02  # +2% TP
            tp2 = current_price * 1.04  # +4% TP
            sl = current_price * 0.98   # -2% SL
            tp_label_1, tp_label_2, sl_label = "🎯 TP 1 (+2%)", "🎯 TP 2 (+4%)", "🛡️ SL (-2%)"
        else:
            tp1 = current_price * 0.98  # -2% TP for Short/Sell
            tp2 = current_price * 0.96  # -4% TP for Short/Sell
            sl = current_price * 1.02   # +2% SL for Short/Sell
            tp_label_1, tp_label_2, sl_label = "🎯 TP 1 (-2%)", "🎯 TP 2 (-4%)", "🛡️ SL (+2%)"
    else:
        tp1 = tp2 = sl = 0.0
        tp_label_1 = tp_label_2 = sl_label = "-"

    st.markdown("---")

    # 5. Styled Signal Dashboard Card with TP / SL
    signal_card_html = f"""
    <div style="background-color: #1E2329; padding: 20px; border-radius: 12px; border: 1px solid #2B313A; color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="color: #848E9C; font-size: 13px;">Selected Pair</span>
                <h2 style="margin: 2px 0; color: #F0B90B; font-size: 28px;">{selected_pair}</h2>
                <p style="margin: 4px 0 0 0; color: {trend_color}; font-weight: bold; font-size: 14px;">{trend_text}</p>
            </div>
            <div>
                <div style="background-color: {signal_bg}; color: white; padding: 10px 18px; border-radius: 8px; font-weight: bold; font-size: 18px; text-align: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
                    {signal_badge}
                </div>
            </div>
        </div>
        
        <hr style="border: 0.5px solid #2B313A; margin: 15px 0;">
        
        <div style="display: flex; justify-content: space-between; text-align: center;">
            <div>
                <span style="color: #848E9C; font-size: 12px;">Live Price</span>
                <h3 style="margin: 5px 0 0 0; font-size: 17px;">${current_price:,.4f}</h3>
            </div>
            <div>
                <span style="color: #848E9C; font-size: 12px;">24h Change</span>
                <h3 style="margin: 5px 0 0 0; color: {trend_color}; font-size: 17px;">{price_change_pct:+.2f}%</h3>
            </div>
            <div>
                <span style="color: #848E9C; font-size: 12px;">24h High</span>
                <h3 style="margin: 5px 0 0 0; font-size: 17px;">${high_price:,.4f}</h3>
            </div>
        </div>

        <hr style="border: 0.5px solid #2B313A; margin: 15px 0;">

        <!-- TP and SL Section -->
        <div style="display: flex; justify-content: space-between; text-align: center; gap: 8px;">
            <div style="background-color: #0E3A2F; border: 1px solid #0ECB81; padding: 10px; border-radius: 8px; flex: 1;">
                <span style="color: #0ECB81; font-size: 11px; font-weight: bold;">{tp_label_1}</span>
                <h4 style="margin: 4px 0 0 0; color: white; font-size: 15px;">${tp1:,.4f}</h4>
            </div>
            <div style="background-color: #0E3A2F; border: 1px solid #0ECB81; padding: 10px; border-radius: 8px; flex: 1;">
                <span style="color: #0ECB81; font-size: 11px; font-weight: bold;">{tp_label_2}</span>
                <h4 style="margin: 4px 0 0 0; color: white; font-size: 15px;">${tp2:,.4f}</h4>
            </div>
            <div style="background-color: #3B1B24; border: 1px solid #F6465D; padding: 10px; border-radius: 8px; flex: 1;">
                <span style="color: #F6465D; font-size: 11px; font-weight: bold;">{sl_label}</span>
                <h4 style="margin: 4px 0 0 0; color: white; font-size: 15px;">${sl:,.4f}</h4>
            </div>
        </div>
    </div>
    """
    st.markdown(signal_card_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. Dynamic TradingView Chart Widget
    tradingview_code = f"""
    <div class="tradingview-widget-container" style="height:100%;width:100%">
      <div id="tradingview_chart" style="height:450px;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "BINANCE:{tv_symbol}",
        "interval": "15",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(tradingview_code, height=470)

with tab2:
    st.subheader("Settings")
    st.write("Settings configuration controls.")
