from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import AsyncIterator

from openai import AsyncOpenAI

from app.config import settings, SYSTEM_PROMPT

log = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai.api_key)

SUPPORTED_FILE_EXTENSIONS = {
    ".pdf", ".txt", ".md", ".json", ".csv", ".tsv",
    ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".py", ".js", ".ts", ".html", ".css", ".xml", ".yaml", ".yml",
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
}


def is_supported_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_FILE_EXTENSIONS


def is_image_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _build_input(
    history: list[dict],
    text: str | None = None,
    image_b64: str | None = None,
    file_b64: str | None = None,
    file_name: str | None = None,
) -> list[dict]:
    """Build Responses API input from chat history + current message."""
    messages = [{"role": "developer", "content": SYSTEM_PROMPT}]

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    if text or image_b64 or file_b64:
        content_parts: list[dict] = []
        if text:
            content_parts.append({"type": "input_text", "text": text})
        if image_b64:
            content_parts.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{image_b64}",
            })
        if file_b64 and file_name:
            content_parts.append({
                "type": "input_file",
                "filename": file_name,
                "file_data": f"data:application/octet-stream;base64,{file_b64}",
            })
        messages.append({"role": "user", "content": content_parts})

    return messages


async def chat_stream(
    history: list[dict],
    text: str | None = None,
    image_b64: str | None = None,
    file_b64: str | None = None,
    file_name: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float = 0.7,
) -> AsyncIterator[str]:
    """Stream a chat response, yielding text chunks as they arrive."""
    model = model or settings.openai.default_model
    max_tokens = max_tokens or settings.openai.max_tokens
    inp = _build_input(history, text, image_b64, file_b64, file_name)

    stream = await client.responses.create(
        model=model,
        input=inp,
        max_output_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    )

    async for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta
        elif event.type == "response.completed":
            break
        elif event.type == "error":
            log.error("OpenAI stream error: %s", event)
            raise RuntimeError(f"OpenAI error: {event}")


async def chat_complete(
    history: list[dict],
    text: str | None = None,
    image_b64: str | None = None,
    file_b64: str | None = None,
    file_name: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float = 0.7,
) -> tuple[str, int, int]:
    """Non-streaming chat. Returns (response_text, input_tokens, output_tokens)."""
    model = model or settings.openai.default_model
    max_tokens = max_tokens or settings.openai.max_tokens
    inp = _build_input(history, text, image_b64, file_b64, file_name)

    response = await client.responses.create(
        model=model,
        input=inp,
        max_output_tokens=max_tokens,
        temperature=temperature,
    )

    text_out = ""
    for item in response.output:
        if item.type == "message":
            for part in item.content:
                if part.type == "output_text":
                    text_out += part.text

    usage = response.usage
    return text_out, usage.input_tokens, usage.output_tokens


async def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Whisper."""
    with open(audio_path, "rb") as f:
        transcript = await client.audio.transcriptions.create(
            model=settings.openai.stt_model,
            file=f,
        )
    return transcript.text


async def text_to_speech(text: str, voice: str = "nova", output_path: str = "output.mp3") -> str:
    """Convert text to speech and save to file."""
    response = await client.audio.speech.create(
        model=settings.openai.tts_model,
        voice=voice,
        input=text,
    )
    with open(output_path, "wb") as f:
        async for chunk in response.iter_bytes(1024):
            f.write(chunk)
    return output_path


async def generate_image(prompt: str, quality: str = "medium") -> str:
    """Generate an image and return its URL."""
    response = await client.images.generate(
        model=settings.openai.image_model,
        prompt=prompt,
        size="1024x1024",
        quality=quality,
        n=1,
    )
    return response.data[0].url
