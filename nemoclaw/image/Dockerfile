# syntax=docker/dockerfile:1
#
# Custom NemoClaw Hermes sandbox image that adds streamable-HTTP MCP client support.
# The stock hermes-sandbox-base ships an `mcp` package without `mcp.client.streamable_http`,
# so the hosted hai-agent-platform server can't connect (`hermes mcp test` reports it missing).
# Install it at BUILD time: normal networking and cert trust apply here, whereas at runtime the
# OpenShell egress policy blocks uv from PyPI and uv doesn't use the image's patched CA bundle.
#
# Build and apply:
#   nemohermes onboard --from nemoclaw/image/Dockerfile --name hai-hermes
# (the Dockerfile's parent dir is the build context; keeping it in its own folder keeps that small)

ARG BASE_IMAGE=ghcr.io/nvidia/nemoclaw/hermes-sandbox-base:latest
FROM ${BASE_IMAGE}

# Prefer Hermes' own [mcp] extra (pins matching versions); fall back to explicit packages.
RUN uv pip install --python /opt/hermes/.venv/bin/python -e "/opt/hermes[mcp]" \
 || uv pip install --python /opt/hermes/.venv/bin/python -U mcp httpx httpx-sse

# Fail the build early if the HTTP client still isn't importable.
RUN /opt/hermes/.venv/bin/python -c "import importlib.util as u; assert u.find_spec('mcp.client.streamable_http'), 'streamable_http still missing'"
