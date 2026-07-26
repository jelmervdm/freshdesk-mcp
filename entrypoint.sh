#!/bin/bash
set -e

if [ "$ENABLE_CONTEXTFORGE_GATEWAY" = "true" ]; then
    PORT="${GATEWAY_PORT:-8000}"
    echo "Starting ContextForge Gateway (Port $PORT)..." >&2
    exec python3 -m mcpgateway.translate --stdio "freshdesk-mcp-server" --expose-sse --port "$PORT" --host 0.0.0.0
else
    echo "Starting standard Freshdesk MCP server..." >&2
    exec freshdesk-mcp-server "$@"
fi

