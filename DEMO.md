# DEMO RUNBOOK - read this before judging (5 min)

## Pre-flight (do this once, ~09:30, at home or venue)

```bash
cd ~/computer-use-hackathon

# 1. sanity: straggler sessions + server
.venv/bin/python -m houston.cleanup
pkill -f "uvicorn houston.server" ; .venv/bin/uvicorn houston.server:app --port 4242 &
open http://localhost:4242

# 2. local Holo (for the on-device audit beat) - takes ~90s to load 20GB
pkill -f llama-server
llama-server -m ~/models/holo31/q4_k_m.gguf --mmproj ~/models/holo31/mmproj.f16.gguf \
  --port 8080 -c 8192 --jinja --reasoning-format none &
# ready when: curl -s localhost:8080/health -> {"status":"ok"}
```

Checklist before leaving home: laptop charged + charger, phone hotspot tested (venue WiFi will die), volume up for narration, http://localhost:4242 open, this file open.

## Round 1 (5 min): pitch 1:30 + LIVE demo 1:30 + Q&A 2:00

### Pitch (90s, over the mission you ALREADY launched - see trick below)
- "Every team here built an agent that claims 'task complete'. The most documented failure of computer-use agents is that those claims are often false. Nobody ships the verifier. We did."
- "Houston runs every mission as attempt, audit, heal, arbiter, proof: an independent H session re-checks the claim on the live site, a rejected claim gets healed by steering the SAME live session, a disputed answer goes to an arbiter, and everything seals into a hash-chained receipt with step-level replays."
- The kicker: "At 2:13am our own verifier gaslit a correct agent into a wrong answer. Houston's receipts caught it, and the arbiter exists because of it. The receipt is public - you can scrub the replay."

### Live demo trick (start BEFORE you pitch)
As you plug in, launch the mission so it finishes during the demo slot:
- Click the mic (or type): **"Find every five-star book in the Poetry category on books.toscrape.com and their total price."**
- Voice narration announces phases while you talk. By demo time you are at the verdict/receipt. Show: claim card -> verdict card -> receipts drawer -> click a replay link (agent-view scrubbing) -> local audit line ("zero screenshot bytes left this machine").
- If the run verified on attempt 1 (flash is good), SAY THAT: "no drama this run - here is the 2:13am receipt where there WAS drama" -> open the public replay (no login):
  https://platform.hcompany.ai/share/70d0aa02-1789-420e-8678-a114e3b6fab7 (executor, the incident)
  https://platform.hcompany.ai/share/2446ae92-0b4f-4719-8df7-38b320e82d23 (the arbiter firing, later run)
  Every outcome is a good story: that is the product.

### Q&A ammo
- "Verifier can be wrong too?" -> "Yes - the 2:13am incident (receipt d5914f0d8c93) is the verifier being wrong; the arbiter was built FROM that incident and then fired for real in the gauntlet (receipt 91570138d86d, status verified-by-arbiter). Both replays are public."
- "Cost?" -> "Executor on flash ($0.25/1M in), verifier on pro only when needed; evidence audit is local and free. Verification pays for itself the first time an agent lies."
- "Billion-dollar company?" -> "Every agent deployment needs a trust layer; Houston is the receipts + supervision runtime that lets enterprises turn agents loose. The wedge: agent QA for teams shipping computer-use automations."
- "What primitives?" -> sessions, send_message steering, answer_schema typed verdicts, force_answer watchdog, session streaming, agent-view deep links, share_session. Plus Gradium STT/TTS streaming, plus local Holo3.1 GGUF + NemoClaw policy config.

## Round 2 (3 min, finalists): pitch 1:30 + demo 1:30, no questions
Same beats, tighter. End on the receipts drawer + "Never trust. Always verify."

## Submission (BEFORE 15:30 - portal PROJECTS tab)
Everything staged in SUBMISSION.md: description text, repo URL, video path
`remotion/out/houston-demo-16x9.mp4`. Review, then submit on the portal.

**Evidence freeze before submitting**: `git add evidence/ && git commit -m "evidence freeze" && git push`
(receipts keep accumulating - the repo judges clone must contain the latest chain)

## Fallbacks
- Venue WiFi dead: phone hotspot; narration audio is disk-cached for known lines; the film (remotion/out) plays offline.
- H API hiccup: receipts drawer + replay links of tonight's real runs still demo the whole arc.
- Mic fails: type the mission; narration still speaks.
- llama-server down: local-audit toggle off; everything else works.
