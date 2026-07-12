"""Hash-chained receipts: tamper-evident proof of what agents actually did."""
from __future__ import annotations

import hashlib
import json
import pathlib

from . import config
from .schemas import Receipt

CHAIN_FILE = config.RECEIPTS_DIR / "chain.txt"


def _last_hash() -> str:
    if CHAIN_FILE.exists():
        lines = CHAIN_FILE.read_text().strip().splitlines()
        if lines:
            return lines[-1].split()[0]
    return "genesis"


def finalize_receipt(receipt: Receipt) -> Receipt:
    receipt.prev_hash = _last_hash()
    body = receipt.model_dump(exclude={"hash"})
    receipt.hash = hashlib.sha256(
        json.dumps(body, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]

    path = config.RECEIPTS_DIR / f"{receipt.mission_id}.json"
    path.write_text(receipt.model_dump_json(indent=2))
    with open(CHAIN_FILE, "a") as f:
        f.write(f"{receipt.hash} {receipt.prev_hash} {receipt.mission_id} {receipt.final_status}\n")
    return receipt


def load_receipts() -> list[dict]:
    out = []
    for p in sorted(config.RECEIPTS_DIR.glob("*.json")):
        try:
            out.append(json.loads(p.read_text()))
        except Exception:
            continue
    return out


def verify_chain() -> bool:
    """Recompute the chain; True if intact."""
    prev = "genesis"
    if not CHAIN_FILE.exists():
        return True
    for line in CHAIN_FILE.read_text().strip().splitlines():
        h, p, mission_id, *_ = line.split()
        if p != prev:
            return False
        rp = config.RECEIPTS_DIR / f"{mission_id}.json"
        if rp.exists():
            data = json.loads(rp.read_text())
            data_no_hash = {k: v for k, v in data.items() if k != "hash"}
            recomputed = hashlib.sha256(
                json.dumps(data_no_hash, sort_keys=True, default=str).encode()
            ).hexdigest()[:16]
            if recomputed != h:
                return False
        prev = h
    return True
