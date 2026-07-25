from unittest.mock import MagicMock
from freshdesk_mcp.server import mcp

# Retrieve the registered tool functions from FastMCP registry
list_tickets = mcp._tool_manager._tools["list_tickets"].fn
get_ticket = mcp._tool_manager._tools["get_ticket"].fn
create_ticket = mcp._tool_manager._tools["create_ticket"].fn
update_ticket = mcp._tool_manager._tools["update_ticket"].fn
delete_ticket = mcp._tool_manager._tools["delete_ticket"].fn
list_contacts = mcp._tool_manager._tools["list_contacts"].fn


def test_list_tickets(mock_httpx_client):
    """Test list_tickets converts status/priority strings and simplifies response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": 1,
            "subject": "Test ticket",
            "status": 2,
            "priority": 1,
            "requester_id": 123,
            "responder_id": 456,
            "created_at": "2026-07-24T18:00:00Z",
            "updated_at": "2026-07-24T18:05:00Z",
            "tags": ["test"],
            "type": "Incident",
        }
    ]
    mock_httpx_client.get.return_value = mock_response

    tickets = list_tickets(status="open", priority="low")
    assert len(tickets) == 1
    assert tickets[0]["id"] == 1
    assert tickets[0]["subject"] == "Test ticket"
    assert tickets[0]["status"] == "open"
    assert tickets[0]["priority"] == "low"

    # Verify client was called with converted query params
    mock_httpx_client.get.assert_called_once()
    args, kwargs = mock_httpx_client.get.call_args
    assert args[0] == "/tickets"
    assert kwargs["params"]["status"] == 2
    assert kwargs["params"]["priority"] == 1


def test_get_ticket(mock_httpx_client):
    """Test get_ticket makes the correct request and returns details."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 42, "subject": "Specific Ticket"}
    mock_httpx_client.get.return_value = mock_response

    ticket = get_ticket(42)
    assert ticket["id"] == 42
    assert ticket["subject"] == "Specific Ticket"


def test_create_ticket(mock_httpx_client):
    """Test create_ticket parses input and invokes POST request."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 100, "subject": "New Ticket"}
    mock_httpx_client.post.return_value = mock_response

    ticket = create_ticket(
        subject="New Ticket",
        description="Help me",
        email="user@test.com",
        priority="high",
        status="pending"
    )
    assert ticket["id"] == 100
    assert ticket["subject"] == "New Ticket"

    mock_httpx_client.post.assert_called_once()
    args, kwargs = mock_httpx_client.post.call_args
    assert args[0] == "/tickets"
    assert kwargs["json"]["priority"] == 3
    assert kwargs["json"]["status"] == 3


def test_update_ticket(mock_httpx_client):
    """Test update_ticket with valid attributes sends PUT request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 100, "status": 4}
    mock_httpx_client.put.return_value = mock_response

    res = update_ticket(ticket_id=100, status="resolved")
    assert res["status"] == 4

    mock_httpx_client.put.assert_called_once()
    args, kwargs = mock_httpx_client.put.call_args
    assert args[0] == "/tickets/100"
    assert kwargs["json"]["status"] == 4


def test_delete_ticket(mock_httpx_client):
    """Test delete_ticket sends DELETE request."""
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_response.content = b""
    mock_httpx_client.delete.return_value = mock_response

    res = delete_ticket(100)
    assert res == {"success": True}
    mock_httpx_client.delete.assert_called_once_with("/tickets/100")


def test_list_contacts(mock_httpx_client):
    """Test list_contacts forwards pagination parameters."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 5, "name": "Alice"}]
    mock_httpx_client.get.return_value = mock_response

    res = list_contacts(page=2, per_page=10)
    assert len(res) == 1
    assert res[0]["name"] == "Alice"

    mock_httpx_client.get.assert_called_once()
    args, kwargs = mock_httpx_client.get.call_args
    assert args[0] == "/contacts"
    assert kwargs["params"]["page"] == 2
    assert kwargs["params"]["per_page"] == 10
