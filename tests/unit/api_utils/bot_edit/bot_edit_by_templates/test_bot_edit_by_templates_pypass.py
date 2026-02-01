""" """

import sys
from unittest.mock import MagicMock, patch

import pytest
from newapi.api_utils.bot_edit.bot_edit_by_templates import (
    Bot_Cache,
    is_bot_edit_allowed,
)

# ==================== Fixtures ====================


@pytest.fixture
def original_argv():
    """Store and restore original sys.argv."""
    original = sys.argv.copy()
    yield original
    sys.argv = original


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment before and after each test."""
    # Setup
    Bot_Cache.clear()
    original_argv = sys.argv.copy()
    sys.argv = ["test"]

    yield

    # Teardown
    Bot_Cache.clear()
    sys.argv = original_argv


@pytest.fixture
def mock_wtp():
    """Provide a mocked wikitextparser."""
    with patch("newapi.api_utils.bot_edit.bot_edit_by_templates.wtp") as mock:
        yield mock


@pytest.fixture
def create_mock_template():
    """Factory fixture for creating mock templates."""

    def _create_template(name, arguments=None):
        mock_template = MagicMock()
        mock_template.normal_name.return_value = name
        mock_template.string = f"{{{{{name}}}}}"

        if arguments is None:
            mock_template.arguments = []
        else:
            mock_params = []
            for param_name, param_value in arguments.items():
                mock_param = MagicMock()
                mock_param.name = param_name
                mock_param.value = param_value
                mock_params.append(mock_param)
            mock_template.arguments = mock_params

        return mock_template

    return _create_template


@pytest.fixture
def setup_parser(mock_wtp, create_mock_template):
    """Factory fixture for setting up parser with templates."""

    def _setup(templates_config):
        templates = []
        for config in templates_config:
            if isinstance(config, dict):
                name = config.get("name")
                arguments = config.get("arguments")
                templates.append(create_mock_template(name, arguments))
            else:
                # If just a string, create template with that name
                templates.append(create_mock_template(config))

        mock_parser = MagicMock()
        mock_parser.templates = templates
        mock_wtp.parse.return_value = mock_parser

        return mock_parser

    return _setup


# ==================== Command Line Bypass Tests ====================


class TestCommandLineBypass:
    """Test command line argument bypass functionality."""

    @pytest.mark.parametrize("argv_value", ["botedit", "editbot", "workibrahem"])
    def test_argv_bypasses_all_checks(self, argv_value, setup_parser):
        """Test that specific argv values bypass all restrictions."""
        sys.argv.append(argv_value)
        setup_parser([{"name": "nobots", "arguments": None}])

        text = "{{nobots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True


class TestBypassConditions:
    """Test cases for bypass conditions via command line arguments."""

    def test_bypass_with_botedit_arg(self, original_argv):
        """Should return True when 'botedit' is in sys.argv."""
        sys.argv = ["script", "botedit"]
        text = "{{nobots}}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bypass_with_editbot_arg(self, original_argv):
        """Should return True when 'editbot' is in sys.argv."""
        sys.argv = ["script", "editbot"]
        text = "{{nobots}}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bypass_with_workibrahem_arg(self, original_argv):
        """Should return True when 'workibrahem' is in sys.argv."""
        sys.argv = ["script", "workibrahem"]
        text = "{{nobots}}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_no_bypass_without_args(self, original_argv):
        """Should check templates when no bypass args are present."""
        sys.argv = ["script"]
        text = "{{nobots}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")
