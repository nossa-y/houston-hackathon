"""Houston mission control server.

  uvicorn houston.server:app --port 4242
"""
from __future__ import annotations

import json
import pathlib
import queue
import threading
import uuid

import asyncio
import base64

import gradium
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel

from . import config, narrator
from .mission import Mission
from .receipts import load_receipts, verify_chain

app = FastAPI(title="Houston", version="0.1.0")

STATIC = pathlib.Path(__file__).parent / "static"

_missions: dict[str, dict] = {}  # id -> {queue, done, receipt}


class MissionRequest(BaseModel):
    task: str
    max_heals: int | None = None
    local_audit: bool = True


@app.post("/api/missions")
def create_mission(req: MissionRequest):
    if not req.task.strip():
        raise HTTPException(400, "empty task")
    mid = uuid.uuid4().hex[:12]
    q: queue.Queue = queue.Queue()
    _missions[mid] = {"queue": q, "done": False, "receipt": None}

    def emit(kind: str, data: dict) -> None:
        say = narrator.line_for(kind, data)
        q.put({"kind": kind, "data": data, "say": say})

    def run() -> None:
        try:
            m = Mission(req.task, emit=emit, max_heals=req.max_heals,
                        local_audit=req.local_audit, mission_id=mid)
            receipt = m.run()
            _missions[mid]["receipt"] = json.loads(receipt.model_dump_json())
        except Exception as e:  # emit the failure instead of dying silently
            q.put({"kind": "mission_error", "data": {"error": repr(e)[:300]}, "say": None})
        finally:
            _missions[mid]["done"] = True
            q.put(None)  # sentinel

    threading.Thread(target=run, daemon=True).start()
    return {"mission_id": mid}


@app.get("/api/stream/{mid}")
def stream(mid: str):
    st = _missions.get(mid)
    if st is None:
        raise HTTPException(404, "unknown mission")

    def gen():
        while True:
            try:
                item = st["queue"].get(timeout=300)
            except queue.Empty:
                yield "event: ping\ndata: {}\n\n"
                continue
            if item is None:
                yield "event: done\ndata: {}\n\n"
                return
            yield f"data: {json.dumps(item, default=str)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/tts")
def tts(text: str):
    if not config.GRADIUM_API_KEY:
        raise HTTPException(503, "no voice configured")
    try:
        wav = narrator.tts_wav(text[:300])
    except Exception as e:
        raise HTTPException(502, f"tts failed: {e}")
    return Response(content=wav, media_type="audio/wav",
                    headers={"Cache-Control": "max-age=86400"})


@app.get("/api/receipts")
def receipts():
    return {"chain_intact": verify_chain(), "receipts": load_receipts()[::-1]}


@app.websocket("/api/stt")
async def stt_bridge(ws: WebSocket):
    """Browser mic -> Gradium streaming STT -> transcript frames back."""
    await ws.accept()
    client = gradium.client.GradiumClient(api_key=config.GRADIUM_API_KEY)
    try:
        async with client.stt_realtime(input_format="pcm") as stt:
            async def pump_in():
                while True:
                    msg = await ws.receive_json()
                    if msg.get("type") == "eos":
                        await stt.send_flush()
                        await stt.send_eos()
                        return
                    audio = msg.get("audio")
                    if audio:
                        await stt.send_audio(base64.b64decode(audio))

            async def pump_out():
                async for m in stt:
                    t = m.get("type")
                    if t in ("text", "word", "partial", "final", "transcript"):
                        await ws.send_json(m)
                    elif t == "end_of_stream":
                        await ws.send_json({"type": "end_of_stream"})
                        return

            await asyncio.gather(pump_in(), pump_out())
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "error": str(e)[:200]})
        except Exception:
            pass
    finally:
        try:
            await ws.close()
        except Exception:
            pass


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")
