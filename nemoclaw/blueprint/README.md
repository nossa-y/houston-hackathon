# Blueprint: Computer-Use Verification Agent (Holo 3.1 local + H Agent Platform)

> Prepared as a contribution to [NVIDIA/nemoclaw-community](https://github.com/NVIDIA/nemoclaw-community).
> No computer-use blueprint exists in the community repo yet; this fills that gap with the
> verification-first pattern from Houston (The Computer Use Hackathon, SF, July 2026).

## What it composes

| NemoClaw layer | This blueprint |
|---|---|
| **Model** | H Company `Holo-3.1-35B-A3B` (Apache-2 open weights, q4_k_m GGUF + vision projector) served by llama.cpp as a local OpenAI-compatible endpoint - UI grounding and screenshot evidence audits run fully on-device |
| **Harness** | Hermes (`NEMOCLAW_AGENT=hermes`) with the `hai-agent-platform` MCP server registered - executor/verifier/arbiter computer-use sessions run on H's agent platform, observable step by step |
| **OpenShell** | Baseline sandbox + one scoped egress preset (`agp.eu.hcompany.ai:443` only) - the agent cannot reach anything else |

## Why verification-first

Computer-use agents claim "done" when they are not - the most-documented failure mode in the
wild. This blueprint runs every task as ATTEMPT -> AUDIT (independent session re-checks the
claim on the live site) -> HEAL (diagnosis steered into the same live session) -> ARBITER
(close-inspection quorum when the healed answer contradicts the original) -> PROOF
(hash-chained receipt with step-level replay links). The sandbox guarantees the *runtime*
cannot exfiltrate; the receipts prove the *work* was real.

## Files

- `../policies/hai-agent-platform.yaml` - the single egress preset
- `../image/Dockerfile` - Hermes image with streamable-HTTP MCP client
- Houston source: https://github.com/nossa-y/houston-hackathon (executor/verifier/healer/arbiter,
  receipts, local audit)

## Quickstart

See `../README.md`. Two commands: start llama-server with the GGUF, `nemohermes onboard`.
