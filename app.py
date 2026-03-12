import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import urllib.parse

# 1. SETUP & THEME
st.set_page_config(page_title="Archie's Schedule", page_icon="🦁", layout="wide")

st.markdown("""
    <style>
    .main { background: #fdfdfd; }
    h1, h2, h3 { color: #2e7d32; font-family: 'Helvetica Neue', sans-serif; }
    .stMetric { background-color: #f1f8e9; padding: 15px; border-radius: 12px; }
    .stTable td { font-size: 16px !important; padding: 10px !important; }
    /* Beautiful WhatsApp Button Styling */
    .whatsapp-btn {
        background-color: #25D366;
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIC ENGINE
genai.configure(api_key="AIzaSyAtlrIyT0LrtmGetXY-bGuEKJHufvzdF-0")
today = datetime.today()

with st.sidebar:
    st.title("🦁 Jungle Controls")
    location = st.radio("📍 Location", ["India (IST)", "Netherlands (CET)"], index=1)
    st.divider()
    wake_time = st.time_input("☀️ Actual Wake-up", value=time(7, 0))
    prev_sleep_time = st.time_input("🌙 Last Night Sleep", value=time(21, 30))
    
    with st.expander("🦉 Night Waking Details"):
        night_wake_start = st.time_input("Woke up at", value=None)
        night_wake_end = st.time_input("Back to sleep at", value=None)
    
    nap_start = st.time_input("😴 Nap Started At (Optional)", value=None)

# Calculations
wake_dt = datetime.combine(today, wake_time)
night_wake_duration = 0
if night_wake_start and night_wake_end:
    start_dt = datetime.combine(today, night_wake_start)
    end_dt = datetime.combine(today, night_wake_end)
    if end_dt < start_dt: end_dt += timedelta(days=1)
    night_wake_duration = (end_dt - start_dt).total_seconds() / 3600

sleep_dt = datetime.combine(today - timedelta(days=1), prev_sleep_time)
actual_night_sleep = ((wake_dt - sleep_dt).total_seconds() / 3600) - night_wake_duration
nap_buffer = 6 if night_wake_duration < 0.5 else 5.5
nap_start_actual = datetime.combine(today, nap_start) if nap_start else wake_dt + timedelta(hours=6)
nap_end_dt = nap_start_actual + timedelta(minutes=90)
bedtime_dt = nap_end_dt + timedelta(hours=6)

# 3. SCHEDULE GENERATION
sched_list = [
    (wake_dt, "🥛 Wake + Immediate Milk"),
    (wake_dt + timedelta(minutes=25), "🍓 Morning Fruit Snack"),
    (wake_dt + timedelta(hours=2), "🍳 Main Breakfast"),
    (nap_start_actual - timedelta(minutes=75), "🍚 Lunch (15m Feast)"),
    (nap_start_actual, "😴 Nap Start"),
    (nap_end_dt, "🎺 Hard Wake (Slow Fade)"),
    (nap_end_dt + timedelta(minutes=15), "🥨 Post-Nap Snack"),
    (nap_end_dt + timedelta(hours=1.5), "🏃 PEAK ACTIVITY ZONE"),
    (nap_end_dt + timedelta(hours=2.5), "🍌 Afternoon Fruit"),
    (datetime.combine(today, time(19, 15)), "🍲 Dinner (Recipe #11)"),
    (bedtime_dt - timedelta(hours=1), "🥛 Pre-Sleep Night Milk"),
    (bedtime_dt, "✨ Bedtime")
]

# 4. WHATSAPP MESSAGE FORMATTING
wa_message = f"*🦁 Archie's Schedule ({location})*\n\n"
for t, act in sched_list:
    wa_message += f"• {t.strftime('%I:%M %p')}: {act}\n"
wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_message)}"

# 5. DASHBOARD DISPLAY
st.title(f"🦁 Archie's Day: {location}")

m1, m2, m3 = st.columns(3)
m1.metric("Night Sleep", f"{actual_night_sleep:.1f}h")
m2.metric("Target Bedtime", bedtime_dt.strftime('%I:%M %p'))
m3.metric("7AM Gap", f"{(wake_dt - datetime.combine(today, time(7,0))).total_seconds()/60 :.0f}m")

st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-btn">📲 Share Schedule via WhatsApp</a>', unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3 = st.tabs(["📅 Daily Plan", "📈 Sleep Pressure Graph", "💬 Jungle Guide"])

with tab1:
    df_sched = pd.DataFrame(sched_list, columns=["Time", "Activity"])
    df_sched["Time"] = df_sched["Time"].apply(lambda x: x.strftime('%I:%M %p'))
    st.table(df_sched)

with tab2:
    st.subheader("Adenosine (Sleep Pressure) Levels")
    # Improved graph labeling
    times = [(wake_dt + timedelta(hours=i)) for i in range(16)]
    # Simplified realistic pressure curve
    pressure_values = [0, 15, 30, 45, 60, 75, 10, 20, 40, 60, 80, 100, 85, 60, 35, 10]
    
    chart_df = pd.DataFrame({
        'Clock Time': [t.strftime('%I %p') for t in times],
        'Sleep Pressure (%)': pressure_values
    }).set_index('Clock Time')
    
    st.area_chart(chart_df, color="#4caf50")
    st.info("The dip in green shows the nap clearing brain fatigue before the final build-up to bedtime.")

with tab3:
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if prompt := st.chat_input("Ask about Archie's day..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"Archie, 23mo. {location}. Night Sleep: {actual_night_sleep}h. {prompt}")
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"): st.markdown(response.text)
