import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Set dummy environment variables before importing freshdesk_mcp
os.environ["FRESHDESK_DOMAIN"] = "testcompany"
os.environ["FRESHDESK_API_KEY"] = "testkey"


@pytest.fixture
def mock_httpx_client():
    """Fixture that mocks the httpx.AsyncClient context manager."""
    client_mock = MagicMock()
    context_client = AsyncMock()
    client_mock.__aenter__.return_value = context_client

    with patch("freshdesk_mcp.client._client", return_value=client_mock):
        yield context_client
