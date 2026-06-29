# PROJECT AUDIT REPORT

**Project:** newapi_bot -- Wikimedia API Python Library
**Date:** 2026-05-27
**Scope:** Full codebase audit of `newapi/` package and `tests/` suite
**Methodology:** Static analysis of all Python source files across 13 modules

---

## Executive Summary

### Purpose

`newapi_bot` is a Python library for automated bot operations on MediaWiki projects (Wikipedia, Wikidata). It provides authenticated API access, page reading/editing/creation, recursive category traversal, Wikidata SPARQL queries, and local database storage via SQLite and MySQL.

### Technologies

| Layer | Technologies |
|---|---|
| Language | Python 3.13 |
| HTTP/API | `mwclient`, `requests` |
| Parsing | `wikitextparser`, `SPARQLWrapper` |
| Database | `sqlite_utils` (SQLite), `pymysql` (MySQL) |
| UI/Progress | `tqdm`, `colorlog`, `pywikibot` |
| Config | `python-dotenv`, `dataclasses` |
| Testing | `pytest`, `pytest-socket`, `unittest.mock` |
| Linting | `ruff`, `black`, `isort`, `mypy`, `flynt` |

### Architecture Overview

The system follows a three-layer architecture:

```
Layer 3: super/S_API/bot_api.py    -- NewApi (30+ high-level operations)
Layer 2: client_wiki/               -- MainPage, CategoryDepth, bot edit checks
Layer 1: api_client/                -- WikiLoginClient (auth, retry, cookies)
         DB_bots/                   -- SQLite and MySQL access
         core/                      -- Exception hierarchy
         config.py                  -- Settings singleton
```

The `AllAPIS` facade in `client_wiki/all_apis.py` serves as the primary entry point, composing page, category, and API access behind a single authenticated constructor.

---

## Project Health Assessment

### Overall Code Quality: 5.5/10

The codebase is functional and covers a wide surface area (60+ methods across all modules), but suffers from god classes, inconsistent naming, missing documentation, and several crash bugs in common code paths.

### Maintainability: 4.5/10

| Factor | Assessment |
|---|---|
| Module structure | Good -- logical sub-packages at the top level |
| File sizes | Poor -- `bot_api.py` (1300+ lines), `super_page.py` (1000+ lines), `client.py` (850+ lines) |
| Naming consistency | Poor -- mix of PascalCase, snake_case, camelCase |
| Documentation | Poor -- most methods lack docstrings |
| Type annotations | Partial -- present on some methods, absent on many |
| Dead code | Moderate -- unused exceptions, commented-out code, no-op `del` statements |

### Scalability: 5/10

- No MySQL connection pooling (new connection per query)
- No proactive rate limiting (reactive only)
- `LiteDbRepository.count()` fetches all rows into memory
- Category traversal can be memory-intensive for large trees
- Single-threaded HTTP client with no async support

### Security Posture: 4/10

| Vulnerability | Severity | Location |
|---|---|---|
| SQL injection via raw SQL | HIGH | `db_bot.py` -- `query()`, `update()` |
| SPARQL injection risk | MEDIUM | `wd_sparql.py` -- `get_query_data()` |
| Cookie directory 0o770 permissions | MEDIUM | `cookies.py` -- group-readable/writable |
| Cookie files inherit umask | LOW | `cookies.py` -- potentially world-readable |
| Plaintext password in memory | LOW | `client.py` -- `self._password` |
| Silent exception swallowing | MEDIUM | `pymysql_bot.py`, `client_request_safe()` |

### Production Readiness: NOT READY

The codebase has **9 crash-level bugs** in common code paths, **1 SQL injection vulnerability**, **no HTTP timeouts**, and **20+ untested modules**. It is not suitable for production deployment in its current state.

---

## Cross-Project Analysis

### Shared Architectural Patterns

| Pattern | Occurrences | Assessment |
|---|---|---|
| Facade | `AllAPIS`, `page.py`, `NewApi` | Good -- consistent entry-point design |
| Mixin/MI | `HandleErrors` + `AskBot` in `MainPage` and `NewApi` | Good -- reusable composition |
| Singleton | `settings` global in `config.py` | Acceptable but makes testing hard |
| Template Method | `RequestsHandler` retry loop | Good -- clean hook-based design |
| Repository | `LiteDbRepository` | Good -- clean interface |
| Decorator | `function_timer` | Good -- correct implementation |
| DTO | Dataclasses in `config.py`, `data.py` | Good -- structured data |

### Repeated Weaknesses (Cross-Cutting)

| Weakness | Modules Affected |
|---|---|
| **Mutable default arguments** | `pymysql_bot.py`, `txtlib.py` |
| **Shadowed builtin `max`** | `client.py`, `bot_api.py`, `super_page.py` (6+ occurrences) |
| **Silent error swallowing** | `pymysql_bot.py`, `client_request_safe()`, `LiteDbRepository` |
| **Global mutable caches** | `Bot_Cache`, `_save_or_ask`, `_created_cache` |
| **Missing type annotations** | 30+ public methods across all modules |
| **Inconsistent naming** | Every module mixes conventions |
| **No `__init__.py` re-exports** | All sub-packages have empty init files |

### Common Technical Debt

1. **God classes**: `NewApi` (1300 lines), `MainPage` (1000 lines), `WikiLoginClient` (850 lines)
2. **Code duplication**: `client_request_retry` is a copy-paste of `_client_request`
3. **Unused abstractions**: `core/exceptions.py` hierarchy defined but never used; `MaxRetriesExceededError` and `CookieError` defined but never raised
4. **Hardcoded values**: `BOT_USERNAME = "Mr.Ibrahembot"`, `mdwiki.org` special case, Arabic `"قالب:"` prefix
5. **Commented-out code**: Scattered across `db_bot.py`, `bot_api.py`, `page.py`
6. **Outdated config**: `pyproject.toml` references `src_paths = "ArWikiCats"` (non-existent project)

### Dependency Issues

- **No pinned versions**: `requirements.in` exists but no `requirements.txt` with locked versions
- **Heavy transitive dependency**: `pywikibot` pulled in just for `showDiff()` -- could be replaced with a lightweight diff library
- **`tqdm` coupled to logic**: Progress bars hardcoded in library code with no way to suppress

### Integration Concerns

- **Two parallel exception hierarchies**: `core/exceptions.py` and `api_client/exceptions.py` are unrelated
- **Two SQLite abstractions**: `LiteDB` and `LiteDbRepository` coexist with overlapping APIs
- **Settings side effects**: `config.py` `__post_init__` parses `sys.argv` and env vars at import time, making unit testing difficult
- **Mixed language comments**: Arabic and English throughout, hindering collaboration

---

## Critical Findings

### High-Risk Issues (9 total)

| # | Issue | Module | Impact |
|---|---|---|---|
| 1 | **SQL injection** -- `query()` and `update()` accept raw SQL | `db_bot.py` | Data breach, data destruction |
| 2 | **Infinite loop** -- `ratelimited` handler never increments `attempt` | `client.py:236` | Process hang, resource exhaustion |
| 3 | **Infinite recursion** -- `move()` recurses on `ratelimited` with no limit | `bot_api.py:1180` | Stack overflow, process crash |
| 4 | **KeyError** -- `PrefixSearch` deletes wrong dict key | `bot_api.py:299` | Crash on common code path |
| 5 | **AttributeError** -- `querypage_list` calls `.isdigit()` on `None` | `bot_api.py:697` | Crash on common code path |
| 6 | **AttributeError** -- `upload_by_file` no None check on `data` | `bot_api.py:1271` | Crash on upload failure |
| 7 | **Mutable default** -- `main_args={}`, `credentials={}` | `pymysql_bot.py:15` | State corruption across calls |
| 8 | **Mutable default** -- `templates=[]` | `txtlib.py:52` | Corrupted template parsing |
| 9 | **Bare `raise`** -- no exception context | `super_page.py:1024` | Unhandled RuntimeError |

### Security Vulnerabilities (3 total)

| # | Vulnerability | Severity | Module |
|---|---|---|---|
| 1 | SQL injection via raw SQL strings | HIGH | `db_bot.py` |
| 2 | SPARQL injection (no query sanitization) | MEDIUM | `wd_sparql.py` |
| 3 | Cookie directory 0o770 + file umask | MEDIUM | `cookies.py` |

### Performance Bottlenecks (4 total)

| # | Bottleneck | Module |
|---|---|---|
| 1 | No MySQL connection pooling (new connection per query) | `pymysql_bot.py` |
| 2 | `count()` fetches all rows into memory | `db_bot.py` |
| 3 | No HTTP timeout (indefinite hangs possible) | `client.py` |
| 4 | `copy.deepcopy` per iteration in `post_continue` | `client.py` |

### Stability Concerns (5 total)

| # | Concern | Module |
|---|---|---|
| 1 | `_ensure_logged_in` does not actually log in | `client.py` |
| 2 | `client_request_safe` swallows all exceptions including `LoginError` | `client.py` |
| 3 | `post_continue` returns partial results silently on continuation failure | `client.py` |
| 4 | `settings.query.to_limit` permanently mutated at import time | `config.py` |
| 5 | `load_dotenv("$HOME/.env")` -- `$HOME` not expanded, silently fails | `config.py` |

### Missing Infrastructure

| Item | Status |
|---|---|
| CI/CD pipeline | Not present |
| `core/__init__.py` | Missing |
| `py.typed` marker | Missing |
| Dependency pinning | Incomplete |
| Code coverage reporting | Not configured |
| Linting in CI | Not configured |
| Integration test environment | Not present |

---

## Strengths

### Strong Engineering Decisions

1. **Layered architecture**: Clear separation between transport (`api_client`), operations (`client_wiki`), and high-level API (`super`). The dependency direction is consistent.

2. **Template Method pattern in `RequestsHandler`**: The retry loop with abstract hooks (`_session`, `_refresh_csrf_token`, `_on_assertnameduserfailed`) is a clean, extensible design for handling transient API errors.

3. **Bot edit safety system**: Multi-layered permission checking (time-based + template-based) is a thoughtful approach to preventing accidental edits to protected pages.

4. **Cookie persistence with staleness invalidation**: Sessions survive process restarts via `LWPCookieJar` with automatic 3-day expiry -- practical for long-running bots.

5. **Write-action safety**: Automatic injection of `bot=1` and `assertuser` parameters for mutating requests prevents accidental non-bot edits.

### Reusable Components

- `HandleErrors` and `AskBot` mixins are cleanly composable across `MainPage` and `NewApi`
- `function_timer` decorator is correct and minimal
- `LiteDbRepository` provides a clean, typed CRUD interface
- Dataclasses in `config.py` and `data.py` provide structured, self-documenting data shapes

### Well-Structured Modules

- `api_client/` -- cleanest module with clear layering and good test coverage
- `core/exceptions.py` -- well-structured exception hierarchy with factory method
- `bot_edit/` -- clear separation of time-based and template-based strategies

### Good Development Practices

- `ruff`, `black`, `isort`, `mypy`, `flynt` configured in `pyproject.toml`
- `pytest-socket` prevents accidental network calls in tests
- `@pytest.mark.parametrize` used effectively in bot_edit tests
- `lru_cache` used appropriately for memoization

---

## Improvement Roadmap

### Immediate Fixes (Week 1)

These are crash bugs and security vulnerabilities that must be fixed before any deployment.

| # | Fix | File | Change |
|---|---|---|---|
| 1 | Fix SQL injection | `db_bot.py` | Remove raw `query()`/`update()` or add parameterization |
| 2 | Fix infinite loop | `client.py:236` | Add `attempt += 1` before `continue` in ratelimited handler |
| 3 | Fix infinite recursion | `bot_api.py:1180` | Add retry counter and max limit to `move()` |
| 4 | Fix KeyError | `bot_api.py:299` | Change `del params["apnamespace"]` to `del params["psnamespace"]` |
| 5 | Fix AttributeError | `bot_api.py:697` | Add `if qplimit and qplimit.isdigit()` guard |
| 6 | Fix AttributeError | `bot_api.py:1271` | Add `if not data: return {}` guard |
| 7 | Fix mutable defaults | `pymysql_bot.py:15` | Change to `main_args=None, credentials=None` with `if None` guards |
| 8 | Fix mutable default | `txtlib.py:52` | Change `templates=[]` to `templates=None` |
| 9 | Fix bare `raise` | `super_page.py:1024` | Replace with `raise RuntimeError("...")` or proper re-raise |
| 10 | Add HTTP timeout | `client.py` | Add `timeout=(10, 30)` to `_execute_request` |

### Short-Term Improvements (Weeks 2-4)

| # | Improvement | Impact |
|---|---|---|
| 1 | Fix `_ensure_logged_in` to actually trigger login | Prevents unauthenticated sessions |
| 2 | Add `core/__init__.py` with re-exports | Package consistency |
| 3 | Fix `get_username()` to read from `login_bot` | Fixes always-empty username |
| 4 | Use context manager for file handles in `upload_by_file` | Prevents resource leaks |
| 5 | Fix `settings.query.to_limit` mutation | Preserves original config value |
| 6 | Fix `load_dotenv` path expansion | Enables `.env` fallback |
| 7 | Remove tautological tests, fix empty test files | Accurate coverage reporting |
| 8 | Extract `_make_client()` to shared conftest | Reduces test duplication |
| 9 | Add `timeout` to all HTTP requests | Prevents indefinite hangs |
| 10 | Remove dead code (`del data`, `tracer`, unused exceptions) | Reduces confusion |

### Medium-Term Improvements (Months 1-3)

| # | Improvement | Module |
|---|---|---|
| 1 | Deprecate `LiteDB` in favor of `LiteDbRepository` | `db_bot.py` |
| 2 | Add MySQL connection pooling | `pymysql_bot.py` |
| 3 | Split `NewApi` into focused classes (Search, Query, Edit, Upload) | `bot_api.py` |
| 4 | Split `MainPage` into reader/writer/metadata mixins | `super_page.py` |
| 5 | Standardize all method naming to `snake_case` | All modules |
| 6 | Add `__all__` and re-exports to all `__init__.py` | All packages |
| 7 | Adopt `core/exceptions.py` hierarchy across codebase | All modules |
| 8 | Rename `handel_errors.py` to `handle_errors.py` | `api_utils/` |
| 9 | Make `BOT_USERNAME` and Arabic prefix configurable | `bot_edit/`, `txtlib.py` |
| 10 | Add type annotations to all public methods | All modules |

### Long-Term Strategic Refactoring (Months 3-6)

| # | Refactoring | Rationale |
|---|---|---|
| 1 | Unify exception hierarchies (`core/` + `api_client/`) | Single error handling strategy |
| 2 | Implement proactive rate limiting | Prevent API abuse |
| 3 | Add `urllib3.util.retry.Retry` + `HTTPAdapter` | Transport-level resilience |
| 4 | Split `client.py` into `transport.py`, `auth.py`, `pagination.py` | 850+ line file |
| 5 | Replace `tqdm` with callback pattern | Decouple UI from logic |
| 6 | Add `__enter__`/`__exit__` to client classes | Clean resource management |
| 7 | Add `abc.ABC` + `@abstractmethod` for abstract methods | Type safety |
| 8 | Add structured error context to exceptions | Debugging aid |

### Security Hardening Priorities

| Priority | Action |
|---|---|
| P0 | Remove or parameterize `LiteDB.query()` and `LiteDB.update()` |
| P0 | Add SPARQL query sanitization |
| P1 | Set cookie file permissions to 0o600 |
| P1 | Set cookie directory to 0o700 |
| P2 | Zeroize password memory after login |
| P2 | Add input validation for `lang`/`family` parameters |
| P3 | Add structured logging with credential redaction |

### DevOps and Testing Recommendations

| Category | Recommendation |
|---|---|
| CI/CD | Add GitHub Actions with lint (`ruff`), type check (`mypy`), and test (`pytest`) |
| Coverage | Configure `pytest-cov` with 60% minimum threshold |
| Integration | Add integration tests against a test wiki instance |
| Dependencies | Pin all dependencies in `requirements.txt` with `pip-compile` |
| Pre-commit | Add `pre-commit` hooks for `ruff`, `black`, `isort` |
| Property testing | Add `hypothesis` tests for wikitext parsing |
| Contract testing | Add API contract tests for MediaWiki response shapes |

---

## Final Evaluation

### Module Scores

| Module | Score | Rating |
|---|---|---|
| `api_client/` | 6.5/10 | Best module -- clean architecture, good tests, fixable bugs |
| `core/` | 7.5/10 | Cleanest code -- but unused in practice |
| `utils/` | 7.0/10 | Simple and correct |
| `client_wiki/` | 6.0/10 | Good structure, messy internals |
| `client_wiki/api_utils/` | 6.0/10 | Functional but naming issues |
| `client_wiki/categories/` | 6.5/10 | Clean logic, fragile error handling |
| `client_wiki/pages/` | 6.0/10 | God class, type mismatches |
| `DB_bots/` | 5.0/10 | SQL injection, dual abstractions |
| `super/` | 5.0/10 | God class, 3 crash bugs |
| `super/S_API/` | 4.5/10 | Lowest rated -- crash bugs in common paths |
| `tests/` | 5.0/10 | Good unit tests exist but 20+ modules untested |

### Aggregate Scores

| Metric | Score |
|---|---|
| **Overall Project Score** | **5.5 / 10** |
| **Risk Level** | **HIGH** -- 9 crash bugs, 1 SQL injection, 3 security vulnerabilities |
| **Technical Debt Level** | **HIGH** -- god classes, inconsistent naming, unused abstractions, 20+ untested modules |
| **Production Readiness** | **NOT READY** -- requires immediate fixes + short-term improvements before deployment |
| **Estimated Effort to Production-Ready** | 4-6 weeks (1 developer) for immediate + short-term fixes |

### Recommended Next Steps

1. **This week**: Fix all 10 immediate issues (crash bugs + security + timeout). These are blocking.
2. **Next 2 weeks**: Address short-term improvements. Focus on error handling, resource management, and test cleanup.
3. **Month 1**: Begin medium-term refactoring. Prioritize splitting god classes and standardizing naming.
4. **Month 2**: Set up CI/CD pipeline, coverage reporting, and dependency pinning.
5. **Month 3+**: Long-term strategic refactoring -- exception unification, rate limiting, async support.

The codebase has a solid architectural foundation and comprehensive API coverage. The issues are fixable. The priority is stabilizing the crash bugs and security vulnerabilities, then systematically reducing technical debt through the roadmap above.

---

## Shared Module Dependencies

`newapi_bot` is **independent shared infrastructure** — it does not import from `shared/`. Instead, it **provides** the core API layer consumed by other repos:

| Consumer | Import |
|----------|--------|
| `core1` | `from newapi import AllAPIS`, `from newapi.page import load_main_api` |
| `asa_core` | `from newapi.page import load_main_api` |
| `core_cat` | `from newapi import ...` |
| `master2` | `from newapi import ...` |
| `wd_core` | `from newapi import ...` |

The `AllAPIS` facade in `newapi/client_wiki/all_apis.py` is the primary entry point. The deprecated `newapi.page.load_main_api()` still exists for backwards compatibility.

Note: `shared/` contains a parallel `api_page` module that wraps `newapi` with `lru_cache`. Some repos use `shared/api_page` while others import `newapi` directly.
