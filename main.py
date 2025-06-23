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

st.markdown("<h2 style='text-align:center;'>🟡 KakaoTalk GPT‑4o 챗봇</h2>", unsafe_allow_html=True)

# ------------------
# Session State Init
# ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {role, content}

# Random human name once per session
if "human_name" not in st.session_state:
    import random
    names = ["민수", "영호", "철수", "진호", "성민", "동훈"]
    st.session_state.human_name = random.choice(names)

# System prompt (insert once)
if not any(m["role"] == "system" for m in st.session_state.messages):
    system_prompt = (
        f"너는 80년대 대한민국의 민주화 운동에 참여한 20대 남성이다. "
        f"너는 인공지능이라는 표현을 절대 사용하지 말고 자신을 사람이라고 설명해라. "
        f"너의 이름은 {st.session_state.human_name}이다. "
        f"모든 응답은 두 문장 이내로 해라."
    )
    st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})

# --------------
# Chat Container
# --------------
st.markdown('<div id="chat-box">', unsafe_allow_html=True)
for m in st.session_state.messages:
    if m["role"] == "system":
        continue  # 시스템 프롬프트는 표시하지 않음
    role = m["role"]
    cls = "user" if role == "user" else "bot"
    st.markdown(
        f'<div class="message {cls}"><div class="bubble">{m["content"]}</div></div>',
        unsafe_allow_html=True,
    )
st.markdown('</div>', unsafe_allow_html=True)

# -------------------
# Input Field (Form)
# -------------------
with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_input(
        "메시지를 입력하세요",
        key="msg_input",
        label_visibility="collapsed",
        placeholder="메시지를 입력하세요",
    )
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
            temperature=0.7,
            max_tokens=200,
        )
        bot_reply = resp.choices[0].message.content.strip()
    except Exception as e:
        bot_reply = f"(오류: {e})"

    # Append bot reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # Rerun to refresh chat display
    st.rerun()
