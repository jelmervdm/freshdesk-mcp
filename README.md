# Freshdesk MCP Server

[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://github.com/jelmervdm/freshdesk-mcp)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](pyproject.toml)
[![TDQS Score](https://img.shields.io/badge/TDQS-4.70%2F5.00%20(Tier%20A%2B)-success.svg)](https://github.com/glama-ai/tool-definition-quality-score)

An MCP (Model Context Protocol) server that exposes Freshdesk helpdesk operations as tools. This allows MCP-compatible AI assistants and clients (e.g. Claude Desktop, VS Code, Cursor) to list, search, create, and manage tickets, contacts, agents, and groups directly.

---

## 🏆 Tool Definition Quality Score (TDQS)

This server is audited against the **[Tool Definition Quality Score (TDQS)](https://github.com/glama-ai/tool-definition-quality-score)** framework to guarantee optimal function calling, type safety, and runtime safety for LLMs:
- **Score:** `4.70 / 5.00` (**Tier A+**)
- **Behavioral Annotations (`ToolAnnotations`):** 100% of tools specify `readOnlyHint`, `destructiveHint`, and `idempotentHint` metadata.
- **Parameter Descriptions:** 100% of tool parameters use explicit Pydantic `Annotated[T, Field(description=...)]` metadata.
- **Operational Guidelines:** Standardized docstrings detailing explicit "Use when..." context across all 35 tools.

---

## Features

- **Ticket Management**: Create, list, search, view, update, delete, restore tickets, add replies, add private notes, and inspect ticket fields metadata.
- **Company Management**: Create, list, search, view, update, and delete customer companies.
- **Contact Management**: Create, list, search, view, update, and delete customer contacts.
- **Time Tracking**: List, log, update, and delete billable/non-billable time entries on tickets.
- **Solutions Knowledge Base**: Browse categories, folders, articles, and search knowledge base solutions.
- **Support Staff (Agents & Groups)**: List agents and ticket assignment groups.
- **MCP Resources & Prompts**: Dynamic resources (`freshdesk://ticket-fields`, `freshdesk://agents`) and workflow prompt templates (`triage_ticket`, `draft_reply`).
- **Async HTTP Client**: Non-blocking `httpx.AsyncClient` context for fast, efficient API calls.
- **Tool Routing**: Enable semantic search routing (`TOOL_ROUTING=true`) to dramatically reduce LLM context usage.
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

### VS Code & Antigravity IDE MCP Configuration

Create a `.vscode/mcp.json` file in your workspace (or add to your IDE's MCP settings):

#### Option 1: Docker / Podman

Podman is fully supported on Fedora/RHEL and works as a rootless drop-in replacement for Docker:

```json
{
  "mcpServers": {
    "freshdesk": {
      "command": "podman",
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

> **Tip for Docker vs Podman**: Simply replace `"command": "podman"` with `"command": "docker"` if using standard Docker or the `podman-docker` alias. Always use `-i` (interactive stdin) and **never** `-t` (TTY), as TTY mode appends carriage returns (`\r\n`) that disrupt JSON-RPC communication over stdio.

#### Option 2: Local Python execution (without PyPI)

If you prefer to run directly from source without containers:

**Via `uv` (local workspace directory):**
```json
{
  "mcpServers": {
    "freshdesk": {
      "command": "uv",
      "args": ["--directory", "/path/to/freshdesk-mcp", "run", "freshdesk-mcp-server"],
      "env": {
        "FRESHDESK_DOMAIN": "yourcompany",
        "FRESHDESK_API_KEY": "your_api_key_here",
        "TOOL_ROUTING": "false"
      }
    }
  }
}
```

**Via `python` (editable install `pip install -e .`):**
```json
{
  "mcpServers": {
    "freshdesk": {
      "command": "python",
      "args": ["-m", "freshdesk_mcp.server"],
      "env": {
        "FRESHDESK_DOMAIN": "yourcompany",
        "FRESHDESK_API_KEY": "your_api_key_here",
        "TOOL_ROUTING": "false"
      }
    }
  }
}
```

**Via `uvx` directly from GitHub repository:**
```json
{
  "mcpServers": {
    "freshdesk": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/jelmervdm/freshdesk-mcp.git", "freshdesk-mcp-server"],
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
