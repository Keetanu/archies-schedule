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
    .stTextInput input { font-size: 1.2rem; font-weight: bold; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# Helper for 4-digit parsing
def clean_time(t_str):
    if not t_str: return None
    t_str = t_str.replace(":", "").strip()
    if len(t_str) == 4 and t_str.isdigit():
        hh, mm = int(t_str[:2]), int(t_str[2:])
        if 0 <= hh < 24 and 0 <= mm < 60:
            return time(hh, mm)
    return None

# 2. SIDEBAR INPUTS
with st.sidebar:
    st.title("🦁 Jungle Controls")
    location = st.radio("📍 Location", ["India (IST)", "Netherlands (CET)"], index=1)
    
    st.divider()
    st.subheader("⌨️ Enter 4 Digits (HHMM)")
    
    w_in = st.text_input("☀️ Wake-up", "0700")
    s_in = st.text_input("🌙 Last Night Sleep", "2130")
    
    with st.expander("🦉 Night Waking"):
        nw_s_in = st.text_input("Woke at", "")
        nw_e_in = st.text_input("Slept at", "")
    
    n_in = st.text_input("😴 Nap Started At (Optional)", "")
    
    st.divider()
    lock = st.button("🌿 LOCK & GENERATE", use_container_width=True, type="primary")

# 3. LOGIC ENGINE
if lock or 'init' not in st.session_state:
    st.session_state.init = True
    
    wake_time = clean_time(w_in) or time(7, 0)
    prev_sleep_time = clean_time(s_in) or time(21, 30)
    n_wake_s, n_wake_e = clean_time(nw_s_in), clean_time(nw_e_in)
    nap_manual = clean_time(n_in)

    today = datetime.today()
    wake_dt = datetime.combine(today, wake_time)

    # Night Waking Math
    nw_dur = 0
    if n_wake_s and n_wake_e:
        dt1, dt2 = datetime.combine(today, n_wake_s), datetime.combine(today, n_wake_e)
        if dt2 < dt1: dt2 += timedelta(days=1)
        nw_dur = (dt2 - dt1).total_seconds() / 3600

    # Sleep Math
    sleep_dt = datetime.combine(today - timedelta(days=1), prev_sleep_time)
    night_sleep = ((wake_dt - sleep_dt).total_seconds() / 3600) - nw_dur
    
    # WINDOW LOGIC
    # Window 1: 6 hours
    nap_start_dt = datetime.combine(today, nap_manual) if nap_manual else wake_dt + timedelta(hours=6)
    nap_end_dt = nap_start_dt + timedelta(minutes=90)
    
    # Evening Sequence
    # Dinner usually starts around 7:15 PM or based on nap end
    dinner_dt = datetime.combine(today, time(19, 15))
    # Ensure milk is 1 hour after dinner start
    milk_dt = dinner_dt + timedelta(hours=1)
    # Bedtime is roughly 1 hour after milk to maintain the 7h window from nap end
    bedtime_dt = nap_end_dt + timedelta(hours=7)
    
    # Adjusting dinner if the 7h window makes bedtime too early/late
    if bedtime_dt < (milk_dt + timedelta(minutes=45)):
        bedtime_dt = milk_dt + timedelta(minutes=45)

    # 4. DASHBOARD
    st.title(f"🦁 Archie's Day: {location}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Night Sleep", f"{night_sleep:.1f}h")
    c2.metric("Target Bedtime", bedtime_dt.strftime('%I:%M %p'))
    c3.metric("Window 1 / 2", "6h / 7h")

    # WhatsApp
    sched = [
        (wake_dt, "🥛 Wake + Milk"),
        (wake_dt + timedelta(minutes=25), "🍓 Morning Fruit"),
        (wake_dt + timedelta(hours=2), "🍳 Main Breakfast"),
        (nap_start_dt - timedelta(minutes=75), "🍚 Lunch (15m Feast)"),
        (nap_start_dt, "😴 Nap Start (6h Window)"),
        (nap_end_dt, "🎺 Hard Wake (90m Nap)"),
        (nap_end_dt + timedelta(minutes=15), "🥨 Post-Nap Snack"),
        (nap_end_dt + timedelta(hours=1.5), "🏃 PEAK ACTIVITY ZONE"),
        (nap_end_dt + timedelta(hours=2.5), "🍌 Afternoon Fruit"),
        (dinner_dt, "🍲 Dinner (Recipe #11)"),
        (milk_dt, "🥛 Pre-Sleep Milk (1h after Dinner)"),
        (bedtime_dt, "✨ Bedtime (7h Window)")
    ]
    wa_msg = f"*🦁 Archie's Day*\n" + "\n".join([f"• {t.strftime('%I:%M %p')}: {a}" for t, a in sched])
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_msg)}" target="_blank" class="whatsapp-btn">📲 Share Schedule</a>', unsafe_allow_html=True)

    st.divider()
    t1, t2, t3 = st.tabs(["📅 Plan", "📈 Sleep Pressure", "💬 Guide"])

    with t1:
        df = pd.DataFrame(sched, columns=["Time", "Activity"])
        df["Time"] = df["Time"].apply(lambda x: x.strftime('%I:%M %p'))
        st.table(df)

    with t2:
        st.subheader("Adenosine (Sleep Pressure) Sequential Timeline")
        total_h = int((bedtime_dt - wake_dt).total_seconds() / 3600) + 2
        times = [wake_dt + timedelta(hours=i) for i in range(total_h)]
        pressures = []
        for t in times:
            if t < nap_start_dt: val = ((t - wake_dt).total_seconds()/3600)*16.6
            elif nap_start_dt <= t <= nap_end_dt: val = 15
            else: val = 20 + (((t - nap_end_dt).total_seconds()/3600)*(100/7.0))
            pressures.append(min(val, 100))
        st.area_chart(pd.DataFrame({'Pressure': pressures}, index=times), color="#4caf50")

    with t3:
        try:
            genai.configure(api_key="AIzaSyAtlrIyT0LrtmGetXY-bGuEKJHufvzdF-0")
            model = genai.GenerativeModel('gemini-1.5-flash')
            if "messages" not in st.session_state: st.session_state.messages = []
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])
            if pr := st.chat_input("Ask the Guide..."):
                st.session_state.messages.append({"role": "user", "content": pr})
                with st.chat_message("user"): st.markdown(pr)
                resp = model.generate_content(f"Archie 23mo. {pr}")
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
                st.rerun()
        except: st.warning("Guide sleeping. Try again later.")
