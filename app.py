import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time

# 1. SETUP & BEAUTIFUL JUNGLE THEME
st.set_page_config(page_title="Archie's Schedule", page_icon="🦁", layout="wide")

st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    .stApp { background-image: url("https://www.transparenttextures.com/patterns/leaf.png"); }
    h1, h2, h3 { color: #1b5e20; font-family: 'Trebuchet MS', sans-serif; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #4caf50; }
    .info-card { background-color: #fff9c4; padding: 15px; border-radius: 10px; border-left: 5px solid #fbc02d; margin-bottom: 10px; font-size: 0.9rem; }
    .stTable { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR COMMAND CENTER
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Date', 'WakeGap', 'TotalSleep'])

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/jungle.png")
    st.header("🌳 Jungle Settings")
    
    location = st.radio("📍 Current Jungle", ["India (IST)", "Netherlands (CET)"], index=1)
    
    st.divider()
    st.write("🎯 **Target Wake:** 7:00 AM")
    wake_time = st.time_input("☀️ Actual Morning Wake-up", value=time(7, 0))
    prev_sleep_time = st.time_input("🌙 Previous Night Sleep", value=time(21, 30))
    
    st.subheader("🦉 Night Waking")
    night_wake_start = st.time_input("Woke up at", value=None)
    night_wake_end = st.time_input("Back to sleep at", value=None)
    
    st.subheader("😴 Daytime Nap")
    nap_start = st.time_input("Nap Started At (Optional)", value=None)
    
    if st.button("🌿 Log Today & Update"):
        # Logic to save to history
        gap = (datetime.combine(datetime.today(), wake_time) - datetime.combine(datetime.today(), time(7,0))).total_seconds()/60
        new_data = pd.DataFrame([[datetime.today().strftime('%m-%d'), gap, 11.5]], columns=['Date', 'WakeGap', 'TotalSleep'])
        st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)

# 3. LOGIC ENGINE
genai.configure(api_key="AIzaSyAtlrIyT0LrtmGetXY-bGuEKJHufvzdF-0")
today = datetime.today()
wake_dt = datetime.combine(today, wake_time)

# Night Waking Logic
night_wake_duration = 0
if night_wake_start and night_wake_end:
    start_dt = datetime.combine(today, night_wake_start)
    end_dt = datetime.combine(today, night_wake_end)
    if end_dt < start_dt: end_dt += timedelta(days=1)
    night_wake_duration = (end_dt - start_dt).total_seconds() / 3600

# Sleep Calculations
sleep_dt = datetime.combine(today - timedelta(days=1),  prev
