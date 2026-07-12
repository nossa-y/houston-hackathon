"""Make session replays publicly viewable (share_session) so anyone can scrub them."""
from __future__ import annotations

import requests

from . import config

BASE = "https://agp.eu.hcompany.ai"


def share_session(session_id: str) -> str | None:
    """Returns a public URL anyone can open without auth, or None on failure."""
    try:
        r = requests.post(
            f"{BASE}/api/v2/sessions/{session_id}/share",
            headers={"Authorization": f"Bearer {config.HAI_API_KEY}"},
            timeout=15,
        )
        r.raise_for_status()
        path = r.json().get("share_url", "")
        if not path:
            return None
        # The API returns a raw trajectory path; the human-viewable page lives on the
        # platform host once the share exists.
        return f"https://platform.hcompany.ai/share/{session_id}"
    except Exception:
        return None


def share_receipt_sessions(receipt) -> dict[str, str]:
    """Share executor + verifier(s) + arbiter sessions of a receipt. Returns label->url."""
    out: dict[str, str] = {}
    if receipt.executor_session_id:
        u = share_session(receipt.executor_session_id)
        if u:
            out["executor"] = u
    for i, vid in enumerate(receipt.verifier_session_ids, 1):
        u = share_session(vid)
        if u:
            out[f"audit{i}"] = u
    if receipt.arbiter_view:
        sid = receipt.arbiter_view.rstrip("/").split("/")[-1].split("?")[0]
        u = share_session(sid)
        if u:
            out["arbiter"] = u
    return out
