import pytest
from unittest.mock import MagicMock
from freshdesk_mcp import client
from freshdesk_mcp.server import mcp

# Retrieve registered tool functions from FastMCP registry
list_tickets = mcp._tool_manager._tools["list_tickets"].fn
get_ticket = mcp._tool_manager._tools["get_ticket"].fn
create_ticket = mcp._tool_manager._tools["create_ticket"].fn
update_ticket = mcp._tool_manager._tools["update_ticket"].fn
delete_ticket = mcp._tool_manager._tools["delete_ticket"].fn
restore_ticket = mcp._tool_manager._tools["restore_ticket"].fn
add_reply = mcp._tool_manager._tools["add_reply"].fn
add_private_note = mcp._tool_manager._tools["add_private_note"].fn
search_tickets = mcp._tool_manager._tools["search_tickets"].fn
get_ticket_fields = mcp._tool_manager._tools["get_ticket_fields"].fn
list_agents = mcp._tool_manager._tools["list_agents"].fn
list_groups = mcp._tool_manager._tools["list_groups"].fn

list_contacts = mcp._tool_manager._tools["list_contacts"].fn
get_contact = mcp._tool_manager._tools["get_contact"].fn
create_contact = mcp._tool_manager._tools["create_contact"].fn
update_contact = mcp._tool_manager._tools["update_contact"].fn
delete_contact = mcp._tool_manager._tools["delete_contact"].fn
search_contacts = mcp._tool_manager._tools["search_contacts"].fn

list_companies = mcp._tool_manager._tools["list_companies"].fn
get_company = mcp._tool_manager._tools["get_company"].fn
create_company = mcp._tool_manager._tools["create_company"].fn
update_company = mcp._tool_manager._tools["update_company"].fn
delete_company = mcp._tool_manager._tools["delete_company"].fn
search_companies = mcp._tool_manager._tools["search_companies"].fn

list_time_entries = mcp._tool_manager._tools["list_time_entries"].fn
create_time_entry = mcp._tool_manager._tools["create_time_entry"].fn
update_time_entry = mcp._tool_manager._tools["update_time_entry"].fn
delete_time_entry = mcp._tool_manager._tools["delete_time_entry"].fn

list_solution_categories = mcp._tool_manager._tools["list_solution_categories"].fn
list_solution_folders = mcp._tool_manager._tools["list_solution_folders"].fn
list_solution_articles = mcp._tool_manager._tools["list_solution_articles"].fn
get_solution_article = mcp._tool_manager._tools["get_solution_article"].fn
search_solution_articles = mcp._tool_manager._tools["search_solution_articles"].fn
raw_api_request = mcp._tool_manager._tools["raw_api_request"].fn


async def test_list_tickets(mock_httpx_client):
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

    tickets = await list_tickets(status="open", priority="low")
    assert len(tickets) == 1
    assert tickets[0]["id"] == 1
    assert tickets[0]["subject"] == "Test ticket"
    assert tickets[0]["status"] == "open"
    assert tickets[0]["priority"] == "low"

    mock_httpx_client.get.assert_called_once()
    args, kwargs = mock_httpx_client.get.call_args
    assert args[0] == "/tickets"
    assert kwargs["params"]["status"] == 2
    assert kwargs["params"]["priority"] == 1


async def test_get_ticket(mock_httpx_client):
    """Test get_ticket makes the correct request and returns details."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 42, "subject": "Specific Ticket"}
    mock_httpx_client.get.return_value = mock_response

    ticket = await get_ticket(42)
    assert ticket["id"] == 42
    assert ticket["subject"] == "Specific Ticket"


async def test_create_ticket(mock_httpx_client):
    """Test create_ticket parses input and invokes POST request."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 100, "subject": "New Ticket"}
    mock_httpx_client.post.return_value = mock_response

    ticket = await create_ticket(
        subject="New Ticket",
        description="Help me",
        email="user@test.com",
        priority="high",
        status="pending",
    )
    assert ticket["id"] == 100
    assert ticket["subject"] == "New Ticket"

    mock_httpx_client.post.assert_called_once()
    args, kwargs = mock_httpx_client.post.call_args
    assert args[0] == "/tickets"
    assert kwargs["json"]["priority"] == 3
    assert kwargs["json"]["status"] == 3


async def test_update_ticket(mock_httpx_client):
    """Test update_ticket with valid attributes sends PUT request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 100, "status": 4}
    mock_httpx_client.put.return_value = mock_response

    res = await update_ticket(ticket_id=100, status="resolved")
    assert res["status"] == 4

    mock_httpx_client.put.assert_called_once()
    args, kwargs = mock_httpx_client.put.call_args
    assert args[0] == "/tickets/100"
    assert kwargs["json"]["status"] == 4


async def test_delete_ticket(mock_httpx_client):
    """Test delete_ticket sends DELETE request."""
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_response.content = b""
    mock_httpx_client.delete.return_value = mock_response

    res = await delete_ticket(100)
    assert res == {"success": True}
    mock_httpx_client.delete.assert_called_once_with("/tickets/100")


async def test_restore_ticket(mock_httpx_client):
    """Test restore_ticket sends PUT request to /restore."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 100, "deleted": False}
    mock_httpx_client.put.return_value = mock_response

    res = await restore_ticket(100)
    assert res["id"] == 100
    mock_httpx_client.put.assert_called_once_with("/tickets/100/restore")


async def test_get_ticket_fields(mock_httpx_client):
    """Test get_ticket_fields fetches field definitions."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "name": "status", "label": "Status"}]
    mock_httpx_client.get.return_value = mock_response

    res = await get_ticket_fields()
    assert len(res) == 1
    assert res[0]["name"] == "status"
    mock_httpx_client.get.assert_called_once_with("/ticket_fields")


async def test_list_contacts(mock_httpx_client):
    """Test list_contacts forwards pagination parameters."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 5, "name": "Alice"}]
    mock_httpx_client.get.return_value = mock_response

    res = await list_contacts(page=2, per_page=10)
    assert len(res) == 1
    assert res[0]["name"] == "Alice"

    mock_httpx_client.get.assert_called_once()
    args, kwargs = mock_httpx_client.get.call_args
    assert args[0] == "/contacts"
    assert kwargs["params"]["page"] == 2
    assert kwargs["params"]["per_page"] == 10


async def test_companies_crud(mock_httpx_client):
    """Test list_companies, get_company, create_company, update_company, delete_company, search_companies."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 10, "name": "Acme Corp"}]
    mock_httpx_client.get.return_value = mock_response

    companies = await list_companies()
    assert len(companies) == 1
    assert companies[0]["name"] == "Acme Corp"

    # get_company
    mock_response.json.return_value = {"id": 10, "name": "Acme Corp", "note": "VIP client"}
    company = await get_company(10)
    assert company["note"] == "VIP client"

    # create_company
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 11, "name": "Beta LLC"}
    mock_httpx_client.post.return_value = mock_response
    new_company = await create_company("Beta LLC", domains=["beta.com"])
    assert new_company["id"] == 11

    # update_company
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 11, "name": "Beta Corp"}
    mock_httpx_client.put.return_value = mock_response
    updated = await update_company(11, name="Beta Corp")
    assert updated["name"] == "Beta Corp"

    # delete_company
    mock_response.status_code = 204
    mock_response.content = b""
    mock_httpx_client.delete.return_value = mock_response
    del_res = await delete_company(11)
    assert del_res == {"success": True}

    # search_companies
    mock_response.status_code = 200
    mock_response.content = b'{"results": [{"id": 10, "name": "Acme Corp"}]}'
    mock_response.json.return_value = {"results": [{"id": 10, "name": "Acme Corp"}]}
    mock_httpx_client.get.return_value = mock_response
    found = await search_companies("name:Acme")
    assert len(found) == 1
    assert found[0]["name"] == "Acme Corp"


async def test_time_entries(mock_httpx_client):
    """Test list_time_entries, create_time_entry, update_time_entry, delete_time_entry."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "time_spent": "01:30"}]
    mock_httpx_client.get.return_value = mock_response

    entries = await list_time_entries(100)
    assert len(entries) == 1
    assert entries[0]["time_spent"] == "01:30"

    mock_response.status_code = 201
    mock_httpx_client.post.return_value = mock_response
    created = await create_time_entry(100, time_spent="01:30", note="Debugging")
    assert created[0]["time_spent"] == "01:30"

    mock_response.status_code = 200
    mock_httpx_client.put.return_value = mock_response
    updated = await update_time_entry(1, time_spent="02:00")
    assert updated[0]["time_spent"] == "01:30"

    mock_response.status_code = 204
    mock_response.content = b""
    mock_httpx_client.delete.return_value = mock_response
    deleted = await delete_time_entry(1)
    assert deleted == {"success": True}


async def test_solutions_kb(mock_httpx_client):
    """Test solution categories, folders, articles, and article search."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "name": "General"}]
    mock_httpx_client.get.return_value = mock_response

    cats = await list_solution_categories()
    assert len(cats) == 1

    folders = await list_solution_folders(1)
    assert len(folders) == 1

    articles = await list_solution_articles(5)
    assert len(articles) == 1

    mock_response.json.return_value = {"id": 10, "title": "How to reset password"}
    article = await get_solution_article(10)
    assert article["title"] == "How to reset password"

    mock_response.content = b'{"results": [{"id": 10, "title": "How to reset password"}]}'
    mock_response.json.return_value = [{"id": 10, "title": "How to reset password"}]
    search_res = await search_solution_articles("password")
    assert len(search_res) == 1


def test_handle_response_error_formatting():
    """Test detailed error message formatting from Freshdesk response."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "description": "Validation failed",
        "errors": [{"field": "email", "message": "It should be a valid email address"}],
    }

    with pytest.raises(RuntimeError) as exc_info:
        client._handle_response(mock_response)

    assert (
        "Freshdesk API error 400: Validation failed: email: It should be a valid email address"
        in str(exc_info.value)
    )


def test_sanitize_domain():
    """Test domain sanitization helper."""
    assert client._sanitize_domain("mycompany") == "mycompany"
    assert client._sanitize_domain("mycompany.freshdesk.com") == "mycompany"
    assert client._sanitize_domain("https://mycompany.freshdesk.com") == "mycompany"
    assert client._sanitize_domain("http://mycompany.freshdesk.com/api/v2") == "mycompany"
    assert client._sanitize_domain(None) is None


def test_format_search_query():
    """Test search query formatting strips existing quotes cleanly."""
    assert client._format_search_query("status:2") == '"status:2"'
    assert client._format_search_query('"status:2 AND priority:3"') == '"status:2 AND priority:3"'
    assert client._format_search_query("'name:Acme'") == '"name:Acme"'


async def test_add_reply_and_note(mock_httpx_client):
    """Test add_reply and add_private_note."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 1, "body": "Thank you"}
    mock_httpx_client.post.return_value = mock_response

    reply = await add_reply(100, "Thank you")
    assert reply["body"] == "Thank you"

    note = await add_private_note(100, "Internal note", notify_agent_ids=[5])
    assert note["body"] == "Thank you"


async def test_search_tickets(mock_httpx_client):
    """Test search_tickets uses _format_search_query."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": [{"id": 1, "subject": "Found"}]}
    mock_httpx_client.get.return_value = mock_response

    res = await search_tickets('"subject:billing"')
    assert len(res) == 1
    assert res[0]["subject"] == "Found"
    mock_httpx_client.get.assert_called_once_with(
        "/search/tickets", params={"query": '"subject:billing"'}
    )


async def test_list_agents_and_groups(mock_httpx_client):
    """Test list_agents and list_groups."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "name": "Agent Smith"}]
    mock_httpx_client.get.return_value = mock_response

    agents = await list_agents()
    assert len(agents) == 1

    groups = await list_groups()
    assert len(groups) == 1


async def test_raw_api_request(mock_httpx_client):
    """Test raw_api_request supports HTTP methods, endpoint path normalization, params, and body payload."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "name": "Custom Field"}]
    mock_httpx_client.request.return_value = mock_response

    # Test GET request with path normalization and params
    res = await raw_api_request("get", "/api/v2/custom_objects", params={"page": 1})
    assert res == [{"id": 1, "name": "Custom Field"}]
    mock_httpx_client.request.assert_called_once_with(
        method="GET",
        url="/custom_objects",
        params={"page": 1},
        json=None,
    )
    mock_httpx_client.request.reset_mock()

    # Test POST request with body payload and path without leading slash
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 10, "status": "created"}
    res_post = await raw_api_request("POST", "custom_objects", data={"name": "New Object"})
    assert res_post == {"id": 10, "status": "created"}
    mock_httpx_client.request.assert_called_once_with(
        method="POST",
        url="/custom_objects",
        params=None,
        json={"name": "New Object"},
    )
    mock_httpx_client.request.reset_mock()

    # Test DELETE request
    mock_response.status_code = 204
    mock_response.content = b""
    res_del = await raw_api_request("DELETE", "/tickets/123")
    assert res_del == {"success": True}

    # Test invalid method raises ValueError
    with pytest.raises(ValueError) as exc_info:
        await raw_api_request("INVALID_METHOD", "/tickets")
    assert "Invalid HTTP method 'INVALID_METHOD'" in str(exc_info.value)
