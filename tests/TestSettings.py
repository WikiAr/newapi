"""Tests for the config/settings module."""
import pytest
import sys


class TestSettings:
    """Test the Settings class."""

    def test_settings_import(self):
        """Test that settings can be imported."""
        from newapi.config import settings
        assert settings is not None

    def test_settings_has_flags(self):
        """Test that settings has flags attribute."""
        from newapi.config import settings
        assert hasattr(settings, 'flags')

    def test_settings_has_wikipedia_config(self):
        """Test that settings has wikipedia config."""
        from newapi.config import settings
        assert hasattr(settings, 'wikipedia')
        assert settings.wikipedia.ar_family == 'wikipedia'
        assert settings.wikipedia.ar_code == 'ar'

    def test_settings_has_wikidata_config(self):
        """Test that settings has wikidata config."""
        from newapi.config import settings
        assert hasattr(settings, 'wikidata')
        assert 'wikidata.org' in settings.wikidata.endpoint

    def test_settings_has_database_config(self):
        """Test that settings has database config."""
        from newapi.config import settings
        assert hasattr(settings, 'database')
        assert settings.database.port == 3306


class TestArgFlags:
    """Test the ArgFlags class."""

    def test_flags_default_values(self):
        """Test that all flags default to False."""
        from newapi.config import ArgFlags
        flags = ArgFlags()
        # Don't call init_from_argv to test defaults
        assert flags.debug is False
        assert flags.ask is False
        assert flags.workibrahem is False

    def test_flags_can_be_set(self):
        """Test that flags can be set programmatically."""
        from newapi.config import ArgFlags
        flags = ArgFlags()
        flags.debug = True
        flags.ask = True
        assert flags.debug is True
        assert flags.ask is True

    def test_flags_init_from_argv(self):
        """Test that flags can be initialized from argv."""
        from newapi.config import ArgFlags
        # Save original argv
        original_argv = sys.argv.copy()

        try:
            # Set test argv
            sys.argv = ['test_script', 'debug', 'ask', 'workibrahem']
            flags = ArgFlags()
            flags.init_from_argv()
            assert flags.debug is True
            assert flags.ask is True
            assert flags.workibrahem is True
        finally:
            # Restore original argv
            sys.argv = original_argv

    def test_raise_errors_flag(self):
        """Test that raise flag maps to raise_errors attribute."""
        from newapi.config import ArgFlags
        original_argv = sys.argv.copy()

        try:
            sys.argv = ['test_script', 'raise']
            flags = ArgFlags()
            flags.init_from_argv()
            assert flags.raise_errors is True
        finally:
            sys.argv = original_argv


class TestWikipediaConfig:
    """Test the WikipediaConfig class."""

    def test_wikipedia_config_defaults(self):
        """Test WikipediaConfig default values."""
        from newapi.config import WikipediaConfig
        config = WikipediaConfig()
        assert config.ar_family == 'wikipedia'
        assert config.ar_code == 'ar'
        assert config.en_family == 'wikipedia'
        assert config.en_code == 'en'


class TestWikidataConfig:
    """Test the WikidataConfig class."""

    def test_wikidata_config_defaults(self):
        """Test WikidataConfig default values."""
        from newapi.config import WikidataConfig
        config = WikidataConfig()
        assert config.endpoint == 'https://www.wikidata.org/w/api.php'
        assert config.sparql_endpoint == 'https://query.wikidata.org/sparql'
        assert config.timeout == 10


class TestDatabaseConfig:
    """Test the DatabaseConfig class."""

    def test_database_config_defaults(self):
        """Test DatabaseConfig default values."""
        from newapi.config import DatabaseConfig
        config = DatabaseConfig()
        assert config.host is None
        assert config.port == 3306
        assert config.use_sql is True
