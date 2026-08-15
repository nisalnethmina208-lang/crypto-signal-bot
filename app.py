import streamlit as st

# Signal Card Component
def render_signal_card(symbol, signal_type, entry, tp, sl, confidence, reason):
    bg_color = "#0ecb81" if signal_type == "BUY" else "#f6465d"
    
    card_html = f"""
    <div style="background-color: #1e2329; border-left: 6px solid {bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="color: {bg_color}; margin: 0;">{"🟢" if signal_type == "BUY" else "🔴"} {signal_type} SIGNAL ({symbol})</h3>
            <span style="background-color: {bg_color}; color: black; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px;">
                Confidence: {confidence}%
            </span>
        </div>
        <p style="color: #848e9c; font-size: 13px; margin: 5px 0 10px 0;">Reason: {reason}</p>
        <hr style="border: 0.5px solid #2b313a; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 14px;">
            <div><span style="color: #848e9c;">Entry Range:</span><br><b style="color: #eaecef;">{entry}</b></div>
            <div><span style="color: #848e9c;">Take Profit (TP):</span><br><b style="color: #0ecb81;">{tp}</b></div>
            <div><span style="color: #848e9c;">Stop Loss (SL):</span><br><b style="color: #f6465d;">{sl}</b></div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# App එකේ Main page එකට Call කරන ආකාරය:
render_signal_card(
    symbol="BTC/USDT (15m)",
    signal_type="BUY",
    entry="$63,200 - $63,350",
    tp="$64,500",
    sl="$62,700",
    confidence=88,
    reason="RSI Oversold (28) + EMA 20/50 Golden Cross"
)
