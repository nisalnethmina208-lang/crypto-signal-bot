import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(page_title="Crypto Signal Bot", layout="centered")

st.title("Crypto Signal Bot 🚀")

# ඔබ සතුව ඇති HTML Code එක මේ Quotation (""") ඇතුළට Paste කරන්න
html_code = """
<div style="text-align: center; padding: 20px; background-color: #1e1e1e; color: white; border-radius: 10px;">
    <h2>Crypto Signal Bot Dashboard</h2>
    <p>Status: Active 🟢</p>
</div>
"""

# HTML Code එක Streamlit එකේ Render කිරීම
components.html(html_code, height=500, scrolling=True)
