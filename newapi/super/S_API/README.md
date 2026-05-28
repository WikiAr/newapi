# S_API -- MediaWiki Bot API Implementation

## Project Overview

The `S_API` package contains the `NewApi` class, the primary high-level interface for MediaWiki bot operations. This is where the bulk of the bot's wiki interaction logic lives.

### Main Modules

| Module | Purpose |
|---|---|
| `bot_api.py` | `NewApi` class -- 30+ methods for search, query, edit, upload, and page manipulation |

### Technologies & Dependencies

- **`tqdm`** -- Progress bars for batch operations
- **Internal**: `WikiLoginClient`, `HandleErrors`, `AskBot`, `change_codes`

---

## Architecture & Code Quality Review

### Code Organization

**Fair.** Single file (`bot_api.py`) containing one large class with 30+ methods spanning 1300+ lines.

### Design Patterns

- **Facade**: Wraps `WikiLoginClient` behind a high-level API.
- **Mixin**: Inherits `HandleErrors` and `AskBot` for error handling and user prompts.
- **Delegation**: Most methods delegate to `login_bot.client_request` or `login_bot.post_continue`.

### Maintainability

**Low.** The god-class approach with 1300+ lines, mixed naming, and no docstrings makes this the hardest module to maintain.

---

## Strengths

- **Comprehensive coverage**: 30+ methods covering search, query, edit, upload, move, and more.
- **Batch processing**: Chunking with `tqdm` for large operations.
- **Delegation pattern**: Clean separation from transport layer.

---

## Weaknesses

- **God class**: 1300+ lines, 30+ methods in a single class.
- **Inconsistent naming**: PascalCase, snake_case, and mixed conventions.
- **No docstrings** on most methods.
- **No type annotations** on many methods.
- **Shadowed builtins**: `max` parameter in multiple methods.

---

## Critical Issues

See the parent `super/README.md` for the full critical issues list. Key bugs in this file:

1. `PrefixSearch` deletes wrong dict key -- `KeyError` (line 299)
2. `querypage_list` calls `.isdigit()` on `None` -- `AttributeError` (line 697)
3. `move()` infinite recursion on `ratelimited` (line 1180)
4. `upload_by_file` file handle leak (line 1269)
5. `get_username()` always returns `""` (line 26)

---

## Areas That Need Attention

- **Split into focused modules**: Search, Query, Edit, Upload, Utilities.
- **Fix all crash bugs** listed above.
- **Add docstrings and type annotations**.
- **Standardize naming** to `snake_case`.

---

## Improvement Plan

### Quick Wins
1. Fix the three crash bugs (KeyError, AttributeError, infinite recursion).
2. Use context manager for file handles.
3. Fix `get_username()` to read from `login_bot`.

### Medium-Term Improvements
1. Add docstrings and type annotations.
2. Standardize method naming.
3. Remove dead code.

### Long-Term Refactoring
1. Split `NewApi` into focused classes/modules.
2. Add comprehensive unit tests.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **4.5/10** |
| **Production Readiness** | Low -- multiple crash bugs in common code paths |
| **Technical Debt** | Very High -- god class, no docs, no tests, crash bugs |
| **Risk Assessment** | High -- KeyError, AttributeError, infinite recursion |
| **Maintainability** | 3/10 -- 1300+ line god class with no tests |
