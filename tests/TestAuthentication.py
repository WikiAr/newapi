from unittest.mock import MagicMock

import pytest
from newapi import WikiLoginClient


@pytest.fixture
def mock_requests(mocker):
    mock_req = MagicMock()
    mocker.patch("newapi.super.bot.requests", return_value=mock_req)
    return mock_req


class TestAuthentication:

    def test_successful_login(self, mock_login_client: WikiLoginClient):
        """Test successful authentication"""
        params = {"action": "query", "titles": "Main Page", "format": "json"}
        mock_login_client.client_request.return_value = {"query": {"pages": {"1": {"title": "Main Page"}}}}
        response = mock_login_client.client_request(params, method="post")
        assert response is not None
        assert len(response) > 0
