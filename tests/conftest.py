
from unittest.mock import MagicMock

import pytest

from newapi import Login


@pytest.fixture(scope="session")
def api_credentials():
    from newapi import useraccount

    return {"username": useraccount.username, "password": useraccount.password}


@pytest.fixture
def temp_test_page():
    return "User:TestBot/pytest_sandbox"


@pytest.fixture
def user_credentials():
    return {"username": "username", "password": "password"}


@pytest.fixture(autouse=True)
def mock_super_botnew_requests(mocker):
    """
    Fixture to mock the 'requests' module inside the target bot module.
    """
    # Patch the requests module in the target path
    mock_req = mocker.patch("newapi.super.bot_new.requests")

    # Setup a mock response object
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}

    # Configure the mock to return the response for common HTTP methods
    mock_req.get.return_value = mock_response
    mock_req.post.return_value = mock_response
    mock_req.request.return_value = mock_response

    return mock_req


@pytest.fixture(autouse=True)
def mock_super_bot_requests(mocker):
    """
    Fixture to mock the 'requests' module inside the target bot module.
    """
    # Patch the requests module in the target path
    mock_req = mocker.patch("newapi.super.bot.requests")

    # Setup a mock response object
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}

    # Configure the mock to return the response for common HTTP methods
    mock_req.get.return_value = mock_response
    mock_req.post.return_value = mock_response
    mock_req.request.return_value = mock_response

    return mock_req


@pytest.fixture
def mock_login_client(user_credentials, mock_super_bot_requests) -> Login:
    bot = Login("ar", family="wikipedia")
    bot.add_User_tables("wikipedia", user_credentials)
    return bot
