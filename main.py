import os
import io
import json
import openai
import base64
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS

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
        st.warning("API 키가 없습니다. 키를 입력해주세요.")


def transcribe_audio(audio_bytes):
    """
    Whisper API를 사용하여 오디오 바이트를 텍스트로 변환합니다.
    """
    audio_file = io.BytesIO(audio_bytes)
    transcription = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file
    )
    return transcription["text"].strip()


def chat_with_gpt(prompt, history):
    """
    GPT-3.5-turbo 모델로 대화 응답 생성
    """
    messages = []
    for turn in history:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["bot"]})
    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Streamlit 앱 설정
st.set_page_config(page_title="Voice Chatbot: 박종철", layout="centered")
st.header("음성 챗봇: 박종철 (1987년 대한민국)")

# 중앙 영상 재생
st.video("assets/park_jongchul.mp4", format="video/mp4")

# 대화 기록 초기화
if 'history' not in st.session_state:
    st.session_state.history = []

# 오디오 입력 (Streamlit v1.25+ 내장 기능)
st.subheader("녹음 버튼을 눌러 음성을 녹음하세요")
audio_data = st.audio_input("음성 녹음")  # 브라우저에서 녹음

if audio_data:
    # Whisper로 텍스트 변환
    user_text = transcribe_audio(audio_data.getbuffer())
    st.markdown(f"**User:** {user_text}")

    # 챗봇 응답 생성
    bot_text = chat_with_gpt(user_text, st.session_state.history)
    st.markdown(f"**Bot:** {bot_text}")

    # TTS 음성 출력
    tts = gTTS(bot_text, lang='ko')
    mp3_buf = io.BytesIO()
    tts.write_to_fp(mp3_buf)
    mp3_buf.seek(0)
    mp3_bytes = mp3_buf.read()
    st.audio(mp3_bytes, format='audio/mp3')
    # 자동 재생 HTML 태그 삽입
    b64 = base64.b64encode(mp3_bytes).decode()
    html_audio = f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    components.html(html_audio, height=0)

    # 대화 이력 저장
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
