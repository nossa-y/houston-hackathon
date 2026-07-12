"""Self-talk rig: Gradium TTS speaks a mission -> Houston's STT bridge must transcribe it.

Validates the entire voice loop fully automatically. Requires the server on :4242.
"""
import asyncio
import base64
import json
import os
import pathlib
import struct
import sys

import gradium
import websockets
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).parent
load_dotenv(ROOT / ".env")

SPOKEN = "Find the most expensive book in the Travel category on books dot toscrape dot com"


async def synth_wav48k(text: str) -> bytes:
    client = gradium.client.GradiumClient(api_key=os.environ["GRADIUM_API_KEY"])
    chunks = []
    async with client.tts_realtime(voice_id="YTpq7expH9539ERJ", output_format="wav") as tts:
        async def s():
            await tts.send_text(text)
            await tts.send_eos()
        async def r():
            async for m in tts:
                if m["type"] == "audio":
                    chunks.append(m["audio"])
                elif m["type"] == "end_of_stream":
                    return
        await asyncio.gather(s(), r())
    return b"".join(chunks)


def wav_to_pcm24k(wav: bytes) -> bytes:
    """Extract PCM from 48k mono wav and naive-downsample to 24k s16le."""
    assert wav[:4] == b"RIFF"
    # find data chunk
    i = 12
    while i < len(wav):
        cid, size = wav[i:i+4], struct.unpack("<I", wav[i+4:i+8])[0]
        if cid == b"data":
            pcm = wav[i+8:i+8+size]
            break
        i += 8 + size
    else:
        raise ValueError("no data chunk")
    samples = struct.unpack(f"<{len(pcm)//2}h", pcm)
    down = samples[::2]  # 48k -> 24k
    return struct.pack(f"<{len(down)}h", *down)


async def main() -> int:
    wav = await synth_wav48k(SPOKEN)
    pcm = wav_to_pcm24k(wav)
    print(f"synthesized {len(wav)} wav bytes -> {len(pcm)} pcm24k bytes")

    transcript = []
    async with websockets.connect("ws://localhost:4242/api/stt") as ws:
        async def send():
            chunk = 4800 * 2  # 200ms
            for off in range(0, len(pcm), chunk):
                await ws.send(json.dumps({"audio": base64.b64encode(pcm[off:off+chunk]).decode()}))
                await asyncio.sleep(0.18)
            await ws.send(json.dumps({"type": "eos"}))

        async def recv():
            async for raw in ws:
                m = json.loads(raw)
                if m.get("type") in ("text", "word"):
                    transcript.append(m.get("text") or m.get("word") or "")
                elif m.get("type") in ("transcript", "final") and m.get("text"):
                    transcript.clear()
                    transcript.append(m["text"])
                elif m.get("type") == "end_of_stream":
                    return
                elif m.get("type") == "error":
                    print("ERROR:", m)
                    return

        await asyncio.gather(send(), recv())

    text = " ".join(t.strip() for t in transcript if t.strip())
    text = text.replace(" .", ".").replace(" ,", ",").strip()
    print("heard:", repr(text))
    spoken_words = set(SPOKEN.lower().replace(".", " ").split())
    heard_words = set(text.lower().replace(".", " ").replace(",", " ").split())
    overlap = len(spoken_words & heard_words) / max(1, len(spoken_words))
    print(f"word overlap: {overlap:.0%}")
    return 0 if overlap > 0.6 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
