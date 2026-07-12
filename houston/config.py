"""Central config. Reads .env at repo root."""
import os
import pathlib

from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

HAI_API_KEY = os.environ.get("HAI_API_KEY", "")
GRADIUM_API_KEY = os.environ.get("GRADIUM_API_KEY", "")

# Agents: executor is fast and fallible (that is the point); verifier is stronger and independent.
EXECUTOR_AGENT = os.environ.get("HOUSTON_EXECUTOR_AGENT", "h/web-surfer-flash")
VERIFIER_AGENT = os.environ.get("HOUSTON_VERIFIER_AGENT", "h/web-surfer-pro")

MAX_HEALS = int(os.environ.get("HOUSTON_MAX_HEALS", "2"))
EXECUTOR_IDLE_TIMEOUT_S = 900  # keep the session alive and steerable between heal cycles
SESSION_TIMEOUT_S = 720        # executor wait ceiling per attempt
VERIFIER_BUDGET_S = 300        # soft budget: after this we force_answer the verifier
VERIFIER_GRACE_S = 180         # extra time for the forced answer to land

AGENT_VIEW_HOST = "https://platform.hcompany.ai"

EVIDENCE_DIR = ROOT / "evidence"
RECEIPTS_DIR = EVIDENCE_DIR / "receipts"
RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)

# Local Holo (NVIDIA lane): llama-server serving Holo-3.1-35B-A3B GGUF
LOCAL_HOLO_URL = os.environ.get("HOUSTON_LOCAL_HOLO_URL", "http://localhost:8080/v1")
GRADIUM_VOICE_ID = os.environ.get("HOUSTON_VOICE_ID", "cLONiZ4hQ8VpQ4Sz")


def agent_view_url(session_id: str, event: int | None = None) -> str:
    url = f"{AGENT_VIEW_HOST}/agent-view/{session_id}"
    if event is not None:
        url += f"?event={event}&expanded=true&screenshot={event}"
    return url
