import os
import tempfile

import pytest
from newapi.DB_bots.db_bot import LiteDB


class TestLiteDB:
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(prefix="test", suffix=".db")
        os.close(fd)
        sql_db = LiteDB(path)
        yield sql_db

        sql_db.db.conn.close()
        os.unlink(path)

    @pytest.mark.skip("TypeError: argument of type 'NoneType' is not iterable")
    def test_create_table(self, temp_db) -> None:
        """Test table creation"""
        fields = {"name": str, "age": int}
        temp_db.create_table("test_table", fields)
        tables = temp_db.show_tables()
        # Verify table exists by checking table names
        assert "test_table" in tables

    def test_create_table2(self, temp_db) -> None:
        """Test table creation"""
        fields = {"name": str, "age": int}
        temp_db.create_table("test_table2", fields)
        table_names = temp_db.db.table_names()
        assert "test_table2" in table_names

    def test_insert_data(self, temp_db) -> None:
        """Test data insertion"""
        fields = {"name": str, "age": int}
        temp_db.create_table("test_table", fields)

        test_data = {"name": "Test User", "age": 25}
        temp_db.insert("test_table", test_data)

        result = temp_db.get_data("test_table")
        assert len(list(result)) > 0
