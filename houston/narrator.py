"""Terse mission-control narration. No LLM in this path - event type -> line.

TTS is synthesized once per unique line and cached to disk (WiFi-resilient).
"""
from __future__ import annotations

import asyncio
import hashlib
import pathlib

import gradium

from . import config

TTS_CACHE = config.EVIDENCE_DIR / "tts-cache"
TTS_CACHE.mkdir(parents=True, exist_ok=True)


def line_for(kind: str, data: dict) -> str | None:
    """Map a mission event to one short spoken line (or None for silence)."""
    if kind == "mission_started":
        return "Mission received. Executor launching."
    if kind == "executor_started":
        return "Agent is live. Houston is watching every step."
    if kind == "claimed":
        n = data.get("n", 1)
        if n == 1:
            return "The agent claims the task is done. Houston never trusts a claim."
        return "The agent claims the corrected task is done. Auditing again."
    if kind == "phase" and data.get("phase") == "audit":
        return "Verifying independently against the live site."
    if kind == "verdict":
        if data.get("verified"):
            return "Audit result: confirmed. Evidence attached."
        div = (data.get("divergence") or "the claims did not match the site")
        div = div.split(".")[0][:110]
        return f"Audit result: rejected. {div}."
    if kind == "healing":
        return "Injecting the diagnosis into the live session. The agent gets a second chance."
    if kind == "phase" and data.get("phase") == "arbiter":
        return "The two answers disagree. Escalating to the arbiter for close inspection."
    if kind == "arbiter_verdict":
        w = data.get("winner", "")
        if w == "attempt_original":
            return "Arbiter ruling: the original answer was right all along. Restored."
        if w == "attempt_healed":
            return "Arbiter ruling: the healed answer stands."
        return "Arbiter ruling: both were wrong. Corrected answer issued."
    if kind == "local_audit":
        return "Evidence re-checked on device. No screenshot left this machine."
    if kind == "receipt":
        status = str(data.get("final_status", "")).replace("-", " ")
        return f"Receipt sealed. Mission {status}."
    return None


async def _synth(text: str) -> bytes:
    client = gradium.client.GradiumClient(api_key=config.GRADIUM_API_KEY)
    chunks: list[bytes] = []
    async with client.tts_realtime(voice_id=config.GRADIUM_VOICE_ID, output_format="wav") as tts:
        async def send():
            await tts.send_text(text)
            await tts.send_eos()

        async def recv():
            async for m in tts:
                if m["type"] == "audio":
                    chunks.append(m["audio"])
                elif m["type"] == "end_of_stream":
                    return

        await asyncio.gather(send(), recv())
    return b"".join(chunks)


def tts_wav(text: str) -> bytes:
    """Synthesize (or fetch cached) narration audio for a line."""
    key = hashlib.sha1(text.encode()).hexdigest()[:20]
    cached = TTS_CACHE / f"{key}.wav"
    if cached.exists():
        return cached.read_bytes()
    data = asyncio.run(_synth(text))
    cached.write_bytes(data)
    return data


def prewarm(lines: list[str]) -> None:
    for line in lines:
        try:
            tts_wav(line)
        except Exception:
            pass
