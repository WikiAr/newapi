# config/settings.py
"""
Configuration settings for the newapi package.

This module provides a centralized configuration system using dataclasses.
It replaces the previous pattern of checking sys.argv for flags.

Usage:
    from newapi.config import settings

    # Check flags
    if settings.flags.debug:
        print("Debug mode enabled")

    # Access configuration
    endpoint = settings.wikidata.endpoint

    # Enable flags programmatically
    settings.flags.ask = True

    # Initialize from sys.argv (call once at startup)
    settings.init_from_argv()
"""
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WikipediaConfig:
    """Configuration for Wikipedia API access."""
    ar_family: str = "wikipedia"
    ar_code: str = "ar"
    en_family: str = "wikipedia"
    en_code: str = "en"
    user_agent: str = ""


@dataclass
class WikidataConfig:
    """Configuration for Wikidata API access."""
    endpoint: str = "https://www.wikidata.org/w/api.php"
    sparql_endpoint: str = "https://query.wikidata.org/sparql"
    timeout: int = 10


@dataclass
class DatabaseConfig:
    """Configuration for database connections."""
    host: Optional[str] = None
    port: int = 3306
    use_sql: bool = True


@dataclass
class ArgFlags:
    """
    Flags that control behavior throughout the application.

    These flags replace the previous pattern of checking `sys.argv`.
    They can be set programmatically or initialized from command-line arguments.
    """
    # Logging/Debug flags
    debug: bool = False
    warning: bool = False
    test: bool = False
    test_print: bool = False

    # Output control flags
    noprint: bool = False
    nodiff: bool = False
    printurl: bool = False
    printdata: bool = False
    printresult: bool = False
    printpop: bool = False

    # User interaction flags
    ask: bool = False
    diff: bool = False

    # Edit control flags
    save: bool = False
    botedit: bool = False
    editbot: bool = False
    workibrahem: bool = False
    ibrahemsummary: bool = False
    nofa: bool = False

    # Login/Session flags
    nologin: bool = False
    nocookies: bool = False
    mwclient: bool = False
    nomwclient: bool = False

    # Error handling flags
    raise_errors: bool = field(default=False, metadata={"argv_name": "raise"})

    # Request debugging flags
    dopost: bool = False
    tat: bool = False

    def __post_init__(self):
        """Initialize flags from sys.argv if not already set."""
        pass

    def init_from_argv(self):
        """
        Initialize flags from sys.argv.

        Call this method once at application startup to parse command-line flags.
        """
        # Map of flag attribute names to their argv representations
        argv_mapping = {
            "debug": "debug",
            "warning": "warning",
            "test": "test",
            "test_print": "test_print",
            "noprint": "noprint",
            "nodiff": "nodiff",
            "printurl": "printurl",
            "printdata": "printdata",
            "printresult": "printresult",
            "printpop": "printpop",
            "ask": "ask",
            "diff": "diff",
            "save": "save",
            "botedit": "botedit",
            "editbot": "editbot",
            "workibrahem": "workibrahem",
            "ibrahemsummary": "ibrahemsummary",
            "nofa": "nofa",
            "nologin": "nologin",
            "nocookies": "nocookies",
            "mwclient": "mwclient",
            "nomwclient": "nomwclient",
            "raise_errors": "raise",
            "dopost": "dopost",
            "tat": "tat",
        }

        for attr_name, argv_name in argv_mapping.items():
            if argv_name in sys.argv:
                setattr(self, attr_name, True)


@dataclass
class Settings:
    """
    Main settings class that aggregates all configuration.

    Usage:
        from newapi.config import settings

        # Access nested config
        endpoint = settings.wikidata.endpoint

        # Check flags
        if settings.flags.debug:
            ...

        # Initialize from argv
        settings.init_from_argv()
    """
    wikipedia: WikipediaConfig = field(default_factory=WikipediaConfig)
    wikidata: WikidataConfig = field(default_factory=WikidataConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    flags: ArgFlags = field(default_factory=ArgFlags)

    # Global settings
    range_limit: int = 5
    log_level: str = "INFO"

    def init_from_argv(self):
        """
        Initialize settings from sys.argv.

        This parses command-line arguments and sets the appropriate flags.
        Call this once at application startup.
        """
        self.flags.init_from_argv()

        # Update log_level based on flags
        if self.flags.debug:
            self.log_level = "DEBUG"
        elif self.flags.warning:
            self.log_level = "WARNING"


# Global singleton instance
settings = Settings()

# Initialize from argv by default for backward compatibility
settings.init_from_argv()


__all__ = [
    'settings',
    'Settings',
    'WikipediaConfig',
    'WikidataConfig',
    'DatabaseConfig',
    'ArgFlags',
]
