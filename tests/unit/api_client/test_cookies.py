"""
Unit tests for src/core/api_client/cookies.py module.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from newapi.api_client.cookies import (
    _COOKIE_MAX_AGE_DAYS,
    _delete_cookie_file,
    _delete_if_stale,
    get_cookie_path,
)
from newapi.api_client.exceptions import CookieError


class TestGetCookiePath:
    def test_returns_path_with_components(self, tmp_path) -> None:
        result = get_cookie_path(str(tmp_path), "wikipedia", "en", "MyBot")
        assert result.name == "wikipedia_en_mybot.mozilla"
        assert result.parent == tmp_path

    def test_normalizes_to_lowercase(self, tmp_path) -> None:
        result = get_cookie_path(str(tmp_path), "Wikipedia", "EN", "MY BOT")
        assert result.name == "wikipedia_en_my_bot.mozilla"

    def test_strips_bot_password_suffix(self, tmp_path) -> None:
        result = get_cookie_path(str(tmp_path), "wikipedia", "en", "MyBot@BotPassword")
        assert result.name == "wikipedia_en_mybot.mozilla"

    def test_creates_directory(self, tmp_path) -> None:
        new_dir = tmp_path / "new_cookies"
        get_cookie_path(str(new_dir), "wikipedia", "en", "bot")
        assert new_dir.exists()


class TestDeleteIfStale:
    def test_does_nothing_for_missing_file(self, tmp_path) -> None:
        path = tmp_path / "nonexistent.mozilla"
        _delete_if_stale(path)  # Should not raise

    def test_deletes_zero_byte_file(self, tmp_path) -> None:
        path = tmp_path / "empty.mozilla"
        path.touch()
        assert path.exists()
        _delete_if_stale(path)
        assert not path.exists()

    def test_does_not_delete_fresh_file(self, tmp_path) -> None:
        path = tmp_path / "fresh.mozilla"
        path.write_text("data")
        _delete_if_stale(path)
        assert path.exists()

    def test_deletes_old_file(self, tmp_path) -> None:
        path = tmp_path / "old.mozilla"
        path.write_text("data")
        old_time = datetime.now() - timedelta(days=_COOKIE_MAX_AGE_DAYS + 1)
        os.utime(path, (old_time.timestamp(), old_time.timestamp()))
        _delete_if_stale(path)
        assert not path.exists()


class TestDeleteCookieFile:
    def test_deletes_existing_file(self, tmp_path) -> None:
        path = tmp_path / "cookie.mozilla"
        path.touch()
        _delete_cookie_file(path)
        assert not path.exists()

    def test_missing_ok_for_nonexistent(self, tmp_path) -> None:
        path = tmp_path / "nonexistent.mozilla"
        _delete_cookie_file(path)  # Should not raise


class TestConstants:
    def test_cookie_max_age_days(self) -> None:
        assert _COOKIE_MAX_AGE_DAYS == 3
