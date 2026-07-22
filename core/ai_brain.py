"""
ai_brain.py
Core LLM brain (Groq) + the voice/text command router that decides
which feature of the assistant a query should go to.
"""

import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are LIKKI, a friendly, human-like personal AI assistant created by Gnani. "
    "Reply conversationally, concisely, and helpfully."
)

YOUTUBE_URL_RE = re.compile(
    r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+", re.IGNORECASE
)


def get_ai_response(user_query: str, history: list | None = None) -> str:
    """Plain conversational reply from the LLM."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-6:])  # last few turns for light context
    messages.append({"role": "user", "content": user_query})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.6,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI ERROR:", e)
        return "Sorry, I am having trouble connecting right now."


def summarize_text(text: str, style: str = "concise") -> str:
    """Summarize a transcript / long text block."""
    prompt = (
        f"Summarize the following transcript in a {style} way, "
        f"using short bullet points where useful:\n\n{text[:8000]}"
    )
    return get_ai_response(prompt)


def extract_youtube_url(text: str) -> str | None:
    match = YOUTUBE_URL_RE.search(text)
    return match.group(0) if match else None


def classify_intent(query: str, has_image: bool = False, has_audio: bool = False) -> dict:
    """
    Lightweight rule-based router. Returns a dict like:
    {"intent": "youtube_download", "payload": "<url>"}

    Intents:
      - youtube_download
      - youtube_transcribe   (download + whisper transcribe + summarize)
      - web_search
      - ocr                  (extract text from the currently uploaded image)
      - transcribe_audio     (whisper transcribe the currently uploaded audio)
      - speak                (read the last AI reply / given text aloud)
      - chat                 (fallback -> general conversation)
    """
    q = query.lower().strip()
    url = extract_youtube_url(query)

    if url:
        if any(w in q for w in ["transcribe", "summarize", "summary", "subtitles", "captions"]):
            return {"intent": "youtube_transcribe", "payload": url}
        return {"intent": "youtube_download", "payload": url}

    if has_audio and any(w in q for w in ["transcribe", "speech to text", "convert audio"]):
        return {"intent": "transcribe_audio", "payload": None}

    if has_image and any(w in q for w in ["extract text", "read text", "ocr", "read this image"]):
        return {"intent": "ocr", "payload": None}

    if any(w in q for w in ["search for", "search the web", "look up", "google"]):
        return {"intent": "web_search", "payload": query}

    if any(w in q for w in ["read this out", "read it out", "speak this", "say this", "read aloud"]):
        return {"intent": "speak", "payload": query}

    return {"intent": "chat", "payload": query}
