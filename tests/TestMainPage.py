import pytest
from newapi.page import MainPage

class TestMainPage:
    @pytest.fixture
    def test_page(self):
        return MainPage("User:Mr. Ibrahem/sandbox", 'en')

    @pytest.fixture
    def arabic_page(self):
        return MainPage("وب:ملعب", "ar")

    def test_page_exists(self, test_page):
        """Test page existence check"""
        exists = test_page.exists()
        assert isinstance(exists, bool)

    def test_can_edit_permission(self, arabic_page):
        """Test edit permission check"""
        can_edit = arabic_page.can_edit()
        assert isinstance(can_edit, bool)

    def test_get_text(self, arabic_page):
        """Test text retrieval"""
        text = arabic_page.get_text()
        assert isinstance(text, str)
