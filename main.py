import os
import io
import json
import openai
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration


def transcribe_audio(audio_bytes):
    """
    Whisper API를 사용하여 입력된 오디오 바이트를 텍스트로 변환합니다.
    """
    audio_file = io.BytesIO(audio_bytes)
    transcription = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file
    )
    return transcription["text"].strip()


def chat_with_gpt(prompt, history):
    """
    사용자 프롬프트와 대화 기록을 기반으로 GPT-3.5-turbo 모델을 통해 응답을 생성합니다.
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

# 중앙에 영상 재생 (assets/park_jongchul.mp4 파일 필요)
st.video("assets/park_jongchul.mp4", format="video/mp4")

# 대화 기록 초기화
if 'history' not in st.session_state:
    st.session_state.history = []

# RTC 설정 (음성 전용)
rtc_configuration = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)
webrtc_ctx = webrtc_streamer(
    key="voice-chat",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=rtc_configuration,
    media_stream_constraints={"audio": True, "video": False},
    audio_receiver_size=1024
)

# 음성 수신 및 처리
if webrtc_ctx.audio_receiver:
    frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
    if frames:
        audio_bytes = b"".join(frame.to_ndarray().tobytes() for frame in frames)
        user_text = transcribe_audio(audio_bytes)
        if user_text:
            st.markdown(f"**User:** {user_text}")
            bot_text = chat_with_gpt(user_text, st.session_state.history)
            st.markdown(f"**Bot:** {bot_text}")

            # TTS 생성 및 재생
            tts = gTTS(bot_text, lang='ko')
            mp3_buf = io.BytesIO()
            tts.write_to_fp(mp3_buf)
            mp3_buf.seek(0)
            st.audio(mp3_buf.read(), format='audio/mp3')

            # 대화 기록 저장
            st.session_state.history.append({"user": user_text, "bot": bot_text})

# 대화 기록 표시 및 복사 기능
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

# API 키 설정 확인
if not os.getenv("OPENAI_API_KEY"):
    st.warning("환경 변수 OPENAI_API_KEY가 설정되지 않았습니다. OpenAI API 키를 설정해주세요.")
