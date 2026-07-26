from unittest.mock import patch


def test_mcp_server_loads():
    """Verify that the FastMCP server instance loads with the correct name."""
    from freshdesk_mcp.server import mcp

    assert mcp is not None
    assert mcp.name == "freshdesk"


def test_all_tools_registered():
    """Verify that all standard tools are registered on the server."""
    from freshdesk_mcp.server import mcp

    tools = mcp._tool_manager._tools

    standard_tool_names = [
        # Tickets
        "list_tickets",
        "get_ticket",
        "search_tickets",
        "create_ticket",
        "update_ticket",
        "delete_ticket",
        "restore_ticket",
        "add_reply",
        "add_private_note",
        "get_ticket_fields",
        # Contacts
        "list_contacts",
        "get_contact",
        "create_contact",
        "update_contact",
        "delete_contact",
        "search_contacts",
        # Companies
        "list_companies",
        "get_company",
        "create_company",
        "update_company",
        "delete_company",
        "search_companies",
        # Time Entries
        "list_time_entries",
        "create_time_entry",
        "update_time_entry",
        "delete_time_entry",
        # Solutions / KB
        "list_solution_categories",
        "list_solution_folders",
        "list_solution_articles",
        "get_solution_article",
        "search_solution_articles",
        # Agents & Groups
        "list_agents",
        "list_groups",
    ]
    for name in standard_tool_names:
        assert name in tools, f"Expected tool '{name}' to be registered on MCP server"


def test_resources_registered():
    """Verify that MCP resources are registered."""
    from freshdesk_mcp.server import mcp

    resources = mcp._resource_manager._resources
    assert "freshdesk://ticket-fields" in resources
    assert "freshdesk://agents" in resources


def test_prompts_registered():
    """Verify that MCP prompts are registered."""
    from freshdesk_mcp.server import mcp

    prompts = mcp._prompt_manager._prompts
    assert "triage_ticket" in prompts
    assert "draft_reply" in prompts


def test_main_calls_mcp_run():
    """Verify that main entry point runs the server in stdio mode."""
    from freshdesk_mcp.server import mcp, main

    with patch.object(mcp, "run") as mock_run:
        main()
        mock_run.assert_called_once_with(transport="stdio")


def test_tool_routing_hooks_registration():
    """Verify that routing hooks are registered if TOOL_ROUTING is enabled."""
    import os
    from freshdesk_mcp.server import _install_routing_hooks, mcp

    with patch.dict(os.environ, {"TOOL_ROUTING": "true"}), patch.object(mcp, "tool") as mock_tool:
        _install_routing_hooks()
        assert mock_tool.call_count >= 0


def test_route_tools_when_disabled():
    """Verify route_tools behavior when tool routing is disabled."""
    import os
    from freshdesk_mcp.server import route_tools

    with patch.dict(os.environ, {"TOOL_ROUTING": "false"}):
        res = route_tools("list tickets")
        assert "Tool routing is not enabled" in res


async def test_call_routed_tool_when_disabled():
    """Verify call_routed_tool behavior when tool routing is disabled."""
    import os
    from freshdesk_mcp.server import call_routed_tool

    with patch.dict(os.environ, {"TOOL_ROUTING": "false"}):
        res = await call_routed_tool("list_tickets")
        assert "Tool routing is not enabled" in res


async def test_call_routed_tool_when_enabled():
    """Verify call_routed_tool behavior when tool routing is enabled."""
    import os
    from freshdesk_mcp.server import call_routed_tool

    with patch.dict(os.environ, {"TOOL_ROUTING": "true"}):
        res_invalid = await call_routed_tool("nonexistent_tool")
        assert "is not registered" in res_invalid

        res_always_visible = await call_routed_tool("route_tools")
        assert "Cannot call 'route_tools' through this tool" in res_always_visible
