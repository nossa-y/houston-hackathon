# Portal submission (PROJECTS tab)

**Team**: Houston (created on the portal)
**Track**: Track 2 - Browser Use
**Side challenges**: Voice Challenge (Gradium) + NVIDIA Challenge (NemoClaw)

**GitHub repo**: https://github.com/nossa-y/houston-hackathon

**2-min demo video**: remotion/out/houston-demo-16x9.mp4 (96.9s)
(if the portal wants a link: upload to YouTube unlisted first, or Google Drive share)

**Short description** (paste):

Houston is mission control for computer-use agents. The most documented failure of CU agents is claiming "done" when they are not - so Houston never trusts a claim. Every mission runs as ATTEMPT -> AUDIT -> HEAL -> ARBITER -> PROOF: an H Company executor session does the task, an independent verifier session re-derives the result on the live site and returns a typed verdict, a rejected claim gets healed by steering the diagnosis into the SAME live session (no restart), and if healing changes the answer an arbiter session settles the dispute by close inspection - because at 2:13am tonight our verifier gaslit a correct agent and Houston's receipts caught it. Every mission seals a hash-chained receipt with step-level agent-view replays. Missions are spoken in and narrated back via Gradium streaming STT/TTS, and evidence screenshots are audited on-device by Holo-3.1-35B GGUF via llama.cpp (zero bytes leave the machine), with a NemoClaw sandbox config + community blueprint included. Battle-tested through the night: every receipt in the repo is from a real run.
