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
import sqlite_utils


def tracer(sql, params):
    print(f"SQL: {sql} - params: {params}")


class LiteDB:
    def __init__(self, db_path):
        self.db_path = db_path
        # self.db = sqlite_utils.Database(db_path, tracer=tracer)
        self.db = sqlite_utils.Database(db_path)

    def create_table(self, table_name, fields, pk="id", **kwargs):
        # Create table if it doesn't exist
        self.db[table_name].create(fields, pk=pk, if_not_exists=True, ignore=True, **kwargs)

    def query(self, sql):
        # return self.db.query(sql)
        return [r for r in self.db.execute(sql).fetchall()]

    def update(self, sql):
        self.db.executescript(sql)

    def show_tables(self):
        tabs = self.db.table_names()
        for tab in tabs:
            print(f"Table: {tab}")
            print(f"schema: {self.db[tab].schema}")

    def insert(self, table_name, data, check=True):
        if check:
            is_in = self.select(table_name, data)
            if is_in:
                print(f" Skipping {data} - already in database")
                return

        self.db[table_name].insert(data, ignore=True, pk="id")
        del data

    def insert_all(self, table_name, datalist, prnt=True):
        if prnt:
            print(f"inserting {len(datalist)} rows")
        self.db[table_name].insert_all(datalist, ignore=True, pk="id")
        del datalist

    def get_data(self, table_name):
        return self.db[table_name].rows

    def select(self, table_name, args):
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

    def select_or(self, table_name, args):
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
