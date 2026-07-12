<div align="center">

# HOUSTON

**Mission control for computer-use agents. Never trust. Always verify.**

*Track 2 (Browser Use) · Voice Challenge (Gradium) · NVIDIA Challenge (NemoClaw + local Holo)*

Built at The Computer Use Hackathon, San Francisco, July 11-12 2026 · Team HOUSTON

**[▶ 97-second demo film](remotion/out/houston-demo-16x9.mp4)** · **[Public session replays - no login needed](evidence/public-replays.md)**

</div>

---

## The problem

The most documented failure of computer-use agents in the wild is not clicking the wrong button. It is **claiming "done" when they are not**: empty results reported as success, per-night prices reported as totals, constraints silently dropped. Everyone says "verify agent output". Nobody ships the verifier.

## What Houston does

Houston wraps any H Company computer-use agent in a supervision runtime:

```
ATTEMPT -> AUDIT -> HEAL -> ARBITER -> PROOF
```

1. **ATTEMPT** - an executor session (`h/web-surfer-flash`) runs your mission on the real web. You can speak the mission in (Gradium STT) and Houston narrates every phase back (Gradium TTS).
2. **AUDIT** - Houston never trusts the claim. An independent verifier session (`h/web-surfer-pro`, different model) re-derives the answer against the live site and returns a **typed verdict** (`answer_schema`): itemized claims, observations, matches.
3. **HEAL** - on rejection, the diagnosis is steered into the SAME still-alive executor session (`send_message`). No restart, no lost context. The agent gets a second chance.
4. **ARBITER** - if healing *changed* the answer, neither result is trusted: an arbiter session resolves only the disputed delta by close inspection (opens each disputed item's own page). Quorum under dispute - because **the verifier can be wrong too** (see the 2:13 AM story below).
5. **PROOF** - every mission seals a **hash-chained receipt**: attempts, verdicts, session ids, deep-linkable agent-view replays, on-device evidence audit. Proof, not promises.

## The 2:13 AM story (why the arbiter exists)

At 2:13 AM tonight, on a real mission ("count the five-star books in a category"), our verifier **misread a four-star badge and rejected a CORRECT answer**, then healed the executor into adopting the wrong count, then confirmed its own error. The receipts caught it: replay `d5914f0d8c93` shows the whole incident. By 2:19 AM Houston had two fixes:

- a **close-inspection doctrine** in the verifier (never judge small icons in dense lists), and
- the **arbiter**: whenever a healed answer contradicts the original, a third session settles the disputed facts item by item.

Re-running the same mission after the fix: the correct answer verifies cleanly. Both receipts are in `evidence/receipts/` - this repo's own audit trail includes its own supervisor being caught and corrected.

## Quickstart

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # add HAI_API_KEY (platform.hcompany.ai) and GRADIUM_API_KEY (studio.gradium.ai)

# mission control UI
.venv/bin/uvicorn houston.server:app --port 4242   # -> http://localhost:4242

# or headless
.venv/bin/python run_mission.py "Find every five-star book in the Poetry category on books.toscrape.com and their total price."

# optional: on-device evidence audits (NVIDIA lane)
mkdir -p ~/models/holo31 && cd ~/models/holo31 && \
  curl -LO https://huggingface.co/Hcompany/Holo-3.1-35B-A3B-GGUF/resolve/main/q4_k_m.gguf && \
  curl -LO https://huggingface.co/Hcompany/Holo-3.1-35B-A3B-GGUF/resolve/main/mmproj.f16.gguf
llama-server -m ~/models/holo31/q4_k_m.gguf --mmproj ~/models/holo31/mmproj.f16.gguf \
  --port 8080 -c 8192 --jinja --reasoning-format none
```

## Architecture

```
houston/
  mission.py      the arc: attempt -> audit -> heal -> arbiter -> proof
  prompts.py      verifier doctrine, heal re-brief, arbiter method
  schemas.py      Verdict / ArbiterVerdict / Receipt (typed, validated)
  receipts.py     sha256 hash chain + receipt store
  local_audit.py  on-device screenshot audit via local Holo3.1 (llama.cpp)
  narrator.py     event -> terse line -> Gradium streaming TTS (disk-cached)
  server.py       FastAPI: missions, SSE stream, STT WebSocket bridge, receipts
  share.py        share_session -> public replay links sealed into receipts
  config.py       agents, budgets, .env
  cleanup.py      cancel straggler sessions (frees the concurrency quota)
  static/         the mission control UI
run_mission.py    one mission, headless
run_batch.py      mission battery = the overnight gauntlet
test_*.py         Gradium TTS, live session, and self-talk voice-loop tests
nemoclaw/         NVIDIA challenge: sandbox policy + local-Holo endpoint + blueprint
remotion/         the 97-second demo film, rendered from code
evidence/         receipts chain, batch results, public replays - all real runs
```

## Sponsor integrations (by necessity, not decoration)

| Sponsor | How Houston uses it |
|---|---|
| **H Company** | Executor + verifier + arbiter are separate AGP sessions; healing = `send_message` steering into a live session; typed verdicts via `answer_schema`; `session.stream()` events drive the UI + narration; `agent_view` deep links (`?event=N&screenshot=N`) anchor every receipt; `force_answer` budget watchdog keeps audits bounded |
| **Gradium** | Missions spoken in via streaming STT (WS bridge, word partials, browser mic); every phase narrated in 48 kHz streaming TTS with disk cache; self-talk test rig (TTS speaks a mission, STT transcribes it, 92% word overlap) validates the loop fully automatically |
| **NVIDIA** | Verifier evidence screenshots audited ON-DEVICE by Holo-3.1-35B-A3B (q4_k_m GGUF + mmproj, llama.cpp, ~10 s/audit on Apple Silicon, zero bytes leave the machine); `nemoclaw/` ships the OpenShell egress policy + custom-endpoint wiring + the first computer-use blueprint prepared for nemoclaw-community |

## Evidence

- `evidence/public-replays.md` - **click these**: publicly shared session replays (executor, audits, arbiter) - no login needed
- `evidence/receipts/` - every mission tonight, hash-chained (`chain.txt`), each with executor/verifier replay URLs (plus arbiter when it fired)
- `evidence/batch-results.json` + `evidence/batch-round2.log` - the overnight gauntlet scoreboard
- `remotion/out/houston-demo-16x9.mp4` - the 97-second demo film (every frame rendered from real receipt data)
- `test_gradium.py`, `test_h_session.py`, `test_selftalk.py` - the smoke tests that gated each layer

## Why this matters

Computer-use agents are hitting production with no trust layer. Houston is the missing supervisor: catch the false "done", heal the live session, doubt the supervisor itself, and hand a human a receipt they can replay step by step.

The wedge on Monday morning: **agent QA for teams shipping computer-use automations** - every deployment needs receipts before it can be trusted with real work. Built in one night at the hackathon, and Houston supervised real missions the whole time it was being built.
