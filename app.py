import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import urllib.parse

# 1. KIDS-STYLE THEME & LIGHT MODE FORCING
st.set_page_config(page_title="Archie's Day", page_icon="🦁", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #f0fdf4;
        background-image: radial-gradient(#dcfce7 1px, transparent 1px);
        background-size: 20px 20px;
    }
    .input-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 25px;
        border: 4px solid #86efac;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    h1 { color: #166534; font-family: 'Comic Sans MS', cursive, sans-serif; text-align: center; font-size: 2.5rem; }
    h3 { color: #15803d; font-family: 'Arial Rounded MT Bold', sans-serif; }
    
    .stButton>button {
        background-color: #22c55e;
        color: white;
        border-radius: 50px;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 15px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        display: block;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Larger Input Text for Mobile */
    input { font-size: 1.2rem !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. HELPER FUNCTIONS
def clean_time(t_str):
    if not t_str: return None
    clean = t_str.replace(":", "").strip()
    if len(clean) == 4 and clean.isdigit():
        try:
            hh, mm = int(clean[:2]), int(clean[2:])
            if 0 <= hh < 24 and 0 <= mm < 60:
                return time(hh, mm)
        except: return None
    return None

# 3. TOP-LEVEL INPUTS
st.markdown("<h1>🦁 Archie's Jungle</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("📅 Morning Check-in")
    st.caption("Enter 4 digits (e.g., 0715 or 2130)")
    
    c1, c2 = st.columns(2)
    # Empty defaults to allow immediate entry
    w_in = c1.text_input("☀️ Wake-up", "", placeholder="0700")
    s_in = c2.text_input("🌙 Last Sleep", "", placeholder="2130")
    
    n_in = st.text_input("😴 Nap Started? (Optional)", "", placeholder="1300")
    
    location = st.selectbox("📍 Current Jungle", ["Netherlands (CET)", "India (IST)"], index=0)
    
    with st.expander("🦉 Night Waking?"):
        nw_c1, nw_c2 = st.columns(2)
        nw_s_in = nw_c1.text_input("Woke at", "", placeholder="0200")
        nw_e_in = nw_c2.text_input("Slept at", "", placeholder="0245")

    lock = st.button("🌟 GENERATE MY DAY!", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 4. LOGIC ENGINE
if 'run' not in st.session_state: st.session_state.run = False
if lock: st.session_state.run = True

if st.session_state.run:
    # Use indicative defaults only if user leaves blank
    wake_time = clean_time(w_in) or time(7, 0)
    sleep_time = clean_time(s_in) or time(21, 30)
    nap_manual = clean_time(n_in)
    
    today = datetime.today()
    wake_dt = datetime.combine(today, wake_time)
    prev_sleep_dt = datetime.combine(today - timedelta(days=1), sleep_time)
    target _7am =
