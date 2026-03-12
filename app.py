import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta

# 1. SETUP & JUNGLE THEME
st.set_page_config(page_title="Archie's Schedule", page_icon="🦁")
st.markdown("""
    <style>
    .main { background-color: #f0f5f1; }
    h1 { color: #2e7d32; font-family: 'Trebuchet MS'; }
    .stButton>button { background-color: #4caf50; color: white; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦁 Archie's Schedule")

# 2. INPUTS
with st.sidebar:
    st.header("🌳 Jungle Inputs")
    wake_time = st.time_input("Morning Wake-up", value=datetime.strptime("07:00", "%H:%M"))
    nap_start = st.time_input("Nap Started At")
    
    st.divider()
    st.header("🍲 Meal Log")
    meal = st.selectbox("Last Meal", ["Breakfast", "Lunch", "Snack", "Dinner"])
    status = st.radio("How did he eat?", ["Great", "Pickys", "Refused"])

# 3. AGE-BASED LOGIC (23 Months)
# Calculation: 90 min nap + 6 hour wake window
nap_end_dt = datetime.combine(datetime.today(), nap_start) + timedelta(minutes=90)
bedtime_dt = nap_end_dt + timedelta(hours=6)

# 4. DASHBOARD DISPLAY
col1, col2 = st.columns(2)
with col1:
    st.metric("Nap End (Hard Wake)", nap_end_dt.strftime('%I:%M %p'))
    st.caption("Target 90 mins to protect night sleep")
with col2:
    st.metric("Bedtime Goal", bedtime_dt.strftime('%I:%M %p'))
    st.caption("Ensures 6h wake window")

st.subheader("📅 Remaining Daily Plan")
st.write(f"☀️ **Sunlight Walk:** { (nap_end_dt + timedelta(minutes=30)).strftime('%I:%M %p') }")
st.write(f"🥩 **Dinner (Tiger Fuel):** { (bedtime_dt - timedelta(hours=2)).strftime('%I:%M %p') }")
st.write(f"🥛 **Milk Bridge:** { (bedtime_dt - timedelta(minutes=45)).strftime('%I:%M %p') }")

# 5. LIVE GEMINI CHAT BOX
st.divider()
st.subheader("💬 Chat with Gemini")
api_key = st.text_input("Enter Gemini API Key to Chat", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about Archie's mood or meals..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        response = model.generate_content(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
