# LIKKI AI - Unified Multimodal Assistant

A merge of two earlier projects — **LIKKI_AI** (voice assistant, chat, web search, OCR)
and **Multimodal_ai** (YouTube download, Whisper speech-to-text, OCR, TTS) — into one
voice-command-driven app. One command box. Every feature routes through a single
intent router instead of being scattered across separate forms.

## Features

| Feature | How to trigger |
|---|---|
| Conversational chat (Groq LLM) | Just ask anything |
| Web search (DuckDuckGo) | "search for ..." / "look up ..." |
| YouTube video download | Paste/say a YouTube link |
| YouTube transcribe + summarize | Say "transcribe/summarize \<youtube link\>" |
| Image text extraction (OCR) | Upload an image, then say "extract text" |
| Audio file transcription (Whisper) | Upload audio, then say "transcribe" |
| Text-to-speech | Say "read this out loud", or use the standalone TTS box |

Everything is driven by `core/ai_brain.classify_intent()`, a lightweight
keyword-based router. It looks at what you typed/said plus whether an image or
audio file is currently uploaded, and dispatches to the right module.

## Project structure

```
likki_multimodal/
├── app.py              # Streamlit web app (main entry point)
├── main_cli.py          # Terminal voice-loop version (no browser)
├── core/
│   ├── ai_brain.py       # Groq chat + intent router + summarization
│   ├── voice_io.py       # Mic input (SpeechRecognition) + TTS output (gTTS)
│   ├── web_search.py     # DuckDuckGo text search
│   ├── ocr.py             # pytesseract + optional OpenCV preprocessing
│   ├── transcribe.py      # Whisper transcription (cached model)
│   └── youtube_tools.py   # yt-dlp video/audio download
├── requirements.txt
├── packages.txt          # apt-level deps (tesseract, ffmpeg, portaudio)
└── .env.example
```

## Setup

```bash
python -m venv venv
source venv/bin/activate      # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env           # then add your GROQ_API_KEY
```

System packages needed (Linux/macOS via package manager, or already bundled
on Windows installers): `tesseract-ocr`, `ffmpeg`. On Streamlit Community
Cloud these come from `packages.txt` automatically.

Run the web app:
```bash
streamlit run app.py
```

Run the terminal voice assistant instead:
```bash
python main_cli.py
```

## Important note on the microphone

`speech_recognition`'s `sr.Microphone()` accesses the **server's** microphone,
not the browser's. That means live voice input only works when you run the
app on your own machine — it will not work if you deploy `app.py` to a remote
host like Streamlit Community Cloud. Every other feature (chat, search,
YouTube tools, OCR, file transcription, TTS) works fine remotely; only the
"🎤 Speak" button needs a local run.

## What changed from the two originals

- Dropped the Pixabay/DuckDuckGo **image search** panel (flagged as low value).
- Replaced `pyttsx3`/`sapi5` (Windows-only) with **gTTS** for the web app so
  audio output works cross-platform and inside Streamlit via `st.audio()`.
  `pyttsx3` is kept only for the offline terminal assistant.
- Merged LIKKI's chat/search/OCR with Multimodal's YouTube download and
  Whisper transcription into one command router instead of two apps.
- Added a new combined flow: **YouTube link → download audio → Whisper
  transcript → Groq summary**, in one voice command.
