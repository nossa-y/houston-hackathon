"""Cancel all non-terminal sessions (frees the concurrency quota between runs)."""
from hai_agents import Client

from . import config


def cancel_stragglers() -> int:
    client = Client(api_key=config.HAI_API_KEY)
    n = 0
    try:
        page = client.sessions.list_sessions(size=50)
        items = getattr(page, "items", []) or []
    except Exception as e:
        print("list failed:", e)
        return 0
    for s in items:
        status = str(getattr(s, "status", ""))
        if status in ("running", "pending", "queued", "idle", "paused"):
            try:
                client.session(str(s.id)).cancel()
                n += 1
                print(f"cancelled {s.id} ({status})")
            except Exception as e:
                print(f"cancel {s.id} failed: {e}")
    return n


if __name__ == "__main__":
    print("cancelled:", cancel_stragglers())
