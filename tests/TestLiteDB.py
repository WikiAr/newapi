import pytest
import tempfile
import os
from newapi.db_bot import LiteDB

class TestLiteDB:
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        db = LiteDB(path)
        yield db
        os.unlink(path)

    def test_create_table(self, temp_db):
        """Test table creation"""
        fields = {"name": str, "age": int}
        temp_db.create_table("test_table", fields)
        tables = temp_db.show_tables()
        # Add assertions based on expected behavior

    def test_insert_data(self, temp_db):
        """Test data insertion"""
        fields = {"name": str, "age": int}
        temp_db.create_table("test_table", fields)

        test_data = {"name": "Test User", "age": 25}
        temp_db.insert("test_table", test_data)

        result = temp_db.get_data("test_table")
        assert len(list(result)) > 0
