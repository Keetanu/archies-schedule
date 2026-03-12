import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import urllib.parse

# 1. MOBILE-OPTIMIZED SETUP
st.set_page_config(page_title="Archie's Day", page_icon="🦁", layout="centered")

st.markdown("""
    <style>
    .main { background: #fdfdfd; padding: 10px; }
    h1, h2, h3 { color: #2e7d32; font-family: 'Helvetica Neue', sans-serif; text-align: center; }
    .stMetric { background-color: #f1f8e9; padding: 10px; border-radius: 12px; border: 1px solid #a5d6a7; margin-bottom: 5px; }
    .whatsapp-btn { background-color: #25D366; color: white !important; padding: 15px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin: 20px 0; font-size: 1.1rem; }
    .input-box { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 1px solid #ddd; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .recovery-tag { background-color: #fff3e0; color: #e65100; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 0.8rem; display: inline-block; margin-bottom: 10px; }
    /* Table Fixes */
    .stTable { font-size: 14px !important; }
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

# 3. TOP-LEVEL INPUTS (Replacing Sidebar)
st.title("🦁 Archie's Day")

with st.container():
    st.markdown('<div class="input-box">', unsafe_allow_html=True)
    st.subheader("📝 Daily Entry (HHMM)")
    
    col1, col2 = st.columns(2)
    w_in = col1.text_input("☀️ Wake-up", "0700")
    s_in = col2.text_input("🌙 Last Sleep", "2130")
    
    n_in = st.text_input("😴 Nap Started (Optional)", "")
    
    with st.expander("🦉 Night Waking (Optional)"):
        nw_col1, nw_col2 = st.columns(2)
        nw_s_in = nw_col1.text_input("Woke at", "")
        nw_e_in = nw_col2.text_input("Slept at", "")

    location = st.selectbox("📍 Location", ["Netherlands (CET)", "India (IST)"], index=0)
    
    lock = st.button("🌿 LOCK & GENERATE SCHEDULE", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. LOGIC ENGINE
if 'gen' not in st.session_state: st.session_state.gen = False
if lock: st.session_state.gen = True

if st.session_state.gen:
    # Parsing
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

    # 5 AM Recovery Mode
    is_early = wake_dt < (target_7am - timedelta(minutes=90))
    w1_len = 5.5 if is_early else 6.0
    
    # Core Math
    night_hrs = ((wake_dt - prev_sleep_dt).total_seconds() / 3600) - nw_dur
    nap_start_dt = datetime.combine(today, nap_manual) if nap_manual else wake_dt + timedelta(hours=w1_len)
    nap_end_dt = nap_start_dt + timedelta(minutes=90)
    
    # Evening Sequence
    dinner_dt = datetime.combine(today, time(19, 15))
    milk_dt = dinner_dt + timedelta(hours=1)
    bedtime_dt = max(nap_end_dt + timedelta(hours=7), milk_dt + timedelta(minutes=45))

    # 5. DASHBOARD DISPLAY
    if is_early:
        st.markdown('<div class="recovery-tag">⚠️ RECOVERY MODE (5.5h Window)</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Sleep", f"{night_hrs:.1f}h")
    c2.metric("Bedtime", bedtime_dt.strftime('%I:%M %p'))
    gap = (wake_dt - target_7am).total_seconds()/60
    c3.metric("Gap", f"{gap:.0f}m")

    # WhatsApp Link
    sched = [
        (wake_dt, "🥛 Wake + Milk"),
        (wake_dt + timedelta(minutes=25), "🍓 Morning Fruit"),
        (wake_dt + timedelta(hours=2), "🍳 Breakfast"),
        (nap_start_dt - timedelta(minutes=75), "🍚 Lunch (15m Feast)"),
        (nap_start_dt, f"😴 Nap Start ({w1_len}h)"),
        (nap_end_dt, "🎺 Wake Up (90m Nap)"),
        (nap_end_dt + timedelta(minutes=15), "🥨 Post-Nap Snack"),
        (nap_end_dt + timedelta(hours=1.5), "🏃 Peak Activity"),
        (dinner_dt, "🍲 Dinner (Recipe #11)"),
        (milk_dt, "🥛 Night Milk (1h post-dinner)"),
        (bedtime_dt, "✨ Bedtime (7h window)")
    ]
    wa_text = f"*🦁 Archie - {today.strftime('%d %b')}*\n" + "\n".join([f"• {t.strftime('%I:%M %p')}: {a}" for t, a in sched])
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_text)}" target="_blank" class="whatsapp-btn">📲 WhatsApp Family</a>', unsafe_allow_html=True)

    # Tabs for clean mobile view
    tab_plan, tab_graph, tab_guide = st.tabs(["📅 Plan", "📈 Pressure", "💬 Guide"])

    with tab_plan:
        df = pd.DataFrame(sched, columns=["Time", "Activity"])
        df["Time"] = df["Time"].apply(lambda x: x.strftime('%I:%M %p'))
        st.table(df)

    with tab_graph:
        times = [wake_dt + timedelta(hours=i) for i in range(16)]
        pressures = []
        for t in times:
            if t < nap_start_dt: p = ((t - wake_dt).total_seconds()/3600)*(100/w1_len)
            elif nap_start_dt <= t <= nap_end_dt: p = 15
            else: p = 20 + (((t - nap_end_dt).total_seconds()/3600)*(100/7.0))
            pressures.append(min(p, 100))
        st.area_chart(pd.DataFrame({'Pressure': pressures}, index=times), color="#4caf50")

    with tab_guide:
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if prompt := st.chat_input("Ask Guide..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            try:
                genai.configure(api_key="AIzaSyCXHF51cAI9MC6cJUHNNPEYzlD5fhP_SLQ")
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"Archie 23mo. Wake {wake_time}. {prompt}")
                if res.text:
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                    st.rerun() # Single rerun to update chat bubble
            except:
                st.error("Jungle Guide is offline. Continue with the plan!")
else:
    st.info("🦁 Enter times above and click 'Generate' to see Archie's schedule.")
