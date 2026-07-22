"""
app.py
LIKKI AI - Unified Multimodal Assistant

One voice/text command box routes to every capability:
  - conversational chat            (Groq LLM)
  - web search                     (DuckDuckGo)
  - YouTube video download
  - YouTube transcribe + summarize (yt-dlp + Whisper + Groq)
  - image text extraction / OCR    (pytesseract)
  - audio file transcription       (Whisper)
  - text-to-speech playback        (gTTS)

Run locally with: streamlit run app.py
(Microphone input only works when Streamlit is running on your own machine.)
"""

import os

import streamlit as st
from PIL import Image

from core import ai_brain, ocr, transcribe, voice_io, web_search, youtube_tools

st.set_page_config(page_title="LIKKI AI - Multimodal Assistant", page_icon="🤖", layout="wide")
st.title("🤖 LIKKI AI - Unified Multimodal Assistant")
st.caption("One command box. Every feature. Type it or say it.")

# ---------------------------------------------------------------- SESSION STATE
defaults = {
    "chat_history": [],
    "query": "",
    "last_ai_reply": "",
    "uploaded_image": None,
    "uploaded_audio_path": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------- SIDEBAR
with st.sidebar:
    st.header("Settings")
    enable_voice_input = st.checkbox("Enable microphone input", value=False)
    st.caption("🎤 Mic input only works when running LIKKI locally, not on Streamlit Cloud.")
    enable_voice_output = st.checkbox("Speak AI replies (TTS)", value=True)
    whisper_size = st.selectbox("Whisper model size", ["tiny", "base", "small"], index=1)
    st.markdown("---")
    st.markdown(
        "**Try saying / typing:**\n"
        "- `what's the capital of France`\n"
        "- `search for best laptops 2026`\n"
        "- `https://youtu.be/xxxx` → downloads it\n"
        "- `transcribe and summarize https://youtu.be/xxxx`\n"
        "- `extract text` (after uploading an image below)\n"
        "- `transcribe` (after uploading an audio file below)\n"
        "- `read this out loud`"
    )

# ---------------------------------------------------------------- COMMAND BOX
col1, col2 = st.columns([1, 3])

with col1:
    if enable_voice_input and st.button("🎤 Speak a command"):
        heard = None
        with st.spinner("Listening..."):
            try:
                heard = voice_io.listen_from_mic()
            except RuntimeError as e:
                st.error(str(e))
        if heard:
            st.session_state.query = heard
        elif heard == "":
            st.warning("Didn't catch that, try again.")

with col2:
    with st.form(key="command_form", clear_on_submit=True):
        typed = st.text_input("Type a command or question", value="")
        submitted = st.form_submit_button("Send")
        if submitted and typed.strip():
            st.session_state.query = typed.strip()

st.markdown("---")

# ---------------------------------------------------------------- FILE INPUTS (for context-aware voice commands)
fcol1, fcol2 = st.columns(2)

with fcol1:
    st.subheader("🖼 Image (for OCR)")
    img_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="img_uploader")
    if img_file is not None:
        st.session_state.uploaded_image = Image.open(img_file)
        st.image(st.session_state.uploaded_image, caption="Uploaded image", use_column_width=True)

        if st.button("📝 Extract Text"):
            with st.spinner("Extracting text..."):
                extracted = ocr.extract_text_from_image(st.session_state.uploaded_image)
            st.text_area("OCR result", value=extracted or "No text found.", height=150)

with fcol2:
    st.subheader("🎧 Audio file (for transcription)")
    audio_file = st.file_uploader("Upload audio", type=["mp3", "wav", "m4a"], key="audio_uploader")
    if audio_file is not None:
        os.makedirs("uploads", exist_ok=True)
        path = os.path.join("uploads", audio_file.name)
        with open(path, "wb") as f:
            f.write(audio_file.read())
        st.session_state.uploaded_audio_path = path
        st.audio(path)

st.markdown("---")

# ---------------------------------------------------------------- COMMAND ROUTER
if st.session_state.query:
    query = st.session_state.query
    st.session_state.chat_history.append({"role": "user", "content": query})

    intent_data = ai_brain.classify_intent(
        query,
        has_image=st.session_state.uploaded_image is not None,
        has_audio=st.session_state.uploaded_audio_path is not None,
    )
    intent = intent_data["intent"]
    payload = intent_data["payload"]

    st.subheader(f"🤖 Handling: `{intent}`")

    # --- conversational chat ---
    if intent == "chat":
        reply = ai_brain.get_ai_response(query, history=st.session_state.chat_history)
        st.session_state.last_ai_reply = reply
        st.write(reply)
        if enable_voice_output:
            audio_bytes = voice_io.text_to_speech_bytes(reply)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # --- web search ---
    elif intent == "web_search":
        with st.spinner("Searching the web..."):
            results = web_search.search_web(payload)
        if results:
            for r in results:
                st.markdown(f"**[{r['title']}]({r['link']})**")
                st.write(r["snippet"])
        else:
            st.info("No results found.")

    # --- youtube download ---
    elif intent == "youtube_download":
        with st.spinner("Downloading video..."):
            try:
                path = youtube_tools.download_video(payload)
                st.success(f"Downloaded: {os.path.basename(path)}")
                st.video(path)
            except Exception as e:
                st.error(f"Download failed: {e}")

    # --- youtube transcribe + summarize ---
    elif intent == "youtube_transcribe":
        with st.spinner("Downloading audio..."):
            try:
                audio_path = youtube_tools.download_audio(payload)
            except Exception as e:
                st.error(f"Audio download failed: {e}")
                audio_path = None

        if audio_path:
            with st.spinner("Transcribing with Whisper..."):
                transcript = transcribe.transcribe_file(audio_path, model_size=whisper_size)
            st.subheader("📝 Transcript")
            st.text_area("Transcript", value=transcript, height=200)

            with st.spinner("Summarizing..."):
                summary = ai_brain.summarize_text(transcript)
            st.subheader("📌 Summary")
            st.write(summary)

    # --- OCR ---
    elif intent == "ocr":
        if st.session_state.uploaded_image is None:
            st.warning("Upload an image first.")
        else:
            with st.spinner("Extracting text..."):
                text = ocr.extract_text_from_image(st.session_state.uploaded_image)
            st.subheader("📝 Extracted Text")
            st.text_area("OCR result", value=text or "No text found.", height=150)

    # --- audio transcription ---
    elif intent == "transcribe_audio":
        if st.session_state.uploaded_audio_path is None:
            st.warning("Upload an audio file first.")
        else:
            with st.spinner("Transcribing with Whisper..."):
                text = transcribe.transcribe_file(
                    st.session_state.uploaded_audio_path, model_size=whisper_size
                )
            st.subheader("📝 Transcript")
            st.text_area("Transcription result", value=text or "No speech detected.", height=150)

    # --- speak / TTS ---
    elif intent == "speak":
        text_to_read = st.session_state.last_ai_reply or query
        audio_bytes = voice_io.text_to_speech_bytes(text_to_read)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.info("Nothing to read yet.")

    st.session_state.query = ""

# ---------------------------------------------------------------- FREEFORM TEXT-TO-SPEECH TOOL
st.markdown("---")
st.subheader("🔊 Text to Speech (standalone)")
free_text = st.text_area("Enter any text to convert to audio", key="free_tts_text")
if st.button("Generate Audio"):
    audio_bytes = voice_io.text_to_speech_bytes(free_text)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
    else:
        st.warning("Enter some text first.")

# ---------------------------------------------------------------- CHAT HISTORY
if st.session_state.chat_history:
    with st.expander("💬 Conversation history"):
        for turn in st.session_state.chat_history:
            role = "🧑 You" if turn["role"] == "user" else "🤖 LIKKI"
            st.markdown(f"**{role}:** {turn['content']}")