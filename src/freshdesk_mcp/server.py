import logging
import os
from typing import Any

from mcp.server.fastmcp import FastMCP, Context

from freshdesk_mcp.router import get_router
from freshdesk_mcp.tools import tickets, contacts, agents

logger = logging.getLogger(__name__)

mcp = FastMCP("freshdesk")

# Register all domain-specific tool modules
tickets.register(mcp)
contacts.register(mcp)
agents.register(mcp)


# ---------------------------------------------------------------------------
# Tool Routing
# ---------------------------------------------------------------------------

_ALWAYS_VISIBLE = {"route_tools", "call_routed_tool"}
_active_tools: dict[str, Any] = {}
_router_indexed = False


def _is_routed_mode() -> bool:
    return os.environ.get("TOOL_ROUTING", "").lower() in ("1", "true", "yes")


def _all_tools() -> list[Any]:
    """Return every registered tool (bypasses filtering)."""
    tm = mcp._tool_manager  # type: ignore[attr-defined]
    return list(tm._tools.values())  # type: ignore[attr-defined]


def _ensure_router_indexed() -> None:
    """Lazily initialise the router and build the embedding index."""
    global _router_indexed
    if _router_indexed:
        return

    router = get_router()
    if router is None:
        return

    all_tools = _all_tools()
    tool_pairs = [(t.name, (t.description or t.name)[:200]) for t in all_tools]
    router.index(tool_pairs)
    _router_indexed = True


def _filtered_list_tools() -> list[Any]:
    """Return only the base tools (static)."""
    tm = mcp._tool_manager  # type: ignore[attr-defined]
    return [t for t in tm._tools.values() if t.name in _ALWAYS_VISIBLE]  # type: ignore[attr-defined]


def _tool_summary(tool: Any) -> str:
    """Compact one-line summary: name(params) — description."""
    params = tool.parameters or {}
    props = params.get("properties", {})
    required = set(params.get("required", []))
    parts = []
    for pname, pinfo in props.items():
        if pname == "ctx":
            continue
        typ = pinfo.get("type", "any")
        suffix = "" if pname in required else "?"
        parts.append(f"{pname}: {typ}{suffix}")
    sig = ", ".join(parts)
    desc = (tool.description or "").split("\n")[0][:120]
    return f"{tool.name}({sig}) — {desc}"


@mcp.tool()
def route_tools(query: str) -> str:
    """Find tools relevant to your task. Call this FIRST, then use call_routed_tool to invoke them.

    Returns a list of matching tool names with their parameters. Pass the
    exact tool name and a JSON arguments object to call_routed_tool.

    Args:
        query: Natural-language description of what you want to do (e.g. "list all tickets").
    """
    global _active_tools

    if not _is_routed_mode():
        return "Tool routing is not enabled. All tools are already visible."

    _ensure_router_indexed()

    router = get_router()
    if router is None:
        return "Router failed to initialise."

    results = router.search(query)

    # Build name → tool mapping for the activated set
    tm = mcp._tool_manager  # type: ignore[attr-defined]
    _active_tools = {
        name: tm._tools[name]  # type: ignore[attr-defined]
        for name in results
        if name in tm._tools  # type: ignore[attr-defined]
    }

    logger.info("route_tools(%r) → %d tools activated", query, len(_active_tools))

    lines = [f"Found {len(_active_tools)} tools. Use call_routed_tool(name, arguments) to invoke one:\n"]
    for tool in _active_tools.values():
        lines.append(f"  {_tool_summary(tool)}")
    return "\n".join(lines)


@mcp.tool()
async def call_routed_tool(name: str, arguments: str = "{}", ctx: Context = None) -> str:  # type: ignore[assignment]
    """Invoke a tool returned by route_tools.

    Args:
        name: Exact tool name from route_tools output (e.g. "list_tickets").
        arguments: JSON object of arguments (e.g. '{"page": 1}').
    """
    import json as _json

    if not _is_routed_mode():
        return "Tool routing is not enabled."

    if name in _ALWAYS_VISIBLE:
        return f"Cannot call '{name}' through this tool. Call it directly."

    if name not in _active_tools:
        return f"Tool '{name}' is not active. Call route_tools first to find available tools."

    try:
        parsed = _json.loads(arguments) if arguments and arguments != "{}" else {}
    except _json.JSONDecodeError as e:
        return f"Invalid JSON arguments: {e}"

    tm = mcp._tool_manager  # type: ignore[attr-defined]
    result = await tm.call_tool(name, parsed, ctx)

    return str(result)


def _install_routing_hooks() -> None:
    """Patch FastMCP's tool manager so only the base tools are listed."""
    if not _is_routed_mode():
        logger.info("Tool routing disabled — all %d tools visible", len(mcp._tool_manager._tools))  # type: ignore[attr-defined]
        return

    logger.info("Tool routing enabled — only base tools visible")
    tm = mcp._tool_manager  # type: ignore[attr-defined]
    tm.list_tools = _filtered_list_tools  # type: ignore[method-assign]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server (stdio transport)."""
    logging.basicConfig(level=logging.INFO)
    _install_routing_hooks()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
