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
sleep_dt = datetime.combine(today - timedelta(days=1), prev_sleep_time)
actual_night_sleep = ((wake_dt - sleep_dt).total_seconds() / 3600) - night_wake_duration
nap_buffer = 6 if night_wake_duration < 0.5 else 5.5
nap_start_rec = wake_dt + timedelta(hours=nap_buffer)
nap_start_actual = datetime.combine(today, nap_start) if nap_start else nap_start_rec
nap_end_dt = nap_start_actual + timedelta(minutes=90)
bedtime_dt = nap_end_dt + timedelta(hours=6)

# 4. DASHBOARD TOP ROW
st.title(f"🦁 Archie's {location} Dashboard")

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Actual Night Sleep", f"{actual_night_sleep:.1f} hrs")
with c2: st.metric("Night Wake Time", f"{night_wake_duration*60:.0f} mins")
with c3: st.metric("Target Bedtime", bedtime_dt.strftime('%I:%M %p'))
with c4: 
    gap_val = (wake_dt - datetime.combine(today, time(7,0))).total_seconds()/60
    st.metric("7AM Target Gap", f"{gap_val:.0f} min", delta=f"{gap_val} min", delta_color="inverse")

st.divider()

# 5. GRAPHS SECTION
graph_col, history_col = st.columns([2, 1])

with graph_col:
    st.subheader("📈 Today's Sleep Pressure & Activity")
    # Generating a curve that peaks during the Peak Activity Zone
    x = np.linspace(0, 16, 17)
    # Sleep pressure builds during wakefulness, drops during nap, builds again
    y = [0, 10, 25, 45, 60, 75, 5, 10, 25, 50, 80, 100, 90, 70, 40, 10, 0] 
    chart_data = pd.DataFrame({'Time (Hours from Wake)': x, 'Sleep Pressure': y})
    st.area_chart(chart_data.set_index('Time (Hours from Wake)'), color="#2e7d32")

with history_col:
    st.subheader("📊 7AM Goal Tracking")
    if not st.session_state.history.empty:
        st.line_chart(st.session_state.history.set_index('Date')['WakeGap'])
    else:
        st.write("Log data in the sidebar to see your weekly progress!")

st.divider()

# 6. SCHEDULE & WISDOM
tab_col, info_col = st.columns([2, 1])

with tab_col:
    st.subheader("📅 The Golden Path")
    sched = [
        {"Time": wake_dt.strftime('%I:%M %p'), "Event": "🥛 Wake Up + Immediate Milk"},
        {"Time": (wake_dt + timedelta(minutes=25)).strftime('%I:%M %p'), "Event": "🍓 Morning Fruit Snack"},
        {"Time": (wake_dt + timedelta(hours=2)).strftime('%I:%M %p'), "Event": "🍳 Main Breakfast"},
        {"Time": (nap_start_actual - timedelta(hours=1, minutes=15)).strftime('%I:%M %p'), "Event": "🍚 Lunch (15-min Feast)"},
        {"Time": nap_start_actual.strftime('%I:%M %p'), "Event": "😴 Nap Start (Sloth Mode)"},
        {"Time": nap_end_dt.strftime('%I:%M %p'), "Event": "🎺 Hard Wake (Slow Fade)"},
        {"Time": (nap_end_dt + timedelta(minutes=15)).strftime('%I:%M %p'), "Event": "🥨 Post-Nap Snack"},
        {"Time": (nap_end_dt + timedelta(hours=1, minutes=30)).strftime('%I:%M %p'), "Event": "🏃 PEAK ACTIVITY ZONE"},
        {"Time": (nap_end_dt + timedelta(hours=2, minutes=30)).strftime('%I:%M %p'), "Event": "🍌 Afternoon Fruit"},
        {"Time": "07:15 PM", "Event": "🍲 Dinner (Recipe #11)"},
        {"Time": (bedtime_dt - timedelta(hours=1)).strftime('%I:%M %p'), "Event": "🥛 Pre-Sleep Night Milk"},
        {"Time": bedtime_dt.strftime('%I:%M %p'), "Event": "✨ Bedtime"}
    ]
    st.table(sched)

with info_col:
    st.subheader("💡 Jungle Wisdom")
    st.markdown(f"""
    <div class="info-card"><strong>⚡ High Activity Needed:</strong><br>Keep Archie moving at <b>{(nap_end_dt + timedelta(hours=1, minutes=30)).strftime('%I:%M %p')}</b>. This is when his sleep pressure needs to build fastest.</div>
    <div class="info-card"><strong>🌅 7 AM Target:</strong><br>If he wakes before 7 AM, do not turn on lights. Darkness is the only way to shift the internal clock.</div>
    <div class="info-card"><strong>🍲 Feeding Tip:</strong><br>The 15-min lunch followed by a 1-hour gap is his safety shield against reflux.</div>
    """, unsafe_allow_html=True)

# 7. LIVE CHAT
st.divider()
st.subheader("💬 Chat with Archie's Jungle Guide")
if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask about Archie's day..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    model = genai.GenerativeModel('gemini-pro')
    ctx = f"Archie, 23mo. Location: {location}. Target 7am wake. Last night sleep {actual_night_sleep}h. Question: {prompt}"
    response = model.generate_content(ctx)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    with st.chat_message("assistant"): st.markdown(response.text)
