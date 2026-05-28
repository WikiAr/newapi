# newapi -- Wikimedia API Python Library

## Project Overview

`newapi` is a Python library for interacting with the MediaWiki API, designed for automated bot operations on Wikimedia projects. It provides authenticated API access, page manipulation, category traversal, database storage, and Wikidata SPARQL queries.

### Main Modules

| Module | Purpose |
|---|---|
| `__init__.py` | Package entry point -- re-exports key symbols (`AllAPIS`, `WikiLoginClient`, etc.) |
| `all_apis.py` | Re-exports `AllAPIS` from `client_wiki.all_apis` |
| `config.py` | Centralized settings via dataclasses, loaded from env vars and CLI args |
| `logging_config.py` | Colored logging configuration for console and file output |
| `page.py` | Deprecated convenience wrappers (`MainPage`, `CatDepth`, `NewApi`) |
| `pformat.py` | Wikitext template reformatting utility |
| `api_client/` | MediaWiki API client with retry, authentication, and cookie persistence |
| `client_wiki/` | High-level wiki bot client (page operations, categories, bot edit checks) |
| `core/` | Exception hierarchy for MediaWiki API errors |
| `DB_bots/` | Database abstraction (SQLite and MySQL) |
| `super/` | `NewApi` class -- high-level bot API with 30+ methods |
| `utils/` | Shared utilities (function timer decorator) |

### Architecture Diagram

```
newapi/
  __init__.py          # Public API surface
  config.py            # Settings singleton
  logging_config.py    # Logging setup
  page.py              # Deprecated convenience API
  all_apis.py          # Re-export
  pformat.py           # Wikitext formatting

  api_client/          # Layer 1: Transport & Auth
    client.py          #   WikiLoginClient (retry, CSRF, cookies)
    cookies.py         #   Cookie file management
    exceptions.py      #   Client exceptions

  client_wiki/         # Layer 2: Wiki Operations
    all_apis.py        #   AllAPIS facade
    pages/             #   MainPage class
    categories/        #   CategoryDepth traversal
    api_utils/         #   Bot edit checks, error handling, parsing

  super/               # Layer 3: High-Level API
    S_API/bot_api.py   #   NewApi class (search, query, edit, upload)

  core/                # Exception hierarchy
  DB_bots/             # Database access (SQLite, MySQL)
  utils/               # Shared utilities
```

### Technologies & Dependencies

| Package | Version | Purpose |
|---|---|---|
| `mwclient` | -- | MediaWiki API client |
| `requests` | -- | HTTP transport |
| `wikitextparser` | -- | Wikitext parsing |
| `SPARQLWrapper` | -- | Wikidata SPARQL queries |
| `pywikibot` | -- | Diff display |
| `tqdm` | -- | Progress bars |
| `sqlite_utils` | -- | SQLite abstraction |
| `pymysql` | -- | MySQL client |
| `colorlog` | -- | Colored logging |
| `python-dotenv` | -- | Environment file loading |

### Configuration

Settings are loaded from (in order of precedence):
1. Command-line arguments (e.g., `depth:3`, `ask`, `no_cookies`)
2. Environment variables (e.g., `WIKI_LANG`, `WIKI_FAMILY`, `WIKI_USERNAME`)
3. `.env` file
4. Dataclass defaults

The `settings` singleton is instantiated at import time in `config.py`.

---

## Architecture & Code Quality Review

### Code Organization

**Good at the top level.** The layered architecture (transport -> wiki operations -> high-level API) is clear. Sub-packages are logically grouped.

**Weak at the detail level.** Several modules are oversized (`bot_api.py` at 1300+ lines, `super_page.py` at 1000+ lines), naming is inconsistent, and `__init__.py` files are mostly empty.

### Design Patterns

| Pattern | Usage |
|---|---|
| Singleton | `settings` global in `config.py` |
| Facade | `AllAPIS`, `page.py` convenience functions |
| Template Method | `RequestsHandler` retry loop with abstract hooks |
| Mixin | `HandleErrors` and `AskBot` composed into `MainPage` and `NewApi` |
| Repository | `LiteDbRepository` in `db_bot.py` |
| Data Transfer Object | Dataclasses in `config.py` and `pages/data.py` |
| Decorator | `function_timer` in `utils/` |
| Factory Method | `parse_api_error` in `core/exceptions.py` |

### Maintainability

**Moderate.** The top-level structure is clear, but individual modules suffer from god classes, inconsistent naming, missing docs, and mixed languages in comments.

### Readability

**Mixed.** Some modules are clean (`exceptions.py`, `functions_timer.py`), while others mix Arabic/English comments and lack docstrings.

### Scalability Considerations

- No connection pooling for MySQL
- No proactive rate limiting (reactive only)
- Category traversal can be memory-intensive for large trees
- `LiteDbRepository.count()` fetches all rows into memory

---

## Strengths

- **Comprehensive API coverage**: 60+ methods across all modules covering page CRUD, search, categories, uploads, and more.
- **Robust authentication**: Cookie persistence, automatic retry on CSRF/maxlag/rate-limit errors, session recovery.
- **Bot safety**: Multi-layered edit permission checking (time-based + template-based).
- **Clean exception hierarchy**: Well-structured `core/exceptions.py` with factory method.
- **Configuration flexibility**: Settings from env vars, CLI args, and `.env` files.
- **Repository pattern**: `LiteDbRepository` provides a clean database interface.

---

## Weaknesses

- **God classes**: `NewApi` (1300+ lines) and `MainPage` (1000+ lines) violate single responsibility.
- **Inconsistent naming**: Mix of PascalCase, snake_case, and camelCase across the codebase.
- **Unused exception hierarchy**: `core/exceptions.py` is defined but the codebase returns mixed types instead of raising exceptions.
- **Global mutable state**: Module-level caches (`Bot_Cache`, `_save_or_ask`) never cleared.
- **Empty `__init__.py` files**: No re-exports from sub-packages.
- **Mixed language comments**: Arabic and English comments throughout.
- **No tests for most modules**: 20+ source modules have zero test coverage.

---

## Critical Issues

### 1. SQL Injection in `LiteDB.query()` and `LiteDB.update()` (HIGH)

Raw SQL strings accepted with no parameterization. Any user-controlled input is fully exposed.

### 2. Infinite Loop/Recursion on Rate Limiting (HIGH)

- `api_client/client.py`: `ratelimited` handler never increments `attempt` -- infinite loop.
- `super/S_API/bot_api.py`: `move()` recurses on `ratelimited` with no limit -- stack overflow.

### 3. Multiple Crash Bugs in `bot_api.py` (HIGH)

- `PrefixSearch`: deletes wrong dict key (`apnamespace` instead of `psnamespace`) -- `KeyError`.
- `querypage_list`: calls `.isdigit()` on `None` -- `AttributeError`.
- `upload_by_file`: no None check on `data` before `.get()` -- `AttributeError`.

### 4. Mutable Default Arguments in `pymysql_bot.py` (HIGH)

`main_args={}` and `credentials={}` are shared across calls, causing state corruption.

### 5. No HTTP Timeout (MEDIUM)

`api_client/client.py` makes HTTP requests without timeout, risking indefinite hangs.

### 6. Settings Mutation at Import Time (MEDIUM)

`config.py`'s `__post_init__` permanently mutates `query.to_limit` by adding `offset`, destroying the original value.

---

## Areas That Need Attention

- **Missing `core/__init__.py`**: Inconsistent with other packages.
- **Missing `py.typed` marker**: No type-checking support declaration.
- **No CI/CD configuration visible**: No GitHub Actions or similar.
- **Outdated `pyproject.toml` references**: `src_paths = "ArWikiCats"` references a non-existent project.
- **Deprecation warnings not emitted**: `page.py` defines deprecation strings but never applies them.
- **`load_dotenv("$HOME/.env")`**: `$HOME` is not expanded, so this fallback silently fails.

---

## Improvement Plan

### Quick Wins
1. Fix the three crash bugs in `bot_api.py` (KeyError, AttributeError x2).
2. Fix the infinite loop in `api_client/client.py` ratelimited handler.
3. Fix mutable default arguments in `pymysql_bot.py`.
4. Add HTTP timeout to `_execute_request`.
5. Add `core/__init__.py`.

### Medium-Term Improvements
1. Deprecate `LiteDB` in favor of `LiteDbRepository`.
2. Split `NewApi` and `MainPage` into focused modules.
3. Standardize naming to `snake_case` throughout.
4. Add `__all__` and re-exports to all `__init__.py` files.
5. Adopt the `core/exceptions.py` hierarchy across the codebase.
6. Add unit tests for untested modules.

### Long-Term Refactoring
1. Unify the two exception hierarchies (`core/` and `api_client/`).
2. Implement connection pooling for MySQL.
3. Add proactive rate limiting.
4. Add comprehensive integration tests.
5. Add type stubs and `py.typed` marker.
6. Extract hardcoded values (`BOT_USERNAME`, `mdwiki.org`) to configuration.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **5.5/10** |
| **Production Readiness** | Low-Moderate -- multiple crash bugs and SQL injection risks |
| **Technical Debt** | High -- god classes, inconsistent naming, unused abstractions, no tests |
| **Risk Assessment** | High -- SQL injection, infinite loops, crash bugs in common paths |
| **Maintainability** | 5/10 -- clear top-level structure but messy internals |
