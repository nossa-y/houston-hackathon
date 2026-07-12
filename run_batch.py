"""Batch mission runner: the empirical gauntlet.

Runs a battery of missions sequentially, collects stats, and prints a scoreboard.
Every run adds a real receipt to the chain - overnight evidence.

  .venv/bin/python run_batch.py tasks/battery.json --rounds 2
"""
import argparse
import json
import pathlib
import time

from houston.cleanup import cancel_stragglers
from houston.mission import Mission


def emit_quiet(kind: str, data: dict) -> None:
    if kind in ("mission_started", "claimed", "verdict", "healing", "arbiter_verdict", "receipt", "mission_error"):
        stamp = time.strftime("%H:%M:%S")
        brief = {
            "claimed": lambda: (data.get("answer") or "")[:90].replace("\n", " "),
            "verdict": lambda: f"verified={data.get('verified')} conf={data.get('confidence')}",
            "receipt": lambda: f"{data.get('final_status')} #{data.get('hash')}",
            "arbiter_verdict": lambda: f"winner={data.get('winner')}",
            "mission_error": lambda: data.get("error", "")[:120],
        }.get(kind, lambda: "")()
        print(f"  [{stamp}] {kind}: {brief}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("battery", help="JSON file: [{'name':..., 'task':..., 'truth':...}, ...]")
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--local-audit", action="store_true")
    args = ap.parse_args()

    battery = json.loads(pathlib.Path(args.battery).read_text())
    out_path = pathlib.Path("evidence/batch-results.json")
    results = json.loads(out_path.read_text()) if out_path.exists() else []
    for r in range(1, args.rounds + 1):
        for spec in battery:
            print(f"\n=== round {r} · {spec['name']} ===", flush=True)
            cancel_stragglers()
            t0 = time.time()
            try:
                m = Mission(spec["task"], emit=emit_quiet, local_audit=args.local_audit)
                receipt = m.run()
                results.append({
                    "round": r, "name": spec["name"], "mission_id": receipt.mission_id,
                    "status": receipt.final_status, "attempts": len(receipt.attempts),
                    "healed": len(receipt.attempts) > 1,
                    "arbiter": receipt.arbiter.winner if receipt.arbiter else None,
                    "elapsed": receipt.total_elapsed_s,
                    "answer": (receipt.final_answer or "")[:160],
                    "truth": spec.get("truth", ""),
                })
            except Exception as e:
                results.append({"round": r, "name": spec["name"], "status": "crash",
                                "error": repr(e)[:200], "elapsed": round(time.time() - t0, 1)})
            out_path.write_text(json.dumps(results, indent=2))

    print("\n===== SCOREBOARD =====")
    for res in results:
        star = "HEALED" if res.get("healed") else "      "
        print(f"r{res['round']} {res['name']:24s} {res.get('status','?'):32s} "
              f"att={res.get('attempts','-')} {star} {res.get('elapsed','-')}s")
    n_ok = sum(1 for x in results if str(x.get("status", "")).startswith(("verified", "corrected")))
    print(f"\n{n_ok}/{len(results)} missions ended in a verified/corrected state")
    return 0


if __name__ == "__main__":
    main()
