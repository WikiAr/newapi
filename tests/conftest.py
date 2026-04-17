from unittest.mock import MagicMock

import pytest
from newapi import Login


@pytest.fixture(autouse=True)
def mock_get_session(mocker):
    """
    Directly mocks get_session to return a controlled session object
    for all tests automatically.
    """
    # 1. Create a mock session object
    mock_session = MagicMock()

    # 2. Create a mock response object
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}

    # 3. Link the session methods to return the mock response
    # This covers cases like: session.get(), session.post(), or session.request()
    mock_session.get.return_value = mock_response
    mock_session.post.return_value = mock_response
    mock_session.request.return_value = mock_response

    # 4. Patch the get_session function in the target module
    # Note: Replace 'newapi.super.bot' with the actual import path
    mocker.patch("newapi.super.bot.get_session", return_value=mock_session)
    mocker.patch("newapi.super.bot_new.get_session", return_value=mock_session)

    return mock_session


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


@pytest.fixture
def mock_login_client(user_credentials) -> Login:
    bot = Login("ar", family="wikipedia")
    bot.add_User_tables("wikipedia", user_credentials)
    return bot
