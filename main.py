import os
import json
import openai
import streamlit as st

# --------------------
# OpenAI API KEY SETUP
# --------------------
api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key:
    api_key = st.text_input("🔑 OpenAI API Key (sk-...)", type="password")
openai.api_key = api_key

# ---------------
# Streamlit Setup
# ---------------
st.set_page_config(page_title="KakaoTalk Style GPT-4o Chatbot", layout="centered")

# Inject KakaoTalk-like CSS
st.markdown(
    """
<style>
#chat-box{max-width:400px;margin:0 auto;padding-bottom:80px}
.message{display:flex;margin:8px 0;font-size:15px;line-height:1.4}
.user .bubble{margin-left:auto;background:#007AFF;color:#fff;border-radius:15px 15px 3px 15px;padding:8px 12px;max-width:75%}
.bot .bubble{margin-right:auto;background:#FFE812;color:#000;border-radius:15px 15px 15px 3px;padding:8px 12px;max-width:75%}
#input-container{position:fixed;bottom:0;left:0;width:100%;background:#fff;padding:8px 0;box-shadow:0 -2px 4px rgba(0,0,0,.1)}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("<h2 style='text-align:center;'>🟡 KakaoTalk GPT-4o 챗봇</h2>", unsafe_allow_html=True)

# ------------------
# Session State Init
# ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {role, content}

# --------------
# Chat Container
# --------------
st.markdown('<div id="chat-box">', unsafe_allow_html=True)
for m in st.session_state.messages:
    role = m["role"]
    cls = "user" if role == "user" else "bot"
    st.markdown(f'<div class="message {cls}"><div class="bubble">{m["content"]}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------
# Input Field (Form)
# -------------------
with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_input("", key="msg_input", label_visibility="collapsed")
    submitted = st.form_submit_button("Send")

if submitted and user_text:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_text})

    # Prepare history for API
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o",
            messages=history,
            temperatu
