from __future__ import annotations

import asyncio
import base64
import logging
from pathlib import Path

from app.config import settings

log = logging.getLogger(__name__)


async def convert_ogg_to_mp3(ogg_path: str) -> str:
    mp3_path = ogg_path.replace(".ogg", ".mp3")
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y", "-i", ogg_path, "-acodec", "libmp3lame", "-q:a", "2", mp3_path,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()
    return mp3_path


async def convert_mp3_to_ogg(mp3_path: str) -> str:
    ogg_path = mp3_path.replace(".mp3", ".ogg")
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y", "-i", mp3_path,
        "-acodec", "libopus", "-b:a", "64k", ogg_path,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()
    return ogg_path


def file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def ensure_user_dir(user_id: int) -> Path:
    d = Path(settings.messages_dir) / str(user_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


async def get_audio_duration(path: str) -> float:
    """Get audio duration in seconds using ffprobe."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate()
        return float(stdout.decode().strip())
    except Exception:
        return 0.0


def escape_md(text: str) -> str:
    """Escape special chars for Telegram MarkdownV2 (light version)."""
    chars = r"_*[]()~`>#+-=|{}.!"
    for c in chars:
        text = text.replace(c, f"\\{c}")
    return text
