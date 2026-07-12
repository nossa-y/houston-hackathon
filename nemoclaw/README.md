# Houston inside NemoClaw (NVIDIA challenge)

Houston runs H Company models at two layers, and both slot into [NemoClaw](https://github.com/NVIDIA/NemoClaw):

1. **Hosted layer** - Houston's executor/verifier/arbiter sessions run on H's agent platform
   (`agp.eu.hcompany.ai`). Inside a NemoClaw OpenShell sandbox, that egress is blocked by
   default; `policies/hai-agent-platform.yaml` (from H Company's own demos repo pattern)
   opens exactly that host, nothing else.
2. **Local layer (the interesting one)** - Houston's evidence audit runs H's open-weight
   **Holo-3.1-35B-A3B** (q4_k_m GGUF + vision projector) fully on-device via llama.cpp.
   NemoClaw consumes any OpenAI-compatible endpoint, so the same server that Houston uses
   becomes a NemoClaw custom endpoint: UI grounding and screenshot audits stay local, and
   only agent-platform traffic leaves the sandbox under policy.

## Measured on Apple Silicon (M4 Pro, 48 GB)

| Metric | Value |
|---|---|
| Model | Holo-3.1-35B-A3B (MoE, 3B active), q4_k_m, 20 GB |
| Vision | mmproj f16 (858 MB) |
| Screenshot audit (3k-token image prefill + 100 tok out) | ~11 s end to end |
| Privacy | evidence screenshots never leave the machine |

## Run it

```bash
# 1. Local Holo endpoint (same one Houston's local_audit uses)
llama-server -m ~/models/holo31/q4_k_m.gguf \
  --mmproj ~/models/holo31/mmproj.f16.gguf \
  --port 8080 -c 8192 --jinja --reasoning-format none

# 2. NemoClaw sandbox with the Hermes harness (per H Company's demos repo)
export NEMOCLAW_AGENT=hermes
nemohermes onboard --from image/Dockerfile --name houston-hermes
#    inference provider -> Custom OpenAI-compatible -> http://host.docker.internal:8080/v1

# 3. Allow egress to the H agent platform (hosted layer)
nemohermes houston-hermes policy-add --from-file policies/hai-agent-platform.yaml
nemohermes houston-hermes policy-list   # confirm agp.eu.hcompany.ai listed

# 4. Register Houston's MCP surface inside the sandbox (/sandbox/.hermes/config.yaml)
#    mcp_servers:
#      hai-agent-platform:
#        url: https://agp.eu.hcompany.ai/mcp
#        headers: { Authorization: "Bearer hk-..." }
```

Result: a **policied, sandboxed, locally-grounded verification agent** - H Company models
through NemoClaw at both the model layer (local Holo3.1 GGUF endpoint) and the harness
layer (H agent platform via scoped egress).

## Blueprint contribution

`blueprint/` is structured as a nemoclaw-community contribution ("computer-use verification
agent" - no computer-use blueprint exists in that repo yet). See `blueprint/README.md`.
