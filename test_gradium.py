"""Smoke test: Gradium TTS realtime API. Saves PCM audio to evidence/."""
import asyncio
import os
import pathlib

import gradium
from dotenv import load_dotenv

load_dotenv(pathlib.Path(__file__).parent / ".env")


async def main():
    client = gradium.client.GradiumClient(api_key=os.environ["GRADIUM_API_KEY"])
    chunks = []
    async with client.tts_realtime(voice_id="cLONiZ4hQ8VpQ4Sz", output_format="pcm") as tts:
        async def sender():
            await tts.send_text("Voice check. The night build is alive and running.")
            await tts.send_eos()

        async def receiver():
            async for msg in tts:
                if msg["type"] == "audio":
                    chunks.append(msg["audio"])
                elif msg["type"] == "end_of_stream":
                    return

        await asyncio.gather(sender(), receiver())

    out = pathlib.Path(__file__).parent / "evidence"
    out.mkdir(exist_ok=True)
    first = chunks[0] if chunks else b""
    print("chunk type:", type(first).__name__, "n_chunks:", len(chunks))
    if isinstance(first, str):
        import base64
        data = b"".join(base64.b64decode(c) for c in chunks)
    else:
        data = b"".join(chunks)
    (out / "gradium-tts-check.pcm").write_bytes(data)
    print("audio bytes:", len(data))


if __name__ == "__main__":
    asyncio.run(main())
