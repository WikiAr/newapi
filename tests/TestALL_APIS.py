from unittest.mock import MagicMock, patch

import pytest
from newapi import AllAPIS


@pytest.fixture
def mock_dependencies():
    with (
        patch("newapi.client_wiki.all_apis.WikiLoginClient") as mock_login,
        patch("newapi.client_wiki.all_apis.super_page.MainPage") as mock_main_page,
        patch("newapi.client_wiki.all_apis.catdepth_new.subcatquery") as mock_subcatquery,
        patch("newapi.client_wiki.all_apis.bot_api.NewApi") as mock_new_api,
    ):
        mock_login_instance = MagicMock()
        mock_login.return_value = mock_login_instance

        yield {
            "WikiLoginClient": mock_login,
            "LoginInstance": mock_login_instance,
            "MainPage": mock_main_page,
            "subcatquery": mock_subcatquery,
            "NewApi": mock_new_api,
        }


def test_all_apis_init(mock_dependencies):
    lang, family, username, password = "en", "wikipedia", "user", "pass"
    api = AllAPIS(lang, family, username, password)

    assert api.lang == lang
    assert api.family == family
    assert api.username == username
    assert api.password == password

    mock_dependencies["WikiLoginClient"].assert_called_once_with(
        lang=lang, family=family, username=username, password=password
    )


def test_all_apis_main_page(mock_dependencies):
    api = AllAPIS("en", "wikipedia", "user", "pass")
    title = "Test Page"

    api.MainPage(title)

    mock_dependencies["MainPage"].assert_called_once_with(
        mock_dependencies["LoginInstance"], title, "en", family="wikipedia"
    )


def test_all_apis_cat_depth(mock_dependencies):
    api = AllAPIS("en", "wikipedia", "user", "pass")
    title = "Category:Test"

    api.CatDepth(title, depth=2)

    mock_dependencies["subcatquery"].assert_called_once_with(
        mock_dependencies["LoginInstance"],
        title,
        sitecode="en",
        family="wikipedia",
        depth=2,
    )


def test_all_apis_new_api(mock_dependencies):
    api = AllAPIS("en", "wikipedia", "user", "pass")

    api.NewApi()

    mock_dependencies["NewApi"].assert_called_once_with(
        mock_dependencies["LoginInstance"], lang="en", family="wikipedia"
    )
