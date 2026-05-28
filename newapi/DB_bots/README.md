# DB_bots -- Database Abstraction Layer

## Project Overview

The `DB_bots` package provides database access abstractions for both SQLite and MySQL, designed for use by MediaWiki bots for local data storage and querying.

### Main Modules

| Module | Purpose |
|---|---|
| `db_bot.py` | SQLite abstraction with two implementations: `LiteDB` (legacy) and `LiteDbRepository` (repository pattern) |
| `pymysql_bot.py` | MySQL access via PyMySQL with a single `sql_connect_pymysql` function |

### Technologies & Dependencies

- **`sqlite_utils`** -- SQLite database toolkit (used by `LiteDB`)
- **`pymysql`** -- Pure Python MySQL client

---

## Architecture & Code Quality Review

### Code Organization

**Fair.** Two independent modules with no shared interface or base class. `db_bot.py` contains two unrelated implementations (`LiteDB` and `LiteDbRepository`) with significant API overlap.

### Design Patterns

- **Repository Pattern**: `LiteDbRepository` implements a clean repository interface with `get_by_id`, `find_by`, `insert`, `update`, `delete`.
- **Active Record-like**: `LiteDB` provides direct table operations with raw SQL access.

### Maintainability

**Low-Moderate.** Having two unrelated SQLite abstractions in the same file is confusing. `pymysql_bot.py` is a single function with no structure.

### Readability

**Fair.** Method names are descriptive but the dual-implementation approach in `db_bot.py` requires careful reading to understand which to use.

### Scalability Considerations

- **MySQL**: No connection pooling -- a new connection is created and destroyed per query.
- **SQLite**: `LiteDbRepository.count()` fetches all rows into memory to count them instead of using SQL `COUNT`.

---

## Strengths

- **Clean repository interface**: `LiteDbRepository` provides a well-structured CRUD API.
- **Parameterized queries**: `LiteDB.select` correctly uses `?` placeholders to prevent SQL injection.
- **Simple MySQL function**: `sql_connect_pymysql` is straightforward for one-off queries.
- **Type hints**: Both modules use type annotations on method signatures.

---

## Weaknesses

- **Two competing SQLite abstractions**: `LiteDB` and `LiteDbRepository` coexist with overlapping functionality and no shared interface.
- **Dead code**: `del data` / `del datalist` calls in `LiteDB` are no-ops. The `tracer` function is defined but commented out.
- **Silent error swallowing**: `LiteDbRepository` catches bare `Exception` and returns `None`/`False`. `pymysql_bot` returns `[]` on all errors.
- **No connection pooling**: MySQL connections are created fresh for every query call.
- **Inefficient counting**: `LiteDbRepository.count()` with criteria fetches all rows just to `len()` them.

---

## Critical Issues

### 1. SQL Injection in `LiteDB.query()` and `LiteDB.update()` (HIGH)

```python
# db_bot.py
def query(self, sql: str) -> List[tuple]:
    return self.db.query(sql)  # Raw SQL, no parameterization

def update(self, sql: str) -> None:
    self.db.executescript(sql)  # Raw SQL, no parameterization
```

These methods accept raw SQL strings with no sanitization. Any caller passing user-controlled input is fully exposed to SQL injection.

### 2. Mutable Default Arguments in `sql_connect_pymysql()` (HIGH)

```python
# pymysql_bot.py
def sql_connect_pymysql(query, return_dict=False, values=None,
                        main_args={},  # <-- Mutable default!
                        credentials={},  # <-- Mutable default!
                        ...):
```

Modifications to these dicts persist across calls, causing subtle state corruption.

### 3. Silent Error Swallowing (MEDIUM)

`pymysql_bot.py` returns `[]` on all exceptions. `LiteDbRepository` returns `None`/`False`. Callers cannot distinguish "no results" from "database error."

### 4. `LiteDB.insert` Hardcodes Primary Key (LOW)

```python
# db_bot.py
def insert(self, table_name, data, check=True):
    # ... hardcodes pk="id" despite create_table accepting custom pk
```

Tables with non-`id` primary keys will fail.

---

## Areas That Need Attention

- **Unify SQLite abstractions**: Choose one API (`LiteDbRepository` is cleaner) and deprecate the other.
- **Remove dead code**: `del data`, `del datalist`, `tracer` function.
- **Add connection pooling** for MySQL.
- **Use SQL `COUNT`** instead of fetching all rows for counting.
- **Add error differentiation**: Raise or return typed errors instead of silent defaults.
- **Fix mutable default arguments** in `sql_connect_pymysql`.

---

## Improvement Plan

### Quick Wins
1. Fix mutable default arguments in `sql_connect_pymysql` (`main_args=None`, `credentials=None`).
2. Remove dead `del` statements and `tracer` function.
3. Fix `LiteDbRepository.count()` to use SQL `COUNT`.

### Medium-Term Improvements
1. Deprecate `LiteDB` in favor of `LiteDbRepository`.
2. Add connection pooling for MySQL (e.g., `DBUtils` or `SQLAlchemy` pool).
3. Implement proper error handling with typed exceptions.
4. Add `__all__` to `__init__.py`.

### Long-Term Refactoring
1. Define a shared abstract interface for both SQLite and MySQL.
2. Add transaction management for write operations.
3. Add retry logic for transient database errors.
4. Add comprehensive unit tests.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **5/10** |
| **Production Readiness** | Low-Moderate -- SQL injection and mutable defaults are production risks |
| **Technical Debt** | High -- dual abstractions, dead code, silent errors |
| **Risk Assessment** | High -- SQL injection vulnerability and mutable default arguments |
| **Maintainability** | 4/10 -- confusing dual APIs, no tests, silent failures |
