# tests -- Test Suite

## Project Overview

The `tests/` directory contains the test suite for the `newapi` package, using **pytest** as the test framework. Tests are organized into top-level integration tests and `unit/` subdirectory tests.

### Test Structure

```
tests/
  __init__.py                          # Package marker
  conftest.py                          # Shared fixtures (socket disabling, mock clients)
  TestAuthentication.py                # WikiLoginClient login tests
  TestNewAPI.py                        # NewApi basic tests
  TestALL_APIS.py                      # AllAPIS facade tests
  TestMainPage.py                      # MainPage operation tests
  TestLiteDB.py                        # LiteDB database tests
  test_mdwiki_page.py                  # Empty file (0 bytes)
  unit/
    api_client/
      test_client.py                   # WikiLoginClient unit tests (17 tests)
      test_cookies.py                  # Cookie management tests (9 tests)
      test_exceptions.py               # Exception hierarchy tests (9 tests)
      test_requests_handler.py         # RequestsHandler tests (13 tests, 1 class skipped)
    api_utils/
      bot_edit/
        test_bot_edit_by_time.py       # Stub -- imports only, no tests
        test_bot_edit_by_templates.py  # Template-based edit checks (~30 tests)
        test_bot_edit_by_templates2.py # Extended template tests (~40 tests)
        test_bot_edit_by_templates_pypass.py # Bypass condition tests (6 tests)
```

### Technologies & Dependencies

- **`pytest`** -- Test framework
- **`pytest-socket`** -- Disables network access in unit tests
- **`unittest.mock`** -- Mocking (`MagicMock`, `patch`)

---

## Architecture & Code Quality Review

### Test Organization

**Fair.** Clear separation between integration tests (top-level) and unit tests (`unit/`). However, naming is inconsistent (PascalCase vs snake_case filenames).

### Test Patterns

- **Socket disabling**: `conftest.py` autouse fixture prevents accidental network calls.
- **Mock factories**: `_make_client()` helper in unit tests creates properly configured mocks.
- **Parametrized tests**: `test_bot_edit_by_templates2.py` uses `@pytest.mark.parametrize` extensively.
- **Cache isolation**: Bot edit tests clear `Bot_Cache` before/after each test.

### Coverage

| Category | Status |
|---|---|
| `api_client/` | **Good** -- 48 tests across 4 files |
| `bot_edit/` | **Good** -- ~76 tests across 3 files |
| `client_wiki/` | **Poor** -- Only 4 tautological tests in `TestALL_APIS.py` |
| `super/S_API/` | **Poor** -- Only 2 tautological tests in `TestNewAPI.py` |
| `DB_bots/` | **Poor** -- 3 tests (1 skipped) in `TestLiteDB.py` |
| `core/` | **None** -- No tests |
| `config.py` | **None** -- No tests |
| `logging_config.py` | **None** -- No tests |
| `utils/` | **None** -- No tests |
| 20+ other modules | **None** -- No tests |

---

## Strengths

- **Good unit test quality**: `api_client/` and `bot_edit/` tests use proper mocking, parametrization, and edge case coverage.
- **Network isolation**: `pytest_socket.disable_socket` prevents accidental API calls.
- **Cache isolation**: Bot edit tests properly clear global state between runs.
- **Exception hierarchy testing**: `test_exceptions.py` validates inheritance chains.

---

## Weaknesses

- **Tautological assertions**: Top-level tests (`TestAuthentication`, `TestNewAPI`, `TestMainPage`) assert `result is not None` on MagicMock objects -- always passes.
- **Empty test bodies**: `test_empty_page_content` and `test_page_title_validation` have no logic.
- **Empty stub files**: `test_mdwiki_page.py` (0 bytes) and `test_bot_edit_by_time.py` (imports only).
- **Permanently skipped tests**: `TestLiteDB.test_create_table` and `TestPostContinue` class.
- **Duplicated helper**: `_make_client()` identically defined in `test_client.py` and `test_requests_handler.py`.
- **20+ untested modules**: Configuration, logging, database, text processing, category queries, and Wikidata SPARQL have zero test coverage.

---

## Critical Issues

### 1. Tautological Tests Provide False Confidence (HIGH)

```python
# TestAuthentication.py
def test_successful_login(self, mock_login_client):
    response = mock_login_client.client_request({"action": "query"})
    assert response is not None  # Always True for MagicMock
    assert len(response) > 0     # Always True for MagicMock
```

These tests can never fail and provide no safety net.

### 2. Empty Test Files Mislead Coverage Reports (MEDIUM)

`test_mdwiki_page.py` and `test_bot_edit_by_time.py` exist but contain no tests, giving a false impression of coverage.

### 3. Direct `sys.argv` Mutation (MEDIUM)

```python
# test_bot_edit_by_templates.py
sys.argv = ["script"]  # Fragile -- if test fails, teardown may not run
```

Should use `unittest.mock.patch("sys.argv", [...])`.

---

## Areas That Need Attention

- **Fix or remove tautological tests** -- they provide no value.
- **Remove empty stub files** or implement actual tests.
- **Extract `_make_client()`** to a shared conftest or helper module.
- **Add tests for untested modules** (config, logging, DB, categories, SPARQL, etc.).
- **Fix skipped tests** or document why they remain skipped.
- **Use `patch("sys.argv")`** instead of direct mutation.

---

## Improvement Plan

### Quick Wins
1. Remove or fix tautological assertions in top-level tests.
2. Remove empty test files (`test_mdwiki_page.py`, `test_bot_edit_by_time.py`).
3. Extract `_make_client()` to `tests/unit/conftest.py`.
4. Use `patch("sys.argv")` in bot_edit tests.

### Medium-Term Improvements
1. Add unit tests for `config.py`, `logging_config.py`, `pformat.py`.
2. Add unit tests for `db_bot.py` and `pymysql_bot.py`.
3. Add unit tests for `txtlib.py`, `wd_sparql.py`, `handel_errors.py`.
4. Fix or remove permanently skipped tests.

### Long-Term Refactoring
1. Add integration tests with a test wiki instance.
2. Add coverage reporting to CI/CD.
3. Aim for 80%+ code coverage on core modules.
4. Add property-based testing for wikitext parsing.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **5/10** |
| **Production Readiness** | Low -- most modules untested, tautological tests |
| **Technical Debt** | High -- empty files, duplicates, inconsistent patterns |
| **Risk Assessment** | High -- 20+ untested modules, false confidence from tautological tests |
| **Maintainability** | 5/10 -- good unit tests exist but coverage is very incomplete |
