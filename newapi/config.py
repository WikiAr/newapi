"""
Centralized settings configuration for the project.

This module provides dataclass-based configuration for all project settings,
including Wikipedia, Wikidata, and database configurations.

Example:
    >>> from src.config import settings
    >>> print(settings.wikipedia.ar_code)
    'ar'
    >>> print(settings.wikidata.endpoint)
    'https://www.wikidata.org/w/api.php'
"""

import os
import sys
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:
    load_dotenv("$HOME/.env")


@dataclass(frozen=True)
class Paths:
    cookies_dir: str


def _safe_int(value: str, default: int) -> int:
    """Safely convert string to int, returning default on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def default_user_agent() -> str:
    home = (os.getenv("HOME") or "").rstrip("/")
    tool = home.rsplit("/", 1)[-1] or "himo"
    return f"{tool} bot/1.0 (https://{tool}.toolforge.org/; tools.{tool}@toolforge.org)"


@dataclass
class WikidataConfig:
    """Configuration for Wikidata API connections.

    Attributes:
        endpoint: Wikidata API endpoint URL
        sparql_endpoint: SPARQL query endpoint URL
        timeout: Default timeout for Wikidata requests
        maxlag: Maximum lag for Wikidata API requests
        test_mode: Whether to use test.wikidata.org
    """

    endpoint: str = "https://www.wikidata.org/w/api.php"
    sparql_endpoint: str = "https://query.wikidata.org/sparql"
    timeout: int = 30
    maxlag: int = 5
    test_mode: bool = False


@dataclass
class ApiClientConfig:
    """Configuration for the API client.

    Attributes:
        max_retries: Maximum number of retries for API requests
        backoff_base: Base delay for exponential backoff
        maxlag_header: Header name for server maxlag retry-after
    """

    max_retries: int = 5
    backoff_base: int = 1
    maxlag_header: str = "Retry-After"


@dataclass
class DatabaseConfig:
    """Configuration for database connections.

    Attributes:
        host: Database host (optional, derived from wiki code if not set)
        port: Database port
        use_sql: Whether to use SQL database for queries
    """

    host: Optional[str] = None
    port: int = 3306
    use_sql: bool = True


@dataclass
class DebugConfig:
    """Configuration for debug and logging options.

    Attributes:
        print_url: Print API URLs for debugging
        do_post: Force POST requests for debugging
    """

    print_url: bool = False
    do_post: bool = False


@dataclass
class BotConfig:
    """Configuration for bot behavior.

    Attributes:
        ask: Ask for confirmation before making changes
        no_diff: Don't show diff when asking for confirmation
        show_diff: Force show diff when asking for confirmation
        no_print: Don't show diff when asking for confirmation
        no_fa: Dont check if the edit is false edit
        workibrahem:
        force_edit: Force bot edit (bypass nobots check)
        no_login: Disable login assertion
        no_cookies: Disable cookie storage
    """

    ask: bool = False
    no_diff: bool = False
    show_diff: bool = False
    no_print: bool = False
    no_fa: bool = False
    workibrahem: bool = False
    force_edit: bool = False
    no_login: bool = False
    no_cookies: bool = False


@dataclass
class QueryConfig:
    """Configuration for query parameters.

    Attributes:
        offset: Starting offset for queries
        depth: Depth limit for category traversal
        to_limit: Upper limit for results
        ns_no_10: Exclude namespace 10 from results
        ns_only_14: Only include namespace 14 in results
    """

    offset: int = 0
    depth: int = 0
    to_limit: int = 10000
    ns_no_10: bool = False
    ns_only_14: bool = False


@dataclass
class SiteConfig:
    """Configuration for alternative site settings.

    Attributes:
        custom_family: Custom wiki family (e.g., wikiquote, wikisource)
        custom_lang: Custom language code for en site
        secondary_lang: Secondary language to use (e.g., fr)
        secondary_family: Family for secondary language
        use_secondary: Whether to use secondary language site
    """

    custom_family: str = ""
    custom_lang: str = ""
    secondary_lang: str = ""
    secondary_family: str = ""
    use_secondary: bool = False


@dataclass
class WikiSiteInfo:
    """Configuration for a wiki site with family and code.

    Attributes:
        family: Wiki family (e.g., "wikipedia", "commons", "wikiquote")
        code: Language/site code (e.g., "en", "ar", "commons")
        use: Whether this site is enabled for use
    """

    family: str = "wikipedia"
    code: str = "en"
    use: bool = False

    def __getitem__(self, key):
        """Support dictionary-like access for backward compatibility."""
        if key == "family":
            return self.family
        elif key == "code":
            return self.code
        elif key == "use":
            return self.use
        elif key == 1:
            return self.use
        raise KeyError(key)

    def __contains__(self, key) -> bool:
        """Support 'in' operator for backward compatibility."""
        return key in ("family", "code", "use", 1)


@dataclass
class Settings:
    """Main settings container for all project configurations.

    This class aggregates all configuration dataclasses and provides
    global settings that apply across the project.

    Attributes:
        wikidata: Wikidata API configuration
        database: Database connection configuration
        debug_config: Debug and logging options
        bot: Bot behavior configuration
        category: Category processing configuration
        query: Query parameters configuration
        site: Alternative site settings
        range_limit: Maximum number of iterations for category processing
        debug: Enable debug mode
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """

    wikidata: WikidataConfig = field(default_factory=WikidataConfig)
    api_client: ApiClientConfig = field(default_factory=ApiClientConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    debug_config: DebugConfig = field(default_factory=DebugConfig)
    bot: BotConfig = field(default_factory=BotConfig)
    query: QueryConfig = field(default_factory=QueryConfig)
    site: SiteConfig = field(default_factory=SiteConfig)

    paths: Paths = Paths(
        cookies_dir=os.getenv("COOKIES_DIR") or os.path.join(os.getcwd()),
    )

    # Global settings
    range_limit: int = 5
    debug: bool = False
    log_level: str = "INFO"

    @staticmethod
    def is_production() -> bool:
        """Check if the application is running in production mode."""
        return os.getenv("APP_ENV", "").lower() == "production"

    def __post_init__(self) -> None:
        """Process command-line arguments and environment variables."""
        self._process_env_vars()
        self._process_argv()

    def _process_env_vars(self) -> None:
        """Load configuration from environment variables."""

        # Wikidata config
        if os.getenv("WIKIDATA_ENDPOINT"):
            self.wikidata.endpoint = os.environ["WIKIDATA_ENDPOINT"]
        if os.getenv("WIKIDATA_SPARQL_ENDPOINT"):
            self.wikidata.sparql_endpoint = os.environ["WIKIDATA_SPARQL_ENDPOINT"]
        if os.getenv("WIKIDATA_TIMEOUT"):
            self.wikidata.timeout = _safe_int(os.environ["WIKIDATA_TIMEOUT"], self.wikidata.timeout)
        if os.getenv("WIKIDATA_MAXLAG"):
            self.wikidata.maxlag = _safe_int(os.environ["WIKIDATA_MAXLAG"], self.wikidata.maxlag)

        # API Client config
        if os.getenv("API_CLIENT_MAX_RETRIES"):
            self.api_client.max_retries = _safe_int(os.environ["API_CLIENT_MAX_RETRIES"], self.api_client.max_retries)
        if os.getenv("API_CLIENT_BACKOFF_BASE"):
            self.api_client.backoff_base = _safe_int(
                os.environ["API_CLIENT_BACKOFF_BASE"], self.api_client.backoff_base
            )
        if os.getenv("API_CLIENT_MAXLAG_HEADER"):
            self.api_client.maxlag_header = os.environ["API_CLIENT_MAXLAG_HEADER"]

        # Database config
        if os.getenv("DATABASE_HOST"):
            self.database.host = os.environ["DATABASE_HOST"]
        if os.getenv("DATABASE_PORT"):
            self.database.port = _safe_int(os.environ["DATABASE_PORT"], self.database.port)
        if os.getenv("DATABASE_USE_SQL"):
            self.database.use_sql = os.environ["DATABASE_USE_SQL"].lower() in ("true", "1", "yes")

        # Global settings
        if os.getenv("RANGE_LIMIT"):
            self.range_limit = _safe_int(os.environ["RANGE_LIMIT"], self.range_limit)
        if os.getenv("DEBUG"):
            self.debug = os.environ["DEBUG"].lower() in ("true", "1", "yes")
        if os.getenv("LOG_LEVEL"):
            self.log_level = os.environ["LOG_LEVEL"]

    def _process_argv(self) -> None:
        """Process command-line arguments for configuration overrides."""
        for arg in sys.argv:
            arg_name, _, value = arg.partition(":")

            # Range limit
            if arg_name == "-range" and value:
                self.range_limit = _safe_int(value, self.range_limit)

            # Debug mode
            if arg_name in ("DEBUG", "-debug", "--debug"):
                self.debug = True

            # SQL usage
            if arg_name == "-nosql":
                self.database.use_sql = False
            if arg_name == "usesql":
                self.database.use_sql = True

            # Wikidata test environment
            if arg_name in ("testwikidata", "-testwikidata", "wikidata_test"):
                self.wikidata.endpoint = "https://test.wikidata.org/w/api.php"
                self.wikidata.test_mode = True

            # Maxlag configuration
            if arg_name == "maxlag2":
                self.wikidata.maxlag = 1

            # Debug config
            if arg_name == "printurl":
                self.debug_config.print_url = True
            if arg_name == "dopost":
                self.debug_config.do_post = True

            # Bot config
            if arg_name == "ask":
                self.bot.ask = True

            if arg_name == "nodiff":
                self.bot.no_diff = True
            if arg_name == "diff":
                self.bot.show_diff = True

            if arg_name == "noprint":
                self.bot.no_print = True

            if arg_name == "nofa":
                self.bot.no_fa = True

            if arg_name == "workibrahem":
                self.bot.workibrahem = True

            if arg_name in ("botedit", "editbot"):
                self.bot.force_edit = True
            if arg_name == "nologin":
                self.bot.no_login = True
            if arg_name == "nocookies":
                self.bot.no_cookies = True

            # Query config
            if arg_name in ("-offset", "-off") and value:
                self.query.offset = _safe_int(value, self.query.offset)
            if arg_name == "depth" and value:
                self.query.depth = _safe_int(value, self.query.depth)
            if arg_name in ("to", "-to") and value:
                self.query.to_limit = _safe_int(value, self.query.to_limit)

        # Calculate to_limit with offset if both are set
        if self.query.to_limit != 0:
            self.query.to_limit = self.query.to_limit + self.query.offset


# Global settings instance
settings = Settings()

__all__ = [
    "Settings",
    "settings",
]
