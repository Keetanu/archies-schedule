import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import urllib.parse

# 1. SETUP & STABLE THEME
st.set_page_config(page_title="Archie's Schedule", page_icon="🦁", layout="centered") # Centered prevents right-side blankness

st.markdown("""
    <style>
    .main { background: #fdfdfd; }
    h1, h2, h3 { color: #2e7d32; font-family: 'Helvetica Neue', sans-serif; }
    .stMetric { background-color: #f1f8e9; padding: 15px; border-radius: 12px; border-bottom: 4px solid #4caf50; margin-bottom: 10px; }
    .whatsapp-btn { background-color: #25D366; color: white; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin: 10px 0; }
    .recovery-card { background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #e65100; font-weight: bold; }
    /* Fix for table visibility */
    .stTable { width: 100% !important; overflow-x: auto; }
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

# 3. SIDEBAR (Safe Inputs)
with st.sidebar:
    st.title("🦁 Jungle Controls")
    location = st.radio("📍 Location", ["India (IST)", "Netherlands (CET)"], index=1)
    
    st.divider()
    st.subheader("⌨️ HHMM Entry (e.g. 0730)")
    w_in = st.text_input("☀️ Wake-up", "0700")
    s_in = st.text_input("🌙 Last Night Sleep", "2130")
    
    with st.expander("🦉 Night Waking"):
        nw_s_in = st.text_input("Woke at", "")
        nw_e_in = st.text_input("Slept at", "")
    
    n_in = st.text_input("😴 Nap Started At (Optional)", "")
    st.divider()
    lock = st.button("🌿 LOCK & GENERATE", use_container_width=True, type="primary")

# 4. MAIN LOGIC
if 'generated' not in st.session_state:
    st.session_state.generated = False

if lock:
    st.session_state.generated = True

if st.session_state.generated:
    wake_time = clean_time(w_in) or time(7, 0)
    sleep_time = clean_time(s_in) or time(21, 30)
    nap_manual = clean_time(n_in)
    
    today = datetime.today()
    wake_dt = datetime.combine(today, wake_time)
    prev_sleep_dt = datetime.combine(today - timedelta(days=1), sleep_time)
    target_7am = datetime.combine(today, time(7, 0))

    # Night Waking logic
    nw_dur = 0
    nw_s, nw_e = clean_time(nw_s_in), clean_time(nw_e_in)
    if nw_s and nw_e:
        dt1, dt2 = datetime.combine(today, nw_s), datetime.combine(today, nw_e)
        if dt2 < dt1: dt2 += timedelta(days=1)
        nw_dur = (dt2 - dt1).total_seconds() / 3600

    # Recovery Mode (5 AM logic)
    is_early = wake_dt < (target_7am - timedelta(minutes=90))
    w1_length = 5.5 if is_early else 6.0
    
    # Schedule Math
    night_sleep_hrs = ((wake_dt - prev_sleep_dt).total_seconds() / 3600) - nw_dur
    nap_start_dt = datetime.combine(today, nap_manual) if nap_manual else wake_dt + timedelta(hours=w1_length)
    nap_end_dt = nap_start_dt + timedelta(minutes=90)
    
    # Evening Sequence
    dinner_dt = datetime.combine(today, time(19, 15))
    milk_dt = dinner_dt + timedelta(hours=1)
    bedtime_dt = max(nap_end_dt + timedelta(hours=7), milk_dt + timedelta(minutes=45))

    # DISPLAY (Sequential Layout to fix Blank Screen)
    st.title("🦁 Archie's Dashboard")
    
    if is_early:
        st.markdown(f"""<div class="recovery-card">⚠️ RECOVERY MODE ACTIVE: First window shortened to {w1_length}h.</div>""", unsafe_allow_html=True)

    # Metrics stacked or in simple columns
    col1, col2 = st.columns(2)
    col1.metric("Night Sleep", f"{night_sleep_hrs:.1f}h")
    col2.metric("Bedtime", bedtime_dt.strftime('%I:%M %p'))

    # WhatsApp (Full Width)
    sched = [
        (wake_dt, "🥛 Wake + Milk"),
        (wake_dt + timedelta(minutes=25), "🍓 Morning Fruit"),
        (wake_dt + timedelta(hours=2), "🍳 Breakfast"),
        (nap_start_dt - timedelta(minutes=75), "🍚 Lunch"),
        (nap_start_dt, f"😴 Nap Start ({w1_length}h window)"),
        (nap_end_dt, "🎺 Wake Up"),
        (nap_end_dt + timedelta(minutes=15), "🥨 Post-Nap Snack"),
        (nap_end_dt + timedelta(hours=1.5), "🏃 Peak Activity"),
        (dinner_dt, "🍲 Dinner (Recipe #11)"),
        (milk_dt, "🥛 Pre-Sleep Milk (1h after dinner)"),
        (bedtime_dt, "✨ Bedtime (7h window)")
    ]
    wa_text = f"*🦁 Archie - {today.strftime('%d %b')}*\n" + "\n".join([f"• {t.strftime('%I:%M %p')}: {a}" for t, a in sched])
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_text)}" target="_blank" class="whatsapp-btn">📲 Share via WhatsApp</a>', unsafe_allow_html=True)

    st.divider()

    # Plan Table (Full Width)
    st.subheader("📅 Daily Plan")
    df = pd.DataFrame(sched, columns=["Time", "Activity"])
    df["Time"] = df["Time"].apply(lambda x: x.strftime('%I:%M %p'))
    st.table(df)

    # Graph (Full Width)
    st.subheader("📈 Sleep Pressure Build-up")
    times = [wake_dt + timedelta(hours=i) for i in range(16)]
    pressures = []
    for t in times:
        if t < nap_start_dt: p = ((t - wake_dt).total_seconds()/3600)*(100/w1_length)
        elif nap_start_dt <= t <= nap_end_dt: p = 15
        else: p = 20 + (((t - nap_end_dt).total_seconds()/3600)*(100/7.0))
        pressures.append(min(p, 100))
    st.area_chart(pd.DataFrame({'Pressure': pressures}, index=times), color="#4caf50")

    st.divider()
    
    # Chat (Full Width)
    st.subheader("💬 Jungle Guide Chat")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("Ask about Archie's day..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        try:
            genai.configure(api_key="AIzaSyCXHF51cAI9MC6cJUHNNPEYzlD5fhP_SLQ")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"Archie 23mo. Wake: {wake_time}. {prompt}")
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"): st.markdown(response.text)
        except: st.error("Guide is offline.")

else:
    st.info("🦁 Enter HHMM times in the sidebar and click 'Lock & Generate'.")
