import os
import io
import json
import openai
import base64
import streamlit as st
import streamlit.components.v1 as components

# OpenAI API 키 설정
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key
else:
    input_key = st.text_input("OpenAI API Key를 입력하세요:", type="password")
    if input_key:
        openai.api_key = input_key
        os.environ["OPENAI_API_KEY"] = input_key
    else:
        st.warning("API 키를 입력해야 합니다.")


def transcribe_audio(audio_bytes):
    """
    Whisper v1 모델로 오디오 바이트를 텍스트로 변환합니다.
    """
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        transcript = openai.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file
        )
        return transcript.text.strip()
    except openai.error.AuthenticationError:
        st.error("유효하지 않은 OpenAI API 키입니다. 다시 확인해주세요.")
        st.stop()


def chat_with_gpt(prompt, history):
    """
    GPT-4o 모델로 대화 응답을 생성합니다.
    """
    try:
        messages = []
        for turn in history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["bot"]})
        messages.append({"role": "user", "content": prompt})
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except openai.error.AuthenticationError:
        st.error("유효하지 않은 OpenAI API 키입니다. 다시 확인해주세요.")
        st.stop()

# Streamlit 앱 설정
st.set_page_config(page_title="Voice Chatbot: 박종철", layout="centered")
st.header("음성 챗봇: 박종철 (1987년 대한민국)")

# 중앙 영상 재생
st.video("assets/park_jongchul.mp4", format="video/mp4")

# 대화 기록 초기화
if "history" not in st.session_state:
    st.session_state.history = []

# Streamlit 내장 오디오 입력 (v1.25+)
st.subheader("녹음 버튼을 눌러 음성을 녹음하세요")
audio_data = st.audio_input("음성 녹음")

if audio_data:
    # 음성 -> 텍스트
    user_text = transcribe_audio(audio_data.getbuffer())
    st.markdown(f"**User:** {user_text}")

    # GPT-4o 응답
    bot_text = chat_with_gpt(user_text, st.session_state.history)
    st.markdown(f"**Bot:** {bot_text}")

    # OpenAI TTS (20대 남성톤: ash)
    speech = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="ash",
        input=bot_text
    )
    audio_bytes = speech.audio
    st.audio(audio_bytes, format="audio/mp3")
    # 자동 재생
    b64 = base64.b64encode(audio_bytes).decode()
    html_audio = f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    components.html(html_audio, height=0)

    # 대화 기록 저장
    st.session_state.history.append({"user": user_text, "bot": bot_text})

# 대화 기록 표시 및 복사
if st.session_state.history:
    conversation_text = "\n".join(
        f"User: {h['user']}\nBot: {h['bot']}" for h in st.session_state.history
    )
    st.text_area("Conversation History", value=conversation_text, height=200)
    if st.button("Copy Conversation"):
        escaped = json.dumps(conversation_text)
        js = f"<script>navigator.clipboard.writeText({escaped});</script>"
        components.html(js)
        st.success("대화 내용이 클립보드에 복사되었습니다.")
