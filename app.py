import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta, time
import urllib.parse

# 1. THEME & SETTINGS
st.set_page_config(page_title="Archie's Day", page_icon="🦁", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0fdf4; background-image: url('https://www.transparenttextures.com/patterns/leaf.png'); }
    .input-card, .recipe-card, .feature-card { background-color: white; padding: 25px; border-radius: 30px; border: 4px solid #4ade80; margin-bottom: 20px; }
    h1 { color: #166534; font-family: 'Comic Sans MS', cursive; text-align: center; }
    .stButton>button { background: #22c55e; color: white; border-radius: 50px; font-weight: bold; width: 100%; }
    .whatsapp-btn { background-color: #25D366; color: white !important; padding: 15px; border-radius: 50px; text-decoration: none; font-weight: bold; display: block; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA & HELPERS
def clean_time(t_str):
    if not t_str: return None
    clean = t_str.replace(":", "").strip()
    if len(clean) == 3: clean = "0" + clean
    if len(clean) == 4 and clean.isdigit():
        try:
            hh, mm = int(clean[:2]), int(clean[2:])
            return time(hh, mm)
        except: return None
    return None

# 3. INPUT SECTION
st.markdown("<h1>🌳 Archie's Jungle 🦒</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    w_in = c1.text_input("☀️ Wake (625)", "")
    s_in = c2.text_input("🌙 Last Sleep", "")
    
    st.divider()
    recovery_mode = st.toggle("🤢 Recovery Mode (Upset Stomach Today)")
    lock = st.button("🌟 GENERATE ADVENTURE")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. LOGIC ENGINE
if lock or 'run' in st.session_state:
    st.session_state.run = True
    today = datetime.today()
    wake_time = clean_time(w_in) or time(6, 25)
    wake_dt = datetime.combine(today, wake_time)
    
    is_early = wake_time < time(6, 45)
    w1_len = 5.5 if is_early else 6.0
    
    nap_start_dt = wake_dt + timedelta(hours=w1_len)
    nap_end_dt = nap_start_dt + timedelta(minutes=90)
    snack_dt = nap_end_dt + timedelta(minutes=15)
    fruit_dt = snack_dt + timedelta(hours=2)
    
    dinner_dt = datetime.combine(today, time(19, 15))
    milk_dt = dinner_dt + timedelta(hours=1)
    bedtime_dt = max(nap_end_dt + timedelta(hours=7), milk_dt + timedelta(minutes=45))

    # TABS
    t_plan, t_kitchen, t_guide, t_features = st.tabs(["📜 Schedule", "🥘 Kitchen", "💬 Guide", "🚀 Features"])

    with t_plan:
        sched = [(wake_dt, "🥛 Wake + Milk"), (nap_start_dt, f"😴 Nap ({w1_len}h Window)"), (snack_dt, "🥨 Snack"), (fruit_dt, "🍎 Evening Fruit"), (dinner_dt, "🍲 Dinner"), (milk_dt, "🥛 Night Milk"), (bedtime_dt, "✨ Bedtime")]
        df = pd.DataFrame(sched, columns=["Time", "Activity"])
        df["Time"] = df["Time"].apply(lambda x: x.strftime('%H:%M'))
        st.table(df)
        
        wa_text = f"*🦁 Archie - {today.strftime('%d %b')}*\n" + "\n".join([f"• {t.strftime('%H:%M')}: {a}" for t, a in sched])
        st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(wa_text)}" target="_blank" class="whatsapp-btn">📲 WhatsApp Family</a>', unsafe_allow_html=True)

    with t_kitchen:
        if recovery_mode:
            st.warning("🤢 **Recovery Menu Active:** Focusing on low-acid, binding foods.")
            st.markdown("- **Breakfast:** Plain Rice Congee (Ganj) with a pinch of salt.")
            st.markdown("- **Dinner:** Mashed Banana and grated Apple (Pectin helps the stomach).")
        else:
            st.subheader("🍲 Multi-Cuisine Recipes")
            col1, col2 = st.columns(2)
            with col1:
                st.info("**Indian: Moong Dal Khichdi**")
                st.write("Overcook rice and dal with turmeric and ghee. (AH 'Snelkookrijst' works well).")
            with col2:
                st.success("**Global: Sweet Potato Mash**")
                st.write("Boil Dutch 'Zoete Aardappel', mash with a bit of butter/milk. Easy on gut.")

        st.markdown("""
        <div class="recipe-card">
        <h3>🛒 Rotterdam Shopping List</h3>
        <li><b>AH/Jumbo:</b> Volle Kwark (Probiotics), Zoete Aardappel, Flespompoen.</li>
        <li><b>Toko (Blaak/West):</b> Ragi Flour, Moong Dal, Jaggery (Gur).</li>
        </div>
        """, unsafe_allow_html=True)

    with t_guide:
        # Standard API Logic
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if pr := st.chat_input("Ask Archie's Guide..."):
            st.session_state.messages.append({"role": "user", "content": pr})
            try:
                genai.configure(api_key="AIzaSyCXHF51cAI9MC6cJUHNNPEYzlD5fhP_SLQ")
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"Archie 23mo. Recovery Mode: {recovery_mode}. {pr}")
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                st.rerun()
            except: st.error("Guide is offline.")

    with t_features:
        st.subheader("🚀 Future Jungle Upgrades")
        st.markdown("""
        1. **📊 Health Tracker:** Log daily 'stomach performance' to see if pasta or dal causes more issues.
        2. **📍 Toko Finder:** Integration with Google Maps to find the nearest Indian grocer in Rotterdam.
        3. **🔔 Live Alerts:** Browser notifications to remind you: *'Time for Evening Fruit!'*
        4. **📽️ Video Guide:** Short 15-second YouTube Shorts of the recipes playing directly in the app.
         """)
