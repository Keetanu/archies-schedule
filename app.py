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
    .whatsapp-btn { background-color: #25D366; color: white; padding: 10px 20px; border-radius: 10px; text-decoration: none; font-weight: bold; display: inline-block; }
    .time-hint { color: #666; font-size: 0.85rem; margin-top: -15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Helper function for Real-Time Parsing
def parse_manual_time(t_str):
    if not t_str or len(t_str) != 4 or not t_str.isdigit():
        return None
    try:
        hh = int(t_str[:2])
        mm = int(t_str[2:])
        if 0 <= hh < 24 and 0 <= mm < 60:
            return time(hh, mm)
    except:
        return None
    return None

# 2. SIDEBAR INPUTS
with st.sidebar:
    st.title("🦁 Jungle Controls")
    location = st.radio("📍 Location", ["India (IST)", "Netherlands (CET)"], index=1)
    st.divider()
    
    st.subheader("⌨️ Manual Entry (HHMM)")
    
    # Wake Up Input + Real Time Feedback
    wake_str = st.text_input("☀️ Actual Wake-up", "0700", help="Type 4 digits, e.g., 0615")
    wake_parsed = parse_manual_time(wake_str)
    if wake_parsed:
        st.markdown(f"<div class='time-hint'>✅ Interpreted: {wake_parsed.strftime('%I:%M %p')}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='time-hint'>❌ Enter 4 digits (e.g. 0700)</div>", unsafe_allow_html=True)

    # Sleep Input + Real Time Feedback
    prev_sleep_str = st.text_input("🌙 Last Night Sleep", "2130")
    sleep_parsed = parse_manual_time(prev_sleep_str)
    if sleep_parsed:
        st.markdown(f"<div class='time-hint'>✅ Interpreted: {sleep_parsed.strftime('%I:%M %p')}</div>", unsafe_allow_html=True)

    with st.expander("🦉 Night Waking"):
        n_start_str = st.text_input("Woke at", "")
        n_end_str = st.text_input("Slept at", "")
    
    nap_str = st.text_input("😴 Nap Started At", "")
    nap_parsed = parse_manual_time(nap_str)
    if nap_parsed:
        st.markdown(f"<div class='time-hint'>✅ Interpreted: {nap_parsed.strftime('%I:%M %p')}</div>", unsafe_allow_html=True)

    st.divider()
    # THE LOCK BUTTON
    generate = st.button("🌿 LOCK & GENERATE SCHEDULE", use_container_width=True, type="primary")

# 3. LOGIC ENGINE (Triggered by button)
if generate or 'init' not in st.session_state:
    st.session_state.init = True
    
    # Finalize times
    wake_time = wake_parsed if wake_parsed else time(7, 0)
    prev_sleep_time = sleep_parsed if sleep_parsed else time(21, 30)
    n_wake_start = parse_manual_time(n_start_str)
    n_wake_end = parse_manual_time(n_end_str)
    nap_start_manual = nap_parsed

    today = datetime.today()
    wake_dt = datetime.combine(today, wake_time)

    # Night Waking Math
    night_wake_duration = 0
    if n_wake_start and n_wake_end:
        start_dt = datetime.combine(today, n_wake_start)
        end_dt = datetime.combine(today, n_wake_end)
        if end_dt < start_dt: end_dt += timedelta(days=1)
        night_wake_duration = (end_dt - start_dt).total_seconds() / 3600

    # Sleep Math
    sleep_dt = datetime.combine(today - timedelta(days=1), prev_sleep_time)
    actual_night_sleep = ((wake_dt - sleep_dt).total_seconds() / 3600) - night_wake_duration
    
    # Archie (23mo) Nap/Bedtime Rules
    nap_buffer = 6 if night_wake_duration < 0.5 else 5.5
    nap_start_actual = datetime.combine(today, nap_start_manual) if nap_start_manual else wake_dt + timedelta(hours=6)
    nap_end_dt = nap_start_actual + timedelta(minutes=90)
    bedtime_dt = nap_end_dt + timedelta(hours=6)

    # 4. DASHBOARD
    st.title(f"🦁 Archie's Day: {location}")

    m1, m2, m3 = st.columns(3)
    # Target 10:30 - 11:00 hours
    sleep_color = "normal" if 10.5 <= actual_night_sleep <= 11.5 else "inverse"
    m1.metric("Night Sleep", f"{actual_night_sleep:.1f}h", delta=f"{actual_night_sleep-10.75:.1f}h vs Ideal")
    m2.metric("Target Bedtime", bedtime_dt.strftime('%I:%M %p'))
    gap_val = (wake_dt - datetime.combine(today, time(7,0))).total_seconds()/60
    m3.metric("7AM Gap", f"{gap_val:.0f}m", delta=f"{gap_val}m from target", delta_color="inverse")

    # Schedule Data
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
    
    wa_msg = f"*🦁 Archie's Schedule*\n" + "\n".join([f"• {t.strftime('%I:%M %p')}: {a}" for t, a in sched_list])
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}" target="_blank" class="whatsapp-btn">📲 Share via WhatsApp</a>', unsafe_allow_html=True)

    st.divider()

    tab1, tab2, tab3 = st.tabs(["📅 Daily Plan", "📈 Sleep Pressure", "💬 Jungle Guide"])

    with tab1:
        df_sched = pd.DataFrame(sched_list, columns=["Time", "Activity"])
        df_sched["Time"] = df_sched["Time"].apply(lambda x: x.strftime('%I:%M %p'))
        st.table(df_sched)

    with tab2:
        st.subheader("Adenosine (Sleep Pressure) Sequential Timeline")
        total_h = int((bedtime_dt - wake_dt).total_seconds() / 3600) + 2
        chart_times = [wake_dt + timedelta(hours=i) for i in range(total_h)]
        pressures = []
        for t in chart_times:
            if t < nap_start_actual: val = ((t - wake_dt).total_seconds()/3600)*15
            elif nap_start_actual <= t <= nap_end_dt: val = 10
            else: val = 20 + (((t - nap_end_dt).total_seconds()/3600)*12)
            pressures.append(min(val, 100))
        st.area_chart(pd.DataFrame({'Pressure': pressures}, index=chart_times), color="#4caf50")

    with tab3:
        try:
            genai.configure(api_key="AIzaSyAtlrIyT0LrtmGetXY-bGuEKJHufvzdF-0")
            model = genai.GenerativeModel('gemini-1.5-flash')
            if "messages" not in st.session_state: st.session_state.messages = []
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            if prompt := st.chat_input("Ask Archie's Jungle Guide..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.markdown(prompt)
                ctx = f"Archie 23mo. Sleep: {actual_night_sleep}h. Gap: {gap_val}m. {prompt}"
                response = model.generate_content(ctx)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
        except Exception as e:
            st.warning("Chat unavailable. Check  API connection.")
