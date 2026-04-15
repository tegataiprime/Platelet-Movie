#!/bin/sh
# Wrapper script to run Doppler MCP with environment variables

exec npx -y @dopplerhq/mcp-server \
  --read-only \
  --project=platelet-movie \
  --config=dev
