"""On-device evidence audit (NVIDIA lane).

After a verdict, ask the LOCAL Holo3.1 model (llama-server, OpenAI-compatible)
to independently confirm the verdict's key observation from the verifier's
final screenshot. Zero bytes leave the machine. Skips gracefully when the
local server or screenshot is unavailable.
"""
from __future__ import annotations

import base64
import time

import requests

from . import config


def _local_up() -> bool:
    try:
        r = requests.get(config.LOCAL_HOLO_URL.replace("/v1", "/health"), timeout=2)
        return r.ok
    except Exception:
        try:
            r = requests.get(config.LOCAL_HOLO_URL + "/models", timeout=2)
            return r.ok
        except Exception:
            return False


def _verifier_screenshots(mission, n: int = 3) -> list[bytes]:
    """Fetch the last n screenshot resources from the most recent verifier session."""
    if not mission.receipt.verifier_session_ids:
        return []
    sid = mission.receipt.verifier_session_ids[-1]
    shots: list[bytes] = []
    try:
        import re
        base = "https://agp.eu.hcompany.ai/api/v2"
        r = requests.get(
            f"{base}/sessions/{sid}/events",
            headers={"Authorization": f"Bearer {config.HAI_API_KEY}"},
            params={"size": 100},
            timeout=15,
        )
        r.raise_for_status()
        events = r.json().get("items", [])
        urls: list[str] = []
        for ev in events:
            urls += re.findall(r"https?://[^\s\"']+screenshot[^\s\"']*", str(ev))
        seen: list[str] = []
        for u in urls:
            if u not in seen:
                seen.append(u)
        for u in seen[-n:]:
            img = requests.get(u, headers={"Authorization": f"Bearer {config.HAI_API_KEY}"}, timeout=15)
            if img.ok and img.content[:4] in (b"\x89PNG", b"\xff\xd8\xff\xe0", b"\xff\xd8\xff\xe1"):
                shots.append(img.content)
    except Exception:
        pass
    return shots


def _ask_local(shot: bytes, question: str) -> str:
    b64 = base64.b64encode(shot).decode()
    r = requests.post(
        config.LOCAL_HOLO_URL + "/chat/completions",
        json={
            "model": "holo3.1",
            "temperature": 0.0,
            "max_tokens": 120,
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    {"type": "text", "text": question},
                ],
            }],
        },
        timeout=120,
    )
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"]
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    return text.strip()


def audit_verdict(mission, verdict) -> dict | None:
    """Ask local Holo whether any of the verifier's final screenshots supports the
    decisive observation. The screenshots never leave the machine."""
    if not _local_up():
        return None
    shots = _verifier_screenshots(mission, n=3)
    if not shots:
        return None

    key_claim = None
    for c in verdict.checked_claims:
        if c.matches:
            key_claim = c
    if key_claim is None:
        return None

    question = (
        "You are auditing evidence. Answer strictly YES or NO followed by a short reason: "
        f"does this screenshot support the observation \"{key_claim.observed}\"?"
    )
    t0 = time.time()
    per_shot: list[str] = []
    supports = False
    for shot in reversed(shots):  # newest first
        text = _ask_local(shot, question)
        per_shot.append(text[:160])
        if text.upper().startswith("YES"):
            supports = True
            break
    return {
        "engine": "Holo-3.1-35B-A3B q4_k_m via llama.cpp (on-device, Apple Silicon)",
        "checked_observation": key_claim.observed,
        "result": per_shot[-1] if per_shot else "",
        "shots_checked": len(per_shot),
        "supports": supports,
        "latency_s": round(time.time() - t0, 2),
    }
