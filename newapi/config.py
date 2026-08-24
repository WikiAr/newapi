"""
Centralized settings configuration for the project.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:
    load_dotenv("$HOME/.env")


@dataclass
class BotConfig:
    """
    Configuration for bot behavior.
    """

    ask: bool = False
    no_diff: bool = False
    show_diff: bool = False
    no_false_edit: bool = False
    workibrahem: bool = False
    force_edit: bool = False
    no_cookies: bool = False


@dataclass
class Settings:
    """
    Main settings container for all project configurations.

    This class aggregates all configuration dataclasses and provides
    global settings that apply across the project.
    """

    bot: BotConfig = field(default_factory=BotConfig)

    def __post_init__(self) -> None:
        """Process command-line arguments and environment variables."""
        self._process_argv()

    def _process_argv(self) -> None:
        """Process command-line arguments for configuration overrides."""
        for arg in sys.argv:
            arg_name, _, value = arg.removeprefix("-").partition(":")

            # Bot config
            if arg_name == "ask":
                self.bot.ask = True

            if arg_name == "nodiff":
                self.bot.no_diff = True

            if arg_name == "diff":
                self.bot.show_diff = True

            if arg_name == "nofa":
                self.bot.no_false_edit = True

            if arg_name == "workibrahem":
                self.bot.workibrahem = True

            if arg_name in ("botedit", "editbot"):
                self.bot.force_edit = True


main_settings = Settings()

__all__ = [
    "Settings",
    "main_settings",
]
