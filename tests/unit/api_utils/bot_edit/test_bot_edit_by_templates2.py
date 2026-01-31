"""
Comprehensive unit tests for is_bot_edit_allowed function.

Tests cover various scenarios including:
- Template restrictions (nobots, bots, custom templates)
- Bot job types
- Parameter combinations
- Edge cases and special conditions
"""

import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock the wikitextparser module before importing
sys.modules['wikitextparser'] = MagicMock()
sys.modules['newapi'] = MagicMock()
sys.modules['newapi.api_utils'] = MagicMock()

from newapi.api_utils.bot_edit.bot_edit_by_templates import (
    is_bot_edit_allowed,
    Bot_Cache,
    stop_edit_temps,
)


class TestIsBotEditAllowed(unittest.TestCase):
    """Test suite for is_bot_edit_allowed function."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear the cache before each test
        Bot_Cache.clear()

        # Remove command line arguments that bypass checks
        original_argv = sys.argv.copy()
        sys.argv = ['test']
        self.addCleanup(lambda: setattr(sys, 'argv', original_argv))

    def tearDown(self):
        """Clean up after each test method."""
        Bot_Cache.clear()

    # ==================== Basic Functionality Tests ====================

    def test_empty_text_allows_edit(self):
        """Test that empty text allows bot editing."""
        result = is_bot_edit_allowed(text="", title_page="Test Page", botjob="all")
        self.assertTrue(result)

    def test_plain_text_allows_edit(self):
        """Test that plain text without templates allows bot editing."""
        text = "This is just plain text without any templates."
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    def test_default_botjob_parameter(self):
        """Test that empty botjob defaults to 'all'."""
        text = "Plain text"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="")
        self.assertTrue(result)

    # ==================== Cache Tests ====================

    def test_cache_hit_returns_cached_value(self):
        """Test that cached results are returned on subsequent calls."""
        text = "Plain text"
        title = "Test Page"
        botjob = "all"

        # First call - should process and cache
        result1 = is_bot_edit_allowed(text=text, title_page=title, botjob=botjob)

        # Second call - should use cache
        result2 = is_bot_edit_allowed(text=text, title_page=title, botjob=botjob)

        self.assertEqual(result1, result2)
        self.assertIn(botjob, Bot_Cache)
        self.assertIn(title, Bot_Cache[botjob])

    def test_cache_separate_for_different_botjobs(self):
        """Test that cache is separate for different bot jobs."""
        text = "Plain text"
        title = "Test Page"

        result1 = is_bot_edit_allowed(text=text, title_page=title, botjob="all")
        result2 = is_bot_edit_allowed(text=text, title_page=title, botjob="cat")

        self.assertIn("all", Bot_Cache)
        self.assertIn("cat", Bot_Cache)

    # ==================== Command Line Bypass Tests ====================

    def test_botedit_argv_bypasses_all_checks(self):
        """Test that 'botedit' in sys.argv bypasses all restrictions."""
        sys.argv.append('botedit')
        text = "{{nobots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    def test_editbot_argv_bypasses_all_checks(self):
        """Test that 'editbot' in sys.argv bypasses all restrictions."""
        sys.argv.append('editbot')
        text = "{{nobots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    def test_workibrahem_argv_bypasses_all_checks(self):
        """Test that 'workibrahem' in sys.argv bypasses all restrictions."""
        sys.argv.append('workibrahem')
        text = "{{nobots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    # ==================== Nobots Template Tests ====================

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_nobots_template_without_params_denies_edit(self, mock_wtp):
        """Test that {{nobots}} without parameters denies editing."""
        # Mock the template
        mock_template = MagicMock()
        mock_template.normal_name.return_value = "nobots"
        mock_template.arguments = []
        mock_template.string = "{{nobots}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{nobots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_nobots_template_with_all_denies_edit(self, mock_wtp):
        """Test that {{nobots|1=all}} denies editing."""
        mock_param = MagicMock()
        mock_param.name = "1"
        mock_param.value = "all"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "nobots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{nobots|1=all}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{nobots|1=all}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_nobots_template_with_specific_bot_denies_edit(self, mock_wtp):
        """Test that {{nobots|1=Mr.Ibrahembot}} denies editing."""
        mock_param = MagicMock()
        mock_param.name = "1"
        mock_param.value = "Mr.Ibrahembot"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "nobots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{nobots|1=Mr.Ibrahembot}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{nobots|1=Mr.Ibrahembot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_nobots_template_with_bot_list_including_our_bot_denies(self, mock_wtp):
        """Test that {{nobots|1=Bot1,Mr.Ibrahembot,Bot2}} denies editing."""
        mock_param = MagicMock()
        mock_param.name = "1"
        mock_param.value = "Bot1,Mr.Ibrahembot,Bot2"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "nobots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{nobots|1=Bot1,Mr.Ibrahembot,Bot2}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{nobots|1=Bot1,Mr.Ibrahembot,Bot2}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_nobots_template_with_other_bots_allows_edit(self, mock_wtp):
        """Test that {{nobots|1=OtherBot}} allows editing."""
        mock_param = MagicMock()
        mock_param.name = "1"
        mock_param.value = "OtherBot,AnotherBot"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "nobots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{nobots|1=OtherBot,AnotherBot}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{nobots|1=OtherBot,AnotherBot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_nobots_case_insensitive(self, mock_wtp):
        """Test that nobots template matching is case insensitive."""
        mock_template = MagicMock()
        mock_template.normal_name.return_value = "NoBots"
        mock_template.arguments = []
        mock_template.string = "{{NoBots}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{NoBots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    # ==================== Bots Template Tests ====================

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_template_without_params_denies_edit(self, mock_wtp):
        """Test that {{bots}} without parameters denies editing."""
        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = []
        mock_template.string = "{{bots}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_template_allow_all_allows_edit(self, mock_wtp):
        """Test that {{bots|allow=all}} allows editing."""
        mock_param = MagicMock()
        mock_param.name = "allow"
        mock_param.value = "all"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{bots|allow=all}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|allow=all}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_template_allow_specific_bot_allows_edit(self, mock_wtp):
        """Test that {{bots|allow=Mr.Ibrahembot}} allows editing."""
        mock_param = MagicMock()
        mock_param.name = "allow"
        mock_param.value = "Mr.Ibrahembot"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{bots|allow=Mr.Ibrahembot}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|allow=Mr.Ibrahembot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_template_allow_bot_list_including_our_bot_allows(self, mock_wtp):
        """Test that {{bots|allow=Bot1,Mr.Ibrahembot,Bot2}} allows editing."""
        mock_param = MagicMock()
        mock_param.name = "allow"
        mock_param.value = "Bot1,Mr.Ibrahembot,Bot2"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{bots|allow=Bot1,Mr.Ibrahembot,Bot2}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|allow=Bot1,Mr.Ibrahembot,Bot2}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_template_allow_none_denies_edit(self, mock_wtp):
        """Test that {{bots|allow=none}} denies editing."""
        mock_param = MagicMock()
        mock_param.name = "allow"
        mock_param.value = "none"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{bots|allow=none}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|allow=none}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_template_allow_other_bots_denies_edit(self, mock_wtp):
        """Test that {{bots|allow=OtherBot}} denies editing."""
        mock_param = MagicMock()
        mock_param.name = "allow"
        mock_param.value = "OtherBot,AnotherBot"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{bots|allow=OtherBot,AnotherBot}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|allow=OtherBot,AnotherBot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_template_deny_all_denies_edit(self, mock_wtp):
        """Test that {{bots|deny=all}} denies editing."""
        mock_param = MagicMock()
        mock_param.name = "deny"
        mock_param.value = "all"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{bots|deny=all}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|deny=all}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_template_deny_specific_bot_denies_edit(self, mock_wtp):
        """Test that {{bots|deny=Mr.Ibrahembot}} denies editing."""
        mock_param = MagicMock()
        mock_param.name = "deny"
        mock_param.value = "Mr.Ibrahembot"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{bots|deny=Mr.Ibrahembot}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|deny=Mr.Ibrahembot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_template_deny_other_bots_allows_edit(self, mock_wtp):
        """Test that {{bots|deny=OtherBot}} allows editing."""
        mock_param = MagicMock()
        mock_param.name = "deny"
        mock_param.value = "OtherBot,AnotherBot"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{bots|deny=OtherBot,AnotherBot}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|deny=OtherBot,AnotherBot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_bots_case_insensitive(self, mock_wtp):
        """Test that bots template matching is case insensitive."""
        mock_param = MagicMock()
        mock_param.name = "allow"
        mock_param.value = "all"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "Bots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{Bots|allow=all}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{Bots|allow=all}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    # ==================== Stop Edit Templates Tests ====================

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_global_stop_template_denies_edit(self, mock_wtp):
        """Test that global stop templates deny editing."""
        for template_name in stop_edit_temps["all"]:
            with self.subTest(template=template_name):
                Bot_Cache.clear()

                mock_template = MagicMock()
                mock_template.normal_name.return_value = template_name
                mock_template.arguments = []
                mock_template.string = f"{{{{{template_name}}}}}"

                mock_parser = MagicMock()
                mock_parser.templates = [mock_template]
                mock_wtp.parse.return_value = mock_parser

                text = f"{{{{{template_name}}}}}"
                result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
                self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_specific_botjob_stop_template_denies_edit(self, mock_wtp):
        """Test that job-specific stop templates deny editing."""
        # Test تعريب job with its specific template
        mock_template = MagicMock()
        mock_template.normal_name.return_value = "لا للتعريب"
        mock_template.arguments = []
        mock_template.string = "{{لا للتعريب}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{لا للتعريب}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="تعريب")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_stop_template_for_different_botjob_allows_edit(self, mock_wtp):
        """Test that stop templates for different bot jobs allow editing."""
        # Template for تعريب job, but we're running cat job
        mock_template = MagicMock()
        mock_template.normal_name.return_value = "لا للتعريب"
        mock_template.arguments = []
        mock_template.string = "{{لا للتعريب}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{لا للتعريب}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="cat")
        self.assertTrue(result)

    # ==================== Multiple Templates Tests ====================

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_multiple_templates_first_restricting_denies(self, mock_wtp):
        """Test that first restricting template denies editing."""
        mock_template1 = MagicMock()
        mock_template1.normal_name.return_value = "nobots"
        mock_template1.arguments = []
        mock_template1.string = "{{nobots}}"

        mock_template2 = MagicMock()
        mock_template2.normal_name.return_value = "some_other_template"
        mock_template2.arguments = []
        mock_template2.string = "{{some_other_template}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template1, mock_template2]
        mock_wtp.parse.return_value = mock_parser

        text = "{{nobots}} {{some_other_template}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_multiple_non_restricting_templates_allows(self, mock_wtp):
        """Test that multiple non-restricting templates allow editing."""
        mock_template1 = MagicMock()
        mock_template1.normal_name.return_value = "infobox"
        mock_template1.arguments = []
        mock_template1.string = "{{infobox}}"

        mock_template2 = MagicMock()
        mock_template2.normal_name.return_value = "citation"
        mock_template2.arguments = []
        mock_template2.string = "{{citation}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template1, mock_template2]
        mock_wtp.parse.return_value = mock_parser

        text = "{{infobox}} {{citation}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    # ==================== Edge Cases and Special Conditions ====================

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_empty_template_parameters(self, mock_wtp):
        """Test handling of templates with empty parameter values."""
        mock_param = MagicMock()
        mock_param.name = "1"
        mock_param.value = ""  # Empty value

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "nobots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{nobots|1=}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{nobots|1=}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        # Empty params should be treated as no params
        self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_whitespace_in_bot_names(self, mock_wtp):
        """Test handling of whitespace in bot name lists."""
        mock_param = MagicMock()
        mock_param.name = "1"
        mock_param.value = " Bot1 , Mr.Ibrahembot , Bot2 "

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "nobots"
        mock_template.arguments = [mock_param]
        mock_template.string = "{{nobots|1= Bot1 , Mr.Ibrahembot , Bot2 }}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{nobots|1= Bot1 , Mr.Ibrahembot , Bot2 }}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertFalse(result)

    def test_fixref_cat_stub_tempcat_portal_defaults_to_all(self):
        """Test that combined botjob string defaults to 'all'."""
        text = "Plain text"
        result = is_bot_edit_allowed(
            text=text,
            title_page="Test Page",
            botjob="fixref|cat|stub|tempcat|portal"
        )
        self.assertTrue(result)
        self.assertIn("all", Bot_Cache)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_template_with_multiple_parameters(self, mock_wtp):
        """Test template with multiple parameters."""
        mock_param1 = MagicMock()
        mock_param1.name = "allow"
        mock_param1.value = "all"

        mock_param2 = MagicMock()
        mock_param2.name = "other_param"
        mock_param2.value = "some_value"

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param1, mock_param2]
        mock_template.string = "{{bots|allow=all|other_param=some_value}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|allow=all|other_param=some_value}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)

    # ==================== Integration Tests ====================

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_all_stop_templates_for_each_botjob(self, mock_wtp):
        """Test all stop templates for each specific bot job."""
        for botjob, templates in stop_edit_temps.items():
            if botjob == "all":
                continue
            for template_name in templates:
                with self.subTest(botjob=botjob, template=template_name):
                    Bot_Cache.clear()

                    mock_template = MagicMock()
                    mock_template.normal_name.return_value = template_name
                    mock_template.arguments = []
                    mock_template.string = f"{{{{{template_name}}}}}"

                    mock_parser = MagicMock()
                    mock_parser.templates = [mock_template]
                    mock_wtp.parse.return_value = mock_parser

                    text = f"{{{{{template_name}}}}}"
                    result = is_bot_edit_allowed(
                        text=text,
                        title_page="Test Page",
                        botjob=botjob
                    )
                    self.assertFalse(result)

    @patch('newapi.api_utils.bot_edit.bot_edit_by_templates.wtp')
    def test_parameter_filtering_empty_values(self, mock_wtp):
        """Test that parameters with empty values are filtered out."""
        mock_param1 = MagicMock()
        mock_param1.name = "allow"
        mock_param1.value = "all"

        mock_param2 = MagicMock()
        mock_param2.name = "empty_param"
        mock_param2.value = ""  # Empty - should be filtered

        mock_template = MagicMock()
        mock_template.normal_name.return_value = "bots"
        mock_template.arguments = [mock_param1, mock_param2]
        mock_template.string = "{{bots|allow=all|empty_param=}}"

        mock_parser = MagicMock()
        mock_parser.templates = [mock_template]
        mock_wtp.parse.return_value = mock_parser

        text = "{{bots|allow=all|empty_param=}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        self.assertTrue(result)


class TestBotCacheManagement(unittest.TestCase):
    """Test suite for bot cache management."""

    def setUp(self):
        """Set up test fixtures."""
        Bot_Cache.clear()
        sys.argv = ['test']

    def tearDown(self):
        """Clean up after tests."""
        Bot_Cache.clear()

    def test_cache_structure_created_correctly(self):
        """Test that cache structure is created correctly for new botjobs."""
        is_bot_edit_allowed(text="", title_page="Page1", botjob="cat")
        self.assertIn("cat", Bot_Cache)
        self.assertIsInstance(Bot_Cache["cat"], dict)

    def test_multiple_pages_cached_separately(self):
        """Test that different pages are cached separately."""
        is_bot_edit_allowed(text="", title_page="Page1", botjob="all")
        is_bot_edit_allowed(text="", title_page="Page2", botjob="all")

        self.assertIn("Page1", Bot_Cache["all"])
        self.assertIn("Page2", Bot_Cache["all"])

    def test_cache_persists_across_calls(self):
        """Test that cache persists across multiple function calls."""
        page = "Test Page"
        botjob = "all"

        # First call
        is_bot_edit_allowed(text="", title_page=page, botjob=botjob)
        first_cache_value = Bot_Cache[botjob][page]

        # Second call
        is_bot_edit_allowed(text="", title_page=page, botjob=botjob)
        second_cache_value = Bot_Cache[botjob][page]

        self.assertEqual(first_cache_value, second_cache_value)
