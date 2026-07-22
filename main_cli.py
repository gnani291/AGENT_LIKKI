"""
main_cli.py
Terminal voice-loop version of LIKKI (no browser needed).
Say "exit", "stop", or "bye" to quit.
"""

from datetime import datetime

from core import ai_brain, ocr, transcribe, voice_io, web_search, youtube_tools


def handle_intent(query: str):
    intent_data = ai_brain.classify_intent(query)
    intent = intent_data["intent"]
    payload = intent_data["payload"]

    if intent == "web_search":
        results = web_search.search_web(payload, max_results=3)
        if not results:
            return "I couldn't find anything on the web for that."
        lines = [f"{r['title']}: {r['snippet']}" for r in results]
        return " | ".join(lines)

    if intent == "youtube_download":
        try:
            path = youtube_tools.download_video(payload)
            return f"Downloaded the video as {path}"
        except Exception as e:
            return f"Sorry, the download failed: {e}"

    if intent == "youtube_transcribe":
        try:
            audio_path = youtube_tools.download_audio(payload)
            transcript = transcribe.transcribe_file(audio_path)
            summary = ai_brain.summarize_text(transcript)
            return f"Here's the summary: {summary}"
        except Exception as e:
            return f"Sorry, I couldn't process that video: {e}"

    return ai_brain.get_ai_response(query)


def main():
    print("================================")
    print(" LIKKI AI Assistant (CLI mode) ")
    print("================================")
    voice_io.speak_cli("Hello Gnani. I am Likki. You can speak now.")

    while True:
        query = voice_io.listen_from_mic()
        if not query:
            continue

        q_lower = query.lower()

        if "time" in q_lower:
            voice_io.speak_cli(f"The current time is {datetime.now().strftime('%I:%M %p')}")
            continue

        if any(w in q_lower for w in ["exit", "bye", "stop"]):
            voice_io.speak_cli("Goodbye Gnani. Have a nice day.")
            break

        answer = handle_intent(query)
        voice_io.speak_cli(answer or "Sorry, I could not generate a response.")


if __name__ == "__main__":
    main()
