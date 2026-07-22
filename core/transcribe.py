"""
transcribe.py
faster-whisper based speech-to-text for uploaded audio files (and audio
pulled from downloaded YouTube videos). Kept separate from
voice_io.listen_from_mic, which is for short live microphone commands.

Uses faster-whisper instead of openai-whisper: same Whisper models, but no
triton dependency (which has no compatible wheels on newer Python versions
and caused Streamlit Cloud's dependency resolution to fail), and it runs
noticeably faster on CPU-only hosts like Streamlit Community Cloud.
"""

from faster_whisper import WhisperModel

_model_cache = {}


def _get_model(model_size: str = "base"):
    if model_size not in _model_cache:
        # CPU + int8 keeps memory/CPU usage low, which matters on
        # Streamlit Cloud's free-tier resource limits.
        _model_cache[model_size] = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _model_cache[model_size]


def transcribe_file(file_path: str, model_size: str = "base") -> str:
    """Transcribe a local audio/video file to text using faster-whisper."""
    try:
        model = _get_model(model_size)
        segments, _info = model.transcribe(file_path)
        return " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as e:
        print("Transcription error:", e)
        return ""
