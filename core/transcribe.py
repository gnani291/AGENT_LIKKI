from faster_whisper import WhisperModel

_model_cache = {}


def _get_model(model_size: str = "base"):
    if model_size not in _model_cache:
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
