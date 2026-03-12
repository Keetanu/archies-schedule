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
    m1, m2, m3 = st.columns(3)
    m1.metric("Sleep", f"{night_hrs:.1f}h")
    m2.metric("Bedtime", bedtime_dt.strftime('%I:%M %p'))
    gap = (wake_dt - target_7am).total_seconds()/60
    m3.metric("7AM Gap", f"{gap:.0f}m")

    # WhatsApp Export with Date
    sched = [
        (wake_dt, "🥛 Wake + Milk"),
        (wake_dt + timedelta(minutes=25), "🍓 Morning Fruit"),
        (wake_dt + timedelta(hours=2), "🍳 Main Breakfast"),
        (nap_start_dt - timedelta(minutes=75), "🍚 Lunch (15m Feast)"),
        (nap_start_dt, f"😴 Nap Start ({w1_len}h Window)"),
        (nap_end_dt, "🎺 Wake Up (90m Nap)"),
        (nap_end_dt + timedelta(minutes=15), "🥨 Post-Nap Snack"),
        (nap_end_dt + timedelta(hours=1.5), "🏃 Peak Activity"),
        (dinner_dt, "🍲 Dinner (Recipe #11)"),
        (milk_dt, "🥛 Night Milk (1h post-dinner)"),
        (bedtime_dt, "✨ Bedtime (7h Window)")
    ]
    wa_date = today.strftime('%A, %b %d')
    wa_text = f"*🦁 Archie's Day - {wa_date}*\n" + "\n".join([f"• {t.strftime('%I:%M %p')}: {a}" for t, a in sched])
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_text)}" target="_blank" class="whatsapp-btn">📲 WhatsApp to Family</a>', unsafe_allow_html=True)

    # Tabs
    t_plan, t_graph, t_guide = st.tabs(["📜 Plan", "📊 Sleepy Meter", "💬 Jungle Chat"])

    with t_plan:
        df = pd.DataFrame(sched, columns=["Time", "Activity"])
        df["Time"] = df["Time"].apply(lambda x: x.strftime('%I:%M %p'))
        st.table(df)

    with t_graph:
        st.write("### 🔋 Archie's Sleep Pressure")
        times = [wake_dt + timedelta(hours=i) for i in range(16)]
        pressures = []
        for t in times:
            if t < nap_start_dt: p = ((t - wake_dt).total_seconds()/3600)*(100/w1_len)
            elif nap_start_dt <= t <= nap_end_dt: p = 15
            else: p = 20 + (((t - nap_end_dt).total_seconds()/3600)*(100/7.0))
            pressures.append(min(p, 100))
        st.area_chart(pd.DataFrame({'Pressure': pressures}, index=times), color="#4ade80")

    with t_guide:
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if pr := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": pr})
            with st.chat_message("user"): st.markdown(pr)
            try:
                genai.configure(api_key="AIzaSyCXHF51cAI9MC6cJUHNNPEYzlD5fhP_SLQ")
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"You are a kid-friendly sleep guide for 23mo Archie. Context: Wake {wake_time}. User asks: {pr}")
                if res.text:
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                    st.rerun()
            except Exception as e:
                st.error("Jungle Guide is taking a nap. Try again in a minute!")
else:
    st.info("🦁 Ready for a new day? Type Archie's times above (e.g. 0730) and click 'Generate'!")
 
