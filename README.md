# Freshdesk MCP Server

[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://github.com/jelmervdm/freshdesk-mcp)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](pyproject.toml)

An MCP (Model Context Protocol) server that exposes Freshdesk helpdesk operations as tools. This allows MCP-compatible AI assistants and clients (e.g. Claude Desktop, VS Code, Cursor) to list, search, create, and manage tickets, contacts, agents, and groups directly.

---

## Features

- **Ticket Management**: Create, list, search, view, update, delete tickets, add replies, and add private notes.
- **Contact Management**: Create, list, and look up contacts.
- **Support Staff (Agents & Groups)**: List agents and ticket assignment groups.
- **Tool Routing**: Enable semantic search routing to dramatically reduce LLM context usage by only showing active/relevant tools.
- **ContextForge Gateway Support**: Integrated SSE gateway to expose standard MCP servers as SSE interfaces.

---

## Getting Started

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FRESHDESK_DOMAIN` | The subdomain of your Freshdesk instance (e.g. `yourcompany` from `yourcompany.freshdesk.com`). | (Required) |
| `FRESHDESK_API_KEY` | Your Freshdesk API key (found under Profile Settings -> API Key). | (Required) |
| `TOOL_ROUTING` | Set to `true` to enable semantic tool routing (only registers 2 base tools). | `false` |
| `ENABLE_CONTEXTFORGE_GATEWAY` | Run the server through an SSE gateway instead of stdio. | `false` |
| `GATEWAY_PORT` | The port ContextForge Gateway binds to. | `8000` |

---

## Client Integration

### VS Code MCP Configuration

Create a `.vscode/mcp.json` file in your workspace:

```json
{
  "servers": {
    "freshdesk": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "FRESHDESK_DOMAIN",
        "-e", "FRESHDESK_API_KEY",
        "-e", "TOOL_ROUTING",
        "ghcr.io/jelmervdm/freshdesk-mcp:latest"
      ],
      "env": {
        "FRESHDESK_DOMAIN": "yourcompany",
        "FRESHDESK_API_KEY": "your_api_key_here",
        "TOOL_ROUTING": "false"
      }
    }
  }
}
```

### Python execution via uvx

If you prefer to run directly without Docker:

```json
{
  "servers": {
    "freshdesk": {
      "command": "uvx",
      "args": ["freshdesk-mcp-server"],
      "env": {
        "FRESHDESK_DOMAIN": "yourcompany",
        "FRESHDESK_API_KEY": "your_api_key_here",
        "TOOL_ROUTING": "false"
      }
    }
  }
}
```

---

## Semantic Tool Routing

When your MCP server has many tools, it can consume a large amount of LLM context window. To solve this, you can enable `TOOL_ROUTING=true`.

When enabled, only 2 tools are exposed to the LLM:
1. `route_tools` - Search for relevant tools using a natural language query (e.g. *"find tools to reply to tickets"*).
2. `call_routed_tool` - Invoke one of the discovered/activated tools.

This uses a local CPU embedding model (`fastembed` with `BAAI/bge-small-en-v1.5`) to perform similarity search in 5-10ms.

---

## Local Development

### Installation

Clone the repository and install it in editable mode with development and router dependencies:

```bash
pip install -e ".[dev,router]"
```

### Running Tests

Run the test suite using `pytest`:

```bash
pytest tests/ -v
```

### Linting and Typing

Run style and static analysis checks:

```bash
flake8 src/
mypy src/
```

### Containerization

Build the Docker image locally:

```bash
docker build -t freshdesk-mcp:latest .
```

Run via Docker Compose:

```bash
docker-compose up -d
```

---

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
