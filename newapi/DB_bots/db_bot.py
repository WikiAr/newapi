"""

Usage:
# from .db_bot import LiteDB
# db = LiteDB(db_path)
# db.create_table(table_name, fields, pk="id", **kwargs)
# db.show_tables(self)
# db.insert(table_name, data, check=True)
# db.get_data(table_name)
# db.select(table_name, args)

"""

# ---
from typing import Any, Dict, Iterator, List, Optional

import sqlite_utils


def tracer(sql, params):
    print(f"SQL: {sql} - params: {params}")


class LiteDB:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        # self.db = sqlite_utils.Database(db_path, tracer=tracer)
        self.db = sqlite_utils.Database(db_path)

    def create_table(self, table_name: str, fields: Dict[str, Any], pk: str = "id", **kwargs) -> None:
        # Create table if it doesn't exist
        self.db[table_name].create(fields, pk=pk, if_not_exists=True, ignore=True, **kwargs)

    def query(self, sql: str) -> List[tuple]:
        # return self.db.query(sql)
        return [r for r in self.db.execute(sql).fetchall()]

    def update(self, sql: str) -> None:
        self.db.executescript(sql)

    def show_tables(self) -> None:
        tabs = self.db.table_names()
        for tab in tabs:
            print(f"Table: {tab}")
            print(f"schema: {self.db[tab].schema}")

    def insert(self, table_name: str, data: Dict[str, Any], check: bool = True) -> None:
        if check:
            is_in = self.select(table_name, data)
            if is_in:
                print(f" Skipping {data} - already in database")
                return

        self.db[table_name].insert(data, ignore=True, pk="id")
        del data

    def insert_all(self, table_name: str, datalist: List[Dict[str, Any]], prnt: bool = True) -> None:
        if prnt:
            print(f"inserting {len(datalist)} rows")
        self.db[table_name].insert_all(datalist, ignore=True, pk="id")
        del datalist

    def get_data(self, table_name: str) -> Iterator[Dict[str, Any]]:
        return self.db[table_name].rows

    def select(self, table_name: str, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        # ---
        where_conditions = []
        params = []
        # ---
        for k, v in args.items():
            where_conditions.append(f"{k} = ?")
            params.append(v)
        # ---
        where = " and ".join(where_conditions)
        # where = " and ".join([f"{k} = '{v}'" for k, v in args.items()])
        lista = []
        # ---
        # for row in self.db[table_name].rows_where(where):
        for row in self.db[table_name].rows_where(where, params):
            lista.append(row)
        # ---
        return lista

    def select_or(self, table_name: str, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        # ---
        where_conditions = []
        params = []
        # ---
        for k, v in args.items():
            where_conditions.append(f"{k} = ?")
            params.append(v)
        # ---
        where = " or ".join(where_conditions)
        lista = []
        # ---
        for row in self.db[table_name].rows_where(where, params):
            lista.append(row)
        # ---
        return lista


class LiteDbRepository:
    """
    Repository pattern wrapper for LiteDB.

    Provides a cleaner interface for database operations
    following the repository pattern.

    Attributes:
        db_path: Path to the SQLite database.
    """

    def __init__(self, db_path: str) -> None:
        """
        Initialize the repository.

        Args:
            db_path: Path to the SQLite database file.
        """
        self._db = sqlite_utils.Database(db_path)

    def get_by_id(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        """
        Get a record by its ID.

        Args:
            table: The table name.
            id: The record ID.

        Returns:
            The record dictionary, or None if not found.
        """
        try:
            return self._db[table].get(id)
        except Exception:
            return None

    def get_all(self, table: str) -> List[Dict[str, Any]]:
        """
        Get all records from a table.

        Args:
            table: The table name.

        Returns:
            List of all records.
        """
        return list(self._db[table].rows)

    def find_by(self, table: str, **criteria) -> List[Dict[str, Any]]:
        """
        Find records matching criteria.

        Args:
            table: The table name.
            **criteria: Field=value pairs to match.

        Returns:
            List of matching records.
        """
        if not criteria:
            return self.get_all(table)

        where_parts = []
        params = []
        for key, value in criteria.items():
            where_parts.append(f"{key} = ?")
            params.append(value)

        where_clause = " AND ".join(where_parts)
        return list(self._db[table].rows_where(where_clause, params))

    def find_one(self, table: str, **criteria) -> Optional[Dict[str, Any]]:
        """
        Find a single record matching criteria.

        Args:
            table: The table name.
            **criteria: Field=value pairs to match.

        Returns:
            The first matching record, or None.
        """
        results = self.find_by(table, **criteria)
        return results[0] if results else None

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insert a new record.

        Args:
            table: The table name.
            data: The record data.

        Returns:
            The ID of the inserted record.
        """
        return self._db[table].insert(data).last_rowid

    def insert_many(self, table: str, records: List[Dict[str, Any]]) -> None:
        """
        Insert multiple records.

        Args:
            table: The table name.
            records: List of record data dictionaries.
        """
        self._db[table].insert_all(records)

    def update(self, table: str, id: int, data: Dict[str, Any]) -> bool:
        """
        Update a record by ID.

        Args:
            table: The table name.
            id: The record ID.
            data: The updated data.

        Returns:
            True if the update was successful.
        """
        try:
            self._db[table].update(id, data)
            return True
        except Exception:
            return False

    def delete(self, table: str, id: int) -> bool:
        """
        Delete a record by ID.

        Args:
            table: The table name.
            id: The record ID.

        Returns:
            True if the delete was successful.
        """
        try:
            self._db[table].delete(id)
            return True
        except Exception:
            return False

    def count(self, table: str, **criteria) -> int:
        """
        Count records, optionally filtered by criteria.

        Args:
            table: The table name.
            **criteria: Optional filter criteria.

        Returns:
            The count of matching records.
        """
        if not criteria:
            return self._db[table].count

        return len(self.find_by(table, **criteria))

    def table_exists(self, table: str) -> bool:
        """
        Check if a table exists.

        Args:
            table: The table name.

        Returns:
            True if the table exists.
        """
        return table in self._db.table_names()

    def create_table(self, table: str, schema: Dict[str, type], pk: str = "id") -> None:
        """
        Create a table if it doesn't exist.

        Args:
            table: The table name.
            schema: Dictionary mapping column names to types.
            pk: Primary key column name.
        """
        self._db[table].create(schema, pk=pk, if_not_exists=True)
