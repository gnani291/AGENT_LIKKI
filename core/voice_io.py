"""
voice_io.py
Speech input (microphone -> text) and speech output (text -> audio).

TTS uses gTTS (cloud/OS-independent, returns audio bytes -> works cleanly
inside Streamlit via st.audio). pyttsx3 is kept only for the offline CLI
assistant (main_cli.py) since it needs a local sound device anyway.

Note: microphone access via speech_recognition only works when the app is
run LOCALLY (python/streamlit running on the same machine as the mic).
It will not work on a remote server like Streamlit Community Cloud.
"""

from io import BytesIO

import speech_recognition as sr
from gtts import gTTS


def listen_from_mic(timeout: int = 6, phrase_time_limit: int = 12) -> str:
    """Capture one utterance from the default microphone and return text.

    Raises RuntimeError with a clear message if pyaudio isn't installed
    (expected on Streamlit Cloud — install requirements-local.txt to enable
    this when running LIKKI on your own machine instead).
    """
    recognizer = sr.Recognizer()
    try:
        mic = sr.Microphone()
    except (AttributeError, OSError) as e:
        raise RuntimeError(
            "Microphone input isn't available in this environment. "
            "This only works when running LIKKI locally with pyaudio installed "
            "(pip install -r requirements-local.txt)."
        ) from e

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print("Speech service error:", e)
        return ""
    except sr.WaitTimeoutError:
        return ""


def text_to_speech_bytes(text: str, lang: str = "en") -> bytes:
    """Convert text to mp3 audio bytes (for st.audio playback)."""
    if not text.strip():
        return b""
    buf = BytesIO()
    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def speak_cli(text: str):
    """Offline speech output for the terminal assistant (main_cli.py)."""
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)
        print("\nLIKKI:", text)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("TTS ERROR:", e)
        print("LIKKI:", text)
