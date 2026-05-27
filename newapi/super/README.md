# super -- High-Level MediaWiki Bot API

## Project Overview

The `super` package provides the `NewApi` class, the main high-level interface for MediaWiki bot operations including page queries, searches, user contributions, file uploads, and page editing.

### Main Modules

| Module | Purpose |
|---|---|
| `S_API/bot_api.py` | `NewApi` class -- 30+ methods for wiki operations |

### Sub-Package Structure

```
super/
  __init__.py      # Re-exports bot_api
  S_API/
    __init__.py    # Empty
    bot_api.py     # NewApi class (1300+ lines)
```

### Technologies & Dependencies

- **`tqdm`** -- Progress bars for batch operations
- **Internal**: `WikiLoginClient`, `HandleErrors`, `AskBot`, `change_codes`

---

## Architecture & Code Quality Review

### Code Organization

**Fair.** The `NewApi` class in `bot_api.py` is 1300+ lines with 30+ methods covering diverse functionality (search, upload, move, edit, query). This god-class would benefit from decomposition.

### Design Patterns

- **Facade**: Wraps `WikiLoginClient` behind a high-level API.
- **Template Method / Mixin**: Inherits from `HandleErrors` and `AskBot`.
- **Delegation**: Most methods delegate to `login_bot.client_request` or `login_bot.post_continue`.

### Maintainability

**Low.** A single 1300+ line class with mixed naming conventions, no docstrings on most methods, and Arabic/English comment mixing.

### Readability

**Low-Moderate.** Method names are inconsistent (PascalCase, snake_case, mixed). Many methods lack docstrings and type annotations.

### Scalability Considerations

Batch operations like `Find_pages_exists_or_not_with_qids` use chunking with `tqdm`, which is good for large datasets. However, `chunk_titles` with `tqdm` couples UI to logic.

---

## Strengths

- **Comprehensive API coverage**: 30+ methods covering search, query, edit, upload, move, and more.
- **Batch processing**: `chunk_titles` and `Find_pages_exists_or_not_with_qids` handle large title lists efficiently.
- **Continuation support**: `post_continue` handles multi-page API responses.
- **Mixin composition**: `HandleErrors` and `AskBot` provide reusable error handling and user prompts.

---

## Weaknesses

- **God class**: `NewApi` at 1300+ lines with 30+ methods violates single responsibility.
- **Inconsistent naming**: Mix of `PascalCase` (`Find_pages_exists_or_not`), `snake_case` (`get_logs`), and mixed (`Add_To_Bottom`).
- **Missing docstrings**: Most methods lack documentation.
- **Missing type annotations**: Many methods have no return type hints.
- **Shadowed builtins**: `max` parameter used in multiple methods shadows Python's built-in `max()`.
- **Arabic/English comment mixing**: Hinders maintainability for non-Arabic-speaking developers.

---

## Critical Issues

### 1. Infinite Recursion on Rate Limit in `move()` (HIGH)

```python
# bot_api.py, line 1180
if error_code == "ratelimited":
    return self.move(old_title, to, reason, ...)  # No retry limit!
```

If the API persistently returns `ratelimited`, this recurses infinitely until stack overflow. No delay, no retry counter, no backoff.

### 2. `KeyError` Bug in `PrefixSearch()` (HIGH)

```python
# bot_api.py, line 299
del params["apnamespace"]  # Bug: key is "psnamespace"
```

The params dict uses `"psnamespace"`, not `"apnamespace"`. This will raise `KeyError` when the code path is taken.

### 3. `AttributeError` in `querypage_list()` (HIGH)

```python
# bot_api.py, line 697
if qplimit.isdigit():  # qplimit defaults to None!
```

`qplimit` defaults to `None`, and `.isdigit()` is called on it, raising `AttributeError`.

### 4. File Handle Leak in `upload_by_file()` (MEDIUM)

```python
# bot_api.py, line 1269
file = open(file_path, "rb")  # Never closed
data = self.login_bot.client_request_safe(params, files={"file": file})
```

No context manager is used. If the request fails, the file handle leaks.

### 5. `AttributeError` Risk in `upload_by_file()` (MEDIUM)

```python
# bot_api.py, line 1271
result = data.get("upload", {})  # data could be None from client_request_safe
```

`client_request_safe` can return `{}` on failure, but the preceding assignment could also yield `None` in edge cases.

### 6. `get_username()` Always Returns `""` (MEDIUM)

```python
# bot_api.py, __init__
self.username = getattr(self, "username", "")  # Always "" since username not set yet
```

The `getattr` reads `self.username` before it's ever set, so it always gets the default `""`.

---

## Areas That Need Attention

- **Split the god class**: Separate search, query, edit, upload, and utility methods into focused classes or modules.
- **Fix the three crash bugs**: `PrefixSearch` KeyError, `querypage_list` AttributeError, `move` infinite recursion.
- **Add docstrings and type annotations** to all public methods.
- **Standardize naming** to `snake_case`.
- **Use context managers** for file handles in `upload_by_file`.
- **Fix dead code**: Hardcoded `"ususers": "Mr.Ibrahembot"` in `users_infos`.

---

## Improvement Plan

### Quick Wins
1. Fix `PrefixSearch` to delete `"psnamespace"` instead of `"apnamespace"`.
2. Fix `querypage_list` to handle `None` qplimit.
3. Add retry limit to `move()` recursion.
4. Use `with open(...)` in `upload_by_file`.
5. Fix `get_username()` to read from `login_bot`.

### Medium-Term Improvements
1. Add docstrings and return type annotations to all methods.
2. Standardize method naming to `snake_case`.
3. Remove dead code (hardcoded `ususers`, unused `_error` variables).
4. Remove `tqdm` coupling from `chunk_titles`.

### Long-Term Refactoring
1. Split `NewApi` into focused classes: `SearchApi`, `QueryApi`, `EditApi`, `UploadApi`.
2. Implement proper error handling with the `core/exceptions.py` hierarchy.
3. Add comprehensive unit tests.
4. Make `Get_All_pages_generator` actually return a generator.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **5/10** |
| **Production Readiness** | Low -- three crash bugs and a god class |
| **Technical Debt** | High -- 1300+ line class, inconsistent naming, no docs |
| **Risk Assessment** | High -- infinite recursion, KeyError, AttributeError in common code paths |
| **Maintainability** | 4/10 -- god class, no tests, mixed naming, mixed languages |
