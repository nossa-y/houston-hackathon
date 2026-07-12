"""Houston CLI: run one full mission arc headless.

Usage:
  .venv/bin/python run_mission.py "Find the current #1 story on Hacker News and report its title and point count."
  .venv/bin/python run_mission.py --no-local-audit "task..."
"""
import argparse
import json
import sys
import time

from houston.mission import Mission


def emit(kind: str, data: dict) -> None:
    ts = time.strftime("%H:%M:%S")
    line = {"t": ts, "kind": kind, **{k: v for k, v in data.items() if k != "claims"}}
    print(json.dumps(line, default=str)[:600], flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task", help="the mission task")
    ap.add_argument("--max-heals", type=int, default=None)
    ap.add_argument("--no-local-audit", action="store_true")
    args = ap.parse_args()

    m = Mission(args.task, emit=emit, max_heals=args.max_heals,
                local_audit=not args.no_local_audit)
    receipt = m.run()
    print("\n=== RECEIPT ===")
    print(f"mission:   {receipt.mission_id}")
    print(f"status:    {receipt.final_status}")
    print(f"attempts:  {len(receipt.attempts)}")
    print(f"answer:    {receipt.final_answer}")
    print(f"replay:    {receipt.agent_view}")
    for v in receipt.verifier_views:
        print(f"audit:     {v}")
    print(f"hash:      {receipt.hash} (prev {receipt.prev_hash})")
    print(f"elapsed:   {receipt.total_elapsed_s}s")
    return 0 if receipt.final_status == "verified" else 2


if __name__ == "__main__":
    sys.exit(main())
