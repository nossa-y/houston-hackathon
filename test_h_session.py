"""Smoke test: real AGP computer-use session end to end. Saves evidence."""
import json
import os
import pathlib
import time

from dotenv import load_dotenv
from hai_agents import Client, wait_for_session

ROOT = pathlib.Path(__file__).parent
load_dotenv(ROOT / ".env")

TASK = (
    "Go to https://news.ycombinator.com and report the exact title and points "
    "of the current #1 story. Answer with just: title, points."
)

client = Client(api_key=os.environ["HAI_API_KEY"])
t0 = time.time()
session = client.sessions.create_session(agent="h/web-surfer-flash", messages=TASK)
live = f"https://platform.eu.hcompany.ai/agent-view/{session.id}"
print(f"session={session.id}", flush=True)
print(f"live={live}", flush=True)

result = wait_for_session(client, session.id, timeout_seconds=480)
dt = time.time() - t0
status = getattr(result, "status", "settled")
answer = getattr(result, "answer", None)
print(f"status={status} elapsed={dt:.1f}s")
print(f"answer={answer}")

out = ROOT / "evidence"
out.mkdir(exist_ok=True)
(out / "h-session-smoke.json").write_text(json.dumps({
    "session_id": str(session.id),
    "live_url": live,
    "status": str(status),
    "answer": str(answer),
    "elapsed_s": round(dt, 1),
    "agent": "h/web-surfer-flash",
    "task": TASK,
    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
}, indent=2))
print("evidence saved")
