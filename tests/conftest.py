from unittest.mock import MagicMock

import pytest
from newapi import WikiLoginClient
from pytest_socket import disable_socket


@pytest.fixture(autouse=True)
def stop_nets() -> None:
    disable_socket(allow_unix_socket=True)


@pytest.fixture
def temp_test_page() -> str:
    return "User:TestBot/pytest_sandbox"


@pytest.fixture
def user_credentials():
    return {"username": "username", "password": "password"}


@pytest.fixture
def mock_login_client(user_credentials) -> WikiLoginClient:
    bot = MagicMock(spec=WikiLoginClient)
    return bot
