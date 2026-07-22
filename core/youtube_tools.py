"""
youtube_tools.py
YouTube video download + audio-only extraction (used as the first stage of
the "transcribe & summarize a YouTube video" pipeline).
"""

import os
import uuid

import yt_dlp

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_video(url: str) -> str:
    """Download the best available progressive video+audio stream. Returns file path."""
    out_template = os.path.join(DOWNLOAD_DIR, f"%(title).80s-{uuid.uuid4().hex[:6]}.%(ext)s")
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "outtmpl": out_template,
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def download_audio(url: str) -> str:
    """Download audio-only stream as mp3. Returns file path."""
    out_template = os.path.join(DOWNLOAD_DIR, f"%(title).80s-{uuid.uuid4().hex[:6]}.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": out_template,
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base = ydl.prepare_filename(info)
        return os.path.splitext(base)[0] + ".mp3"


def get_video_title(url: str) -> str:
    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("title", url)
