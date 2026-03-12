import streamlit as st
import google.generativeai as genai
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
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR COMMAND CENTER
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/jungle.png")
    st.header("🌳 Jungle Settings")
    
    location = st.radio("📍 Current Jungle", ["India (IST)", "Netherlands (CET)"], index=0)
    is_netherlands = location == "Netherlands (CET)"
    
    st.divider()
    
    wake_time = st.time_input("☀️ Morning Wake-up", value=time(7, 0))
    prev_sleep_time = st.time_input("🌙 Previous Night Sleep", value=time(21, 30))
    
    st.subheader("🦉 Night Waking")
    night_wake_start = st.time_input("Woke up at", value=None)
    night_wake_end = st.time_input("Back to sleep at", value=None)
    
    st.subheader("😴 Daytime Nap")
    nap_start = st.time_input("Nap Started At (Optional)", value=None)
    
    recalculate = st.button("🌿 Update Archie's Day")

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

# Night Sleep Duration
sleep_dt = datetime.combine(today - timedelta(days=1), prev_sleep_time)
actual_night_sleep = ((wake_dt - sleep_dt).total_seconds() / 3600) - night_wake_duration

# Schedule Calculations (23 months age logic)
nap_buffer = 6 if night_wake_duration < 0.5 else 5.5
nap_start_rec = wake_dt + timedelta(hours=nap_buffer)
nap_start_actual = datetime.combine(today, nap_start) if nap_start else nap_start_rec
nap_end_dt = nap_start_actual + timedelta(minutes=90)
bedtime_dt = nap_end_dt + timedelta(hours=6)

# 4. DASHBOARD
st.title(f"🦁 Archie's {location} Schedule")

c1, c2, c3 = st.columns(3)
with c1: st.metric("Actual Night Sleep", f"{actual_night_sleep:.1f} hrs")
with c2: st.metric("Night Wake Time", f"{night_wake_duration*60:.0f} mins")
with c3: st.metric("Target Bedtime", bedtime_dt.strftime('%I:%M %p'))

st.divider()

# 5. UPDATED FEEDING & ACTIVITY SCHEDULE
tab_col, info_col = st.columns([2, 1])

with tab_col:
    st.subheader("📅 The Golden Path (Feeding & Sleep)")
    
    # Building the sequence based on User's description
    sched = [
        {"Time": wake_dt.strftime('%I:%M %p'), "Activity": "🥛 Wake Up + Immediate Milk"},
        {"Time": (wake_dt + timedelta(minutes=20)).strftime('%I:%M %p'), "Activity": "🍓 Morning Fruit Snack"},
        {"Time": (wake_dt + timedelta(hours=2)).strftime('%I:%M %p'), "Activity": "🍳 Main Breakfast (Tiger Power)"},
        {"Time": (nap_start_actual - timedelta(hours=1, minutes=15)).strftime('%I:%M %p'), "Activity": "🍚 Lunch (15-min Feast)"},
        {"Time": nap_start_actual.strftime('%I:%M %p'), "Activity": "😴 Nap Start (Sloth Mode)"},
        {"Time": nap_end_dt.strftime('%I:%M %p'), "Activity": "🎺 Hard Wake (Slow Fade)"},
        {"Time": (nap_end_dt + timedelta(minutes=15)).strftime('%I:%M %p'), "Activity": "🥨 Post-Nap Snack"},
        {"Time": (nap_end_dt + timedelta(hours=2)).strftime('%I:%M %p'), "Activity": "🍌 Afternoon Fruit"},
        {"Time": "07:15 PM", "Activity": "🍲 Dinner (Recipe #11 / Slow Carbs)"},
        {"Time": (bedtime_dt - timedelta(hours=1)).strftime('%I:%M %p'), "Activity": "🥛 Pre-Sleep Night Milk"},
        {"Time": bedtime_dt.strftime('%I:%M %p'), "Activity": "✨ Starry Night (Bedtime)"}
    ]
    st.table(sched)

with info_col:
    st.subheader("💡 Jungle Wisdom")
    location_advice = "Focus on 4:30 PM sunlight in Rotterdam to lock in the timezone!" if is_netherlands else "Keep the room cool; India's heat can cause early wakes."
    st.markdown(f"""
    <div class="info-card"><strong>🌍 Location Advice:</strong><br>{location_advice}</div>
    <div class="info-card"><strong>🍲 Digestion Tip:</strong><br>The 1-hour gap between lunch and nap is perfect to avoid reflux during sleep.</div>
    <div class="info-card"><strong>⚠️ Alert:</strong><br>If he only ate for 15 mins at lunch, ensure the post-nap snack is high-calorie.</div>
    """, unsafe_allow_html=True)

# 6. LIVE CHAT
st.divider()
st.subheader("💬 Chat with Archie's Jungle Guide")
if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask about Archie's day..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    model = genai.GenerativeModel('gemini-pro')
    ctx = f"Archie, 23mo. Location: {location}. Feeding: 7-step grazing cycle. Context: {prompt}"
    response = model.generate_content(ctx)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    with st.chat_message("assistant"): st.markdown(response.text)
