import os
import json
import openai
import streamlit as st

# --------------------
# OpenAI API KEY SETUP
# --------------------
api_key_env = os.getenv("OPENAI_API_KEY", "")
if not api_key_env:
    api_key_env = st.text_input("🔑 OpenAI API Key (sk-...)", type="password")
openai.api_key = api_key_env

# ---------------
# Streamlit Setup
# ---------------
st.set_page_config(page_title="KakaoTalk Style GPT‑4o Chatbot", layout="centered")

# Inject KakaoTalk‑like CSS
kakao_css = """
<style>
/* Chat container */
#chat-box {
  max-width: 400px;
  margin: 0 auto;
  padding-bottom: 80px; /* space for input */
}
/* Message common */
.message {
  display: flex;
  margin: 8px 0;
  font-size: 15px;
  line-height: 1.4;
}
/* User bubble (blue) */
.user .bubble {
  margin-left: auto;
  background: #007AFF;
  color: white;
  border-radius: 15px 15px 3px 15px;
  padding: 8px 12px;
  max-width: 75%;
}
/* Bot bubble (yellow) */
.bot .bubble {
  margin-right: auto;
  background: #FFE812;
  color: black;
  border-radius: 15px 15px 15px 3px;
  padding: 8px 12px;
  max-width: 75%;
}
/* Input box fixed at bottom */
#input-container {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: white;
  padding: 10px 0;
  box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
}
#input-container input {
  width: 380px;
  max-width: 90%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
  font-size: 15px;
}
</style>
"""
st.markdown(kakao_css, unsafe_allow_html=True)

# -----------
# App Header
# -----------
st.markdown("<h2 style='text-align:center;'>🟡 KakaoTalk GPT‑4o 챗봇</h2>", unsafe_allow_html=True)

# ------------------
# Session State Init
# ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {role, content}

# --------------
# Chat Container
# --------------
with st.container():
    st.markdown('<div id="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        cls = "user" if role == "user" else "bot"
        html = f'<div class="message {cls}"><div class="bubble">{content}</div></div>'
        st.markdown(html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------
# Input Field at Bottom
# -------------------
user_input = st.text_input("", key="user_input", label_visibility="collapsed")

if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Compose messages for OpenAI API
    messages_for_api = []
    for m in st.session_state.messages:
        messages_for_api.append({"role": m["role"], "content": m["content"]})

    # GPT‑4o completion
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages_for_api,
            temperature=0.7,
            max_tokens=200,
        )
        bot_reply = resp.choices[0].message.content.strip()
    except Exception as e:
        bot_reply = f"(오류 발생: {e})"
    # Append bot message
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # Rerun to refresh chat display
    st.experimental_rerun()
