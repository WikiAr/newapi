from unittest.mock import MagicMock, patch

import pytest
from newapi import ALL_APIS


@pytest.fixture
def mock_dependencies():
    with (
        patch("newapi.pages_bots.all_apis.Login") as mock_login,
        patch("newapi.pages_bots.all_apis.super_page.MainPage") as mock_main_page,
        patch("newapi.pages_bots.all_apis.catdepth_new.subcatquery") as mock_subcatquery,
        patch("newapi.pages_bots.all_apis.bot_api.NEW_API") as mock_new_api,
        patch("newapi.pages_bots.all_apis.printe") as mock_printe,
    ):

        # Setup mock login instance
        mock_login_instance = MagicMock()
        mock_login.return_value = mock_login_instance

        yield {
            "Login": mock_login,
            "LoginInstance": mock_login_instance,
            "MainPage": mock_main_page,
            "subcatquery": mock_subcatquery,
            "NEW_API": mock_new_api,
            "printe": mock_printe,
        }


def test_all_apis_init(mock_dependencies):
    lang, family, username, password = "en", "wikipedia", "user", "pass"
    api = ALL_APIS(lang, family, username, password)

    assert api.lang == lang
    assert api.family == family
    assert api.username == username
    assert api.password == password

    # Verify login was called
    mock_dependencies["Login"].assert_called_once_with(lang, family=family)
    mock_dependencies["LoginInstance"].add_users.assert_called_once()

    # Verify printe.output was called
    mock_dependencies["printe"].output.assert_called()


def test_all_apis_main_page(mock_dependencies):
    api = ALL_APIS("en", "wikipedia", "user", "pass")
    title = "Test Page"

    api.MainPage(title)

    mock_dependencies["MainPage"].assert_called_once_with(
        mock_dependencies["LoginInstance"], title, "en", family="wikipedia"
    )


def test_all_apis_cat_depth(mock_dependencies):
    api = ALL_APIS("en", "wikipedia", "user", "pass")
    title = "Category:Test"

    api.CatDepth(title, depth=2)

    mock_dependencies["subcatquery"].assert_called_once_with(
        mock_dependencies["LoginInstance"], title, sitecode="en", family="wikipedia", depth=2
    )


def test_all_apis_new_api(mock_dependencies):
    api = ALL_APIS("en", "wikipedia", "user", "pass")

    api.NEW_API()

    mock_dependencies["NEW_API"].assert_called_once_with(
        mock_dependencies["LoginInstance"], lang="en", family="wikipedia"
    )


def test_login_lru_cache(mock_dependencies):
    api = ALL_APIS("en", "wikipedia", "user", "pass")

    # Call _login multiple times
    api._login()
    api._login()

    # Login should only be instantiated once due to lru_cache
    # Note: __init__ calls _login once, so total calls should be 1
    assert mock_dependencies["Login"].call_count == 1
