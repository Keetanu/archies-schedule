import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import urllib.parse

# 1. PLAYFUL JUNGLE THEME (Forcing Light Mode & Background)
st.set_page_config(page_title="Archie's Day", page_icon="🦁", layout="centered")

st.markdown("""
    <style>
    /* Jungle Background with Trees and Animals */
    .stApp {
        background-color: #f0fdf4;
        background-image: 
            url('https://www.transparenttextures.com/patterns/leaf.png'),
            radial-gradient(#dcfce7 1px, transparent 1px);
        background-size: 100px 100px, 20px 20px;
    }
    
    /* Removing the black box artifact */
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Kids-style Cards */
    .input-card, .recipe-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 30px;
        border: 5px solid #4ade80;
        box-shadow: 0 15px 25px -5px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }

    h1 { 
        color: #166534; 
        font-family: 'Comic Sans MS', cursive, sans-serif; 
        text-align: center; 
        text-shadow: 2px 2px #bbf7d0;
        font-size: 3rem;
    }

    /* Playful Jungle Buttons */
    .stButton>button {
        background: linear-gradient(to bottom, #4ade80, #22c55e);
        color: white;
        border-radius: 50px;
        border: 2px solid #166534;
        padding: 15px;
        font-size: 1.2rem;
        font-weight: bold;
        width: 100%;
    }

    /* Input Styling */
    input { 
        font-size: 1.5rem !important; 
        text-align: center; 
        border-radius: 15px !important; 
        border: 2px solid #86efac !important;
    }
    
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 18px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        display: block;
        text-align: center;
        font-size: 1.2rem;
        border: 3px solid #128C7E;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HELPER FUNCTIONS
def clean_time(t_str):
    if not t_str: return None
    clean = t_str.replace(":", "").strip()
    if len(clean) == 3 and clean.isdigit():
        clean = "0" + clean
    if len(clean) == 4 and clean.isdigit():
        try:
            hh, mm = int(clean[:2]), int(clean[2:])
            if 0 <= hh < 24 and 0 <= mm < 60: return time(hh, mm)
        except: return None
    return None

# 3. TOP-LEVEL CONTENT
st.markdown("<h1>🌳 🦁 🦒 🌳<br>Archie's Jungle</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("🍃 Morning Check-in")
    c1, c2 = st.columns(2)
    w_in = c1.text_input("☀️ Wake-up", "", placeholder="735")
    s_in = c2.text_input("🌙 Last Sleep", "", placeholder="2130")
    
    n_in = st.text_input("😴 Nap Started? (Optional)", "", placeholder="1300")
    
    with st.expander("🦉 Night Waking?"):
        nw_c1, nw_c2 = st.columns(2)
        nw_s_in = nw_c1.text_input("Woke", "", placeholder="200")
        nw_e_in = nw_c2.text_input("Slept", "", placeholder="245")
    
    lock = st.button("🌟 START THE ADVENTURE!")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. LOGIC ENGINE
if 'run' not in st.session_state: st.session_state.run = False
if lock: st.session_state.run = True

if st.session_state.run:
    wake_time = clean_time(w_in) or time(7, 0)
    sleep_time = clean_time(s_in) or time(21, 30)
    nap_manual = clean_time(n_in)
    today = datetime.today()
    wake_dt = datetime.combine(today, wake_time)
    prev_sleep_dt = datetime.combine(today - timedelta(days=1), sleep_time)
    target_7am = datetime.combine(today, time(7, 0))

    is_early = wake_dt < (target_7am - timedelta(minutes=90))
    w1_len = 5.5 if is_early else 6.0
    night_hrs = ((wake_dt - prev_sleep_dt).total_seconds() / 3600)
    
    nap_start_dt = datetime.combine(today, nap_manual) if nap_manual else wake_dt + timedelta(hours=w1_len)
    nap_end_dt = nap_start_dt + timedelta(minutes=90)
    
    dinner_dt = datetime.combine(today, time(19, 15))
    milk_dt = dinner_dt + timedelta(hours=1)
    bedtime_dt = max(nap_end_dt + timedelta(hours=7), milk_dt + timedelta(minutes=45))

    # DASHBOARD
    m1, m2, m3 = st.columns(3)
    m1.metric("Sleep", f"{night_hrs:.1f}h")
    m2.metric("Bedtime", bedtime_dt.strftime('%I:%M %p'))
    gap = (wake_dt - target_7am).total_seconds()/60
    m3.metric("Gap", f"{gap:.0f}m")

    # WHATSAPP
    sched = [(wake_dt, "🥛 Wake + Milk"), (wake_dt + timedelta(minutes=25), "🍓 Fruit"), (wake_dt + timedelta(hours=2), "🍳 Breakfast"), (nap_start_dt - timedelta(minutes=75), "🍚 Lunch"), (nap_start_dt, f"😴 Nap Start ({w1_len}h Window)"), (nap_end_dt, "🎺 Wake Up"), (nap_end_dt + timedelta(minutes=15), "🥨 Snack"), (nap_end_dt + timedelta(hours=1.5), "🏃 Activity"), (dinner_dt, "🍲 Dinner"), (milk_dt, "🥛 Night Milk"), (bedtime_dt, "✨ Bedtime (7h Window)")]
    wa_text = f"*🦁 Archie's Jungle Day - {today.strftime('%d %b')}*\n" + "\n".join([f"• {t.strftime('%I:%M %p')}: {a}" for t, a in sched])
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_text)}" target="_blank" class="whatsapp-btn">📲 Send to Jungle Family</a>', unsafe_allow_html=True)

    st.divider()

    # TABS
    t_plan, t_kitchen, t_graph, t_guide = st.tabs(["📜 Plan", "🥘 Kitchen", "🔋 Battery", "💬 Guide"])

    with t_plan:
        df = pd.DataFrame(sched, columns=["Time", "Activity"])
        df["Time"] = df["Time"].apply(lambda x: x.strftime('%I:%M %p'))
        st.table(df)

    with t_kitchen:
        st.subheader("🥘 Multi-Cuisine Jungle Kitchen")
        st.write("Balanced meals for a happy stomach!")
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**🍳 Breakfast:** Ragi Sheera OR Eggs/Toast")
            st.markdown("**🍚 Lunch:** Dal-Chawal OR Creamy Pasta")
        with colB:
            st.markdown("**🥨 Snack:** Makhana OR Apple/Butter")
            st.markdown("**🍲 Dinner:** Upma OR Mashed Potato/Fish")
        
        st.markdown(f"""
        <div class="recipe-card">
            <h3>🌟 Featured: Creamy Pumpkin Pasta</h3>
            <p>Gentle and filling. Great for dinner!</p>
            <a href="https://www.youtube.com/results?search_query=pumpkin+pasta+for+toddlers" target="_blank">📺 Watch Recipe</a>
        </div>
        """, unsafe_allow_html=True)

    with t_graph:
        st.subheader("🔋 Archie's Sleep Battery")
        times = [wake_dt + timedelta(hours=i) for i in range(16)]
        pressures = [min(((t - wake_dt).total_seconds()/3600)*(100/w1_len) if t < nap_start_dt else (15 if t <= nap_end_dt else 20 + (((t - nap_end_dt).total_seconds()/3600)*(100/7.0))), 100) for t in times]
        st.area_chart(pd.DataFrame({'Pressure': pressures}, index=times), color="#4ade80")

    with t_guide:
        st.subheader("💬 Ask the Jungle Guide")
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if pr := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": pr})
            with st.chat_message("user"): st.markdown(pr)
            try:
                genai.configure(api_key="AIzaSyCXHF51cAI9MC6cJUHNNPEYzlD5fhP_SLQ", transport='rest')
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                res = model.generate_content(f"You are a kid-friendly sleep guide for 23mo Archie. Context: Wake {wake_time}. Question: {pr}")
                if res.text:
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                    st.rerun()
            except Exception as e:
                st.error("Guide is sleeping. Try again later!")
else:
    st.info("🦁 Type Archie's wake-up (e.g., 715) and click Start!")
