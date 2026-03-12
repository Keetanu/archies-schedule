import streamlit as st
import google.generativeai as genai
from google.generativeai.types import RequestOptions
import pandas as pd
from datetime import datetime, timedelta, time
import urllib.parse

# 1. PLAYFUL JUNGLE THEME
st.set_page_config(page_title="Archie's Day", page_icon="🦁", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0fdf4; background-image: url('https://www.transparenttextures.com/patterns/leaf.png'); }
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    .input-card { background-color: white; padding: 25px; border-radius: 30px; border: 5px solid #4ade80; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 20px; }
    h1 { color: #166534; font-family: 'Comic Sans MS', cursive; text-align: center; font-size: 2.8rem; }
    .stButton>button { background: #22c55e; color: white; border-radius: 50px; border: none; padding: 15px; font-weight: bold; width: 100%; font-size: 1.1rem; }
    .whatsapp-btn { background-color: #25D366; color: white !important; padding: 15px; border-radius: 50px; text-decoration: none; font-weight: bold; display: block; text-align: center; }
    input { font-size: 1.2rem !important; text-align: center; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. HELPER FUNCTIONS
def clean_time(t_str):
    if not t_str: return None
    clean = t_str.replace(":", "").strip()
    if len(clean) == 3 and clean.isdigit(): clean = "0" + clean
    if len(clean) == 4 and clean.isdigit():
        try:
            hh, mm = int(clean[:2]), int(clean[2:])
            if 0 <= hh < 24 and 0 <= mm < 60: return time(hh, mm)
        except: return None
    return None

# 3. INPUT SECTION
st.markdown("<h1>🌳 🦁 🦒 🌳<br>Archie's Jungle</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("🍃 Morning Check-in")
    c1, c2 = st.columns(2)
    w_in = c1.text_input("☀️ Wake (e.g. 735)", "")
    s_in = c2.text_input("🌙 Sleep (e.g. 2130)", "")
    n_in = st.text_input("😴 Nap Started? (Optional)", "")
    lock = st.button("🌟 START ADVENTURE")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. LOGIC ENGINE
if lock or 'run' in st.session_state:
    st.session_state.run = True
    today = datetime.today()
    
    wake_time = clean_time(w_in) or time(7, 0)
    sleep_time = clean_time(s_in) or time(21, 30)
    nap_manual = clean_time(n_in)

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
    m2.metric("Bedtime", bedtime_dt.strftime('%H:%M'))
    gap = (wake_dt - target_7am).total_seconds()/60
    m3.metric("Gap", f"{gap:.0f}m")

    # WHATSAPP
    sched = [(wake_dt, "🥛 Wake + Milk"), (wake_dt + timedelta(minutes=25), "🍓 Fruit"), (wake_dt + timedelta(hours=2), "🍳 Breakfast"), (nap_start_dt - timedelta(minutes=75), "🍚 Lunch"), (nap_start_dt, f"😴 Nap Start ({w1_len}h Window)"), (nap_end_dt, "🎺 Wake Up"), (nap_end_dt + timedelta(minutes=15), "🥨 Snack"), (dinner_dt, "🍲 Dinner"), (milk_dt, "🥛 Night Milk"), (bedtime_dt, "✨ Bedtime (7h Window)")]
    wa_text = f"*🦁 Archie - {today.strftime('%d %b')}*\n" + "\n".join([f"• {t.strftime('%H:%M')}: {a}" for t, a in sched])
    st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_text)}" target="_blank" class="whatsapp-btn">📲 WhatsApp Family</a>', unsafe_allow_html=True)

    st.divider()

    t_plan, t_kitchen, t_guide = st.tabs(["📜 Plan", "🥘 Kitchen", "💬 Guide"])

    with t_plan:
        df = pd.DataFrame(sched, columns=["Time", "Activity"])
        df["Time"] = df["Time"].apply(lambda x: x.strftime('%H:%M'))
        st.table(df)

    with t_kitchen:
        st.subheader("🥘 Archie's Menu")
        st.markdown("**🍳 Breakfast:** Ragi Sheera / Scrambled Eggs")
        st.markdown("**🍚 Lunch:** Moong Dal Khichdi / Pumpkin Pasta")
        st.markdown("**🍲 Dinner:** Vegetable Upma / Mashed Potatoes & Cod")
        st.caption("Tip: Use 'Volle Kwark' from Jumbo/AH as a probiotic curd substitute.")

    with t_guide:
        st.subheader("💬 Ask the Guide")
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if pr := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": pr})
            with st.chat_message("user"): st.markdown(pr)
            try:
                # BYPASSING v1beta EXPLICITLY
                genai.configure(api_key="AIzaSyCXHF51cAI9MC6cJUHNNPEYzlD5fhP_SLQ")
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Using v1 stable options
                res = model.generate_content(
                    f"You are Archie's kid-friendly sleep guide. Context: Wake {wake_time}. Question: {pr}",
                    request_options=RequestOptions(api_version='v1')
                )
                
                if res and res.text:
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                    st.rerun()
            except Exception as e:
                st.error(f"Guide is resting: {str(e)}")
else:
    st.info("🦁 Enter Archie's wake-up (e.g., 735) and click Start!")
