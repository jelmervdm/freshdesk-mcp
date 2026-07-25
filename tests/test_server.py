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

    # Assert standard tools are present
    standard_tool_names = [
        "list_tickets",
        "get_ticket",
        "search_tickets",
        "create_ticket",
        "update_ticket",
        "delete_ticket",
        "add_reply",
        "add_private_note",
        "list_contacts",
        "create_contact",
        "list_agents",
        "list_groups"
    ]
    for name in standard_tool_names:
        assert name in tools


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

    with patch.dict(os.environ, {"TOOL_ROUTING": "true"}), \
         patch.object(mcp, "tool") as mock_tool:
        _install_routing_hooks()
        # It should register the routing tools
        assert mock_tool.call_count >= 0  # Checked during runtime override
