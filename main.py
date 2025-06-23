import os
import io
import json
import base64
import openai
import streamlit as st
import streamlit.components.v1 as components

# -------------------
# OpenAI API Key Setup
# -------------------
api_key_env = os.getenv("OPENAI_API_KEY", "")
api_key_input = ""
if not api_key_env:
    api_key_input = st.text_input("🔑 OpenAI API Key 입력 (sk-...)", type="password")
openai.api_key = api_key_input or api_key_env

# -------------------
# Helper Functions
# -------------------

def transcribe_audio(audio_bytes: bytes) -> str:
    """Whisper‑1로 음성 → 텍스트."""
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.wav"  # 파일명 필요
    try:
        result = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
            language="ko"
        )
        return result  # response_format=text 이면 str 반환
    except openai.AuthenticationError:
        st.error("❌ OpenAI API Key가 올바르지 않습니다.")
        st.stop()


def chat_with_gpt(prompt: str, history: list[dict]) -> str:
    """GPT‑4o로 대화 응답 생성."""
    messages = []
    for turn in history:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["bot"]})
    messages.append({"role": "user", "content": prompt})
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except openai.AuthenticationError:
        st.error("❌ OpenAI API Key가 올바르지 않습니다.")
        st.stop()


def speak(text: str) -> bytes:
    """gpt‑4o TTS (20대 남성 톤: alloy) → MP3 bytes 반환."""
    try:
        speech_resp = openai.audio.speech.create(
            model="gpt-4o-audio-preview",  # 최신 TTS 프리뷰 모델
            voice="alloy",                 # 자연스러운 젊은 남성 음색
            input=text,
            format="mp3",
        )
        return bytes(speech_resp)  # BinaryContent -> bytes
    except openai.AuthenticationError:
        st.error("❌ OpenAI API Key가 올바르지 않습니다.")
        st.stop()

# -------------------
# Streamlit UI
# -------------------
st.set_page_config(page_title="Voice Chatbot: 박종철", layout="centered")
st.title("🗣️ 1987년 박종철 음성 챗봇")

# 중심 영상 (assets/park_jongchul.mp4 위치에 파일 배치)
st.video("assets/park_jongchul.mp4", format="video/mp4")

# Session state for conversation
if "history" not in st.session_state:
    st.session_state.history = []

# Audio input (Streamlit ≥1.25)
st.subheader("🎤 마이크 녹음")
audio_data = st.audio_input("버튼을 눌러 질문을 녹음하세요")

if audio_data:
    # 1. STT
    user_text = transcribe_audio(audio_data.getbuffer())
    st.markdown(f"**🙋‍♂️ 사용자:** {user_text}")

    # 2. ChatGPT‑4o 응답
    bot_text = chat_with_gpt(user_text, st.session_state.history)
    st.markdown(f"**🤖 박종철:** {bot_text}")

    # 3. TTS (젊은 남성 음성)
    mp3_bytes = speak(bot_text)
    st.audio(mp3_bytes, format="audio/mp3")
    # 자동 재생
    b64 = base64.b64encode(mp3_bytes).decode()
    components.html(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', height=0)

    # 4. Save to history
    st.session_state.history.append({"user": user_text, "bot": bot_text})

# Conversation log & copy
if st.session_state.history:
    convo = "\n".join([
        f"사용자: {h['user']}\n박종철: {h['bot']}" for h in st.session_state.history
    ])
    st.text_area("📜 대화 내역", value=convo, height=250)
    if st.button("📋 대화 복사"):
        escaped = json.dumps(convo)
        components.html(
            f"<script>navigator.clipboard.writeText({escaped});</script>",
            height=0,
        )
        st.success("대화 내용이 클립보드에 복사되었습니다.")
