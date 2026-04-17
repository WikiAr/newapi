import pytest
from newapi.super.S_API.bot_api import NEW_API


class TestNewAPI:
    @pytest.fixture
    def api_client(self) -> NEW_API:
        return NEW_API("en", family="wikipedia")

    def test_find_pages_exists(self, api_client):
        """Test Find_pages_exists_or_not method"""
        result = api_client.Find_pages_exists_or_not(["Thyrotropin alfa", "Thiamine"], get_redirect=True)
        assert result is not None
        assert isinstance(result, (dict, list))

    def test_search_functionality(self, api_client):
        """Test Search method"""
        result = api_client.Search("yemen", srlimit="1000")
        assert result is not None
