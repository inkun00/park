import os
import io
import json
import openai
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
from pydub import AudioSegment

def transcribe_audio(audio_bytes):
    # Whisper API로 음성 -> 텍스트 변환
    audio_file = io.BytesIO(audio_bytes)
    transcription = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file
    )
    return transcription["text"].strip()

def chat_with_gpt(prompt, history):
    # 기본적으로 gpt-3.5-turbo 사용 (비용 최적화 모델)
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

# 중앙에 영상 재생 (assets/park_jongchul.mp4 경로에 비디오 파일 배치)
st.video("assets/park_jongchul.mp4", format="video/mp4")

# 세션 상태 초기화\if 'history' not in st.session_state:
    st.session_state.history = []

# WebRTC 설정 (음성 전용)
client_settings = ClientSettings(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)
webrtc_ctx = webrtc_streamer(
    key="voice-chat",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=client_settings,
    media_stream_constraints={"audio": True, "video": False},
    audio_receiver_size=1024
)

if webrtc_ctx.audio_receiver:
    frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
    if frames:
        # frames -> WAV 변환
        audio_bytes = b"".join([frame.to_ndarray().tobytes() for frame in frames])
        # 음성 텍스트 변환
        user_text = transcribe_audio(audio_bytes)
        if user_text:
            st.markdown(f"**User:** {user_text}")
            # 챗봇 응답
            bot_text = chat_with_gpt(user_text, st.session_state.history)
            st.markdown(f"**Bot:** {bot_text}")
            # 음성합성 (TTS)
            tts = gTTS(bot_text, lang='ko')  
            mp3_buf = io.BytesIO()
            tts.write_to_fp(mp3_buf)
            mp3_buf.seek(0)
            st.audio(mp3_buf.read(), format='audio/mp3')
            # 대화 이력 저장
            st.session_state.history.append({"user": user_text, "bot": bot_text})

# 대화 이력 출력 및 복사 기능
if st.session_state.history:
    conversation_text = "\n".join([
        f"User: {h['user']}\nBot: {h['bot']}" for h in st.session_state.history
    ])
    st.text_area("Conversation History", value=conversation_text, height=200)
    if st.button("Copy Conversation"):
        # 브라우저 클립보드에 복사
        escaped = json.dumps(conversation_text)
        js = f"<script>navigator.clipboard.writeText({escaped});</script>"
        components.html(js)
        st.success("대화 내용이 클립보드에 복사되었습니다.")

# OPENAI_API_KEY 체크 안내
if not os.getenv("OPENAI_API_KEY"):
    st.warning("환경 변수 OPENAI_API_KEY 가 설정되어 있지 않습니다. OpenAI API 키를 설정해주세요.")
