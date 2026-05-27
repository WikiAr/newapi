# client_wiki -- MediaWiki Bot Client Library

## Project Overview

The `client_wiki` package is a high-level MediaWiki bot client library that wraps API interactions for reading, editing, creating, and managing wiki pages. It provides abstractions over the raw MediaWiki API, designed for automated bot editing on Wikimedia projects (primarily Arabic and English Wikipedia).

### Main Modules

| Module | Purpose |
|---|---|
| `all_apis.py` | `AllAPIS` facade class -- single entry point for page, category, and API access |
| `constants.py` | Category namespace prefixes by language code |
| `pages/super_page.py` | `MainPage` class -- central abstraction for single wiki page interaction |
| `pages/data.py` | Dataclasses for structured page metadata (Content, Meta, Revisions, etc.) |
| `categories/category_db.py` | `CategoryDepth` -- recursive category tree traversal |
| `categories/catdepth_new.py` | Category depth query functions with caching |
| `api_utils/` | Utility sub-package (see below) |

### Sub-Package: `api_utils/`

| Module | Purpose |
|---|---|
| `botEdit.py` | Bot edit permission checks (entry point) |
| `bot_edit/bot_edit_by_time.py` | Time-based edit permission checks |
| `bot_edit/bot_edit_by_templates.py` | Template-based edit permission checks (nobots, bots, stop-edit) |
| `printe.py` | Colored console output and logging helpers |
| `ask_bot.py` | Interactive user confirmation prompts |
| `txtlib.py` | Wikitext template parsing utilities |
| `handel_errors.py` | MediaWiki API error handler |
| `user_agent.py` | User agent string generation |
| `lang_codes.py` | Legacy-to-standard language code mapping |
| `wd_sparql.py` | Wikidata SPARQL query execution |

### Technologies & Dependencies

- **`wikitextparser`** (`wtp`) -- Wikitext parsing for template extraction
- **`SPARQLWrapper`** -- Wikidata SPARQL queries
- **`pywikibot`** -- Diff display utilities
- **`tqdm`** -- Progress bars for category traversal
- **`mwclient`** (via `api_client`) -- MediaWiki API transport

---

## Architecture & Code Quality Review

### Code Organization

The package is well-organized into logical sub-packages:
- `pages/` -- Page-level operations
- `categories/` -- Category traversal
- `api_utils/` -- Shared utilities
- `api_utils/bot_edit/` -- Edit permission subsystem

### Design Patterns

- **Facade**: `AllAPIS` unifies access to `MainPage`, `CategoryDepth`, and `NewApi` behind a single constructor.
- **Mixin/Multiple Inheritance**: `MainPage` inherits from `HandleErrors` and `AskBot`, composing error handling and user-prompt capabilities.
- **Data Transfer Objects**: Dataclasses in `pages/data.py` provide structured page metadata.
- **Lazy Loading**: Many `MainPage` methods check if data is already loaded before making API calls.
- **Caching**: `lru_cache` used in `txtlib.py`, `user_agent.py`, `catdepth_new.py`; manual dict caches in `bot_edit/`.

### Maintainability

**Moderate.** The sub-package structure is logical, but naming inconsistencies (PascalCase, snake_case, camelCase), a misspelled filename (`handel_errors.py`), and empty `__init__.py` files with no re-exports make navigation harder.

### Readability

**Mixed.** Some modules are clean and well-documented (`category_db.py`), while others mix Arabic and English comments and lack docstrings (`super_page.py` at 1000+ lines).

### Scalability Considerations

Category traversal uses `tqdm` for progress, which couples UI to logic. No rate limiting exists at this layer. The `MainPage` class loads data lazily but caches indefinitely within a single instance.

---

## Strengths

- **Comprehensive page abstraction**: `MainPage` provides 40+ methods covering read, edit, create, purge, metadata, and link analysis.
- **Bot edit safety system**: Multi-layered permission checking (time-based + template-based) prevents editing protected/restricted pages.
- **Facade pattern**: `AllAPIS` provides a clean single-entry-point API.
- **Lazy loading**: Data is fetched only when needed and cached within instances.
- **Wikitext parsing**: `txtlib.py` provides cached template extraction and parameter parsing.
- **Category traversal**: Recursive depth-limited traversal with configurable namespace filtering.

---

## Weaknesses

- **Empty `__init__.py` files**: Nothing is re-exported from sub-packages, requiring consumers to know internal module paths.
- **Misspelled filename**: `handel_errors.py` should be `handle_errors.py`.
- **Inconsistent naming**: Mix of `snake_case` (`get_text`), `PascalCase` (`Get_tags`, `Create`), and camelCase (`isRedirect`, `isDisambiguation`).
- **`MainPage.Create`** is just an alias for `MainPage.create` -- unnecessary duplication.
- **Global mutable state**: `Bot_Cache` in `bot_edit_by_templates.py` and `_save_or_ask` in `ask_bot.py` persist across sessions and are never cleared.
- **Duplicated data**: `change_codes` dictionary is defined identically in both `api_utils/__init__.py` and `api_utils/lang_codes.py`.

---

## Critical Issues

### 1. Mutable Default Argument Bug (HIGH)

```python
# txtlib.py, line 52
def get_one_temp_params(text, tempname="", templates=[], ...):
    temps = templates
    temps.append(tempname)  # Mutates the shared default list!
```

The mutable default `templates=[]` is shared across all calls. Appending to it corrupts subsequent invocations.

### 2. Bare `raise` With No Exception Context (HIGH)

```python
# super_page.py, line 1024
raise  # noqa: PLE0704
```

This raises `RuntimeError` or `TypeError` since there is no active exception. The `noqa` comment suppresses the linter warning about this known problem.

### 3. Type Mismatch in `exists()` (MEDIUM)

`self.meta.Exists` is typed as `str` with default `""`, but is set to `True` (a bool) when confirmed. The `if not self.meta.Exists` check works by coincidence but the type mismatch is a latent bug.

### 4. SPARQL Injection Risk (MEDIUM)

```python
# wd_sparql.py
def get_query_data(query):
    sparql.setQuery(query)  # No sanitization
```

If user-controlled input is interpolated into SPARQL queries upstream, this is an injection vector.

### 5. Destructive Side Effect in `Get_tags()` (MEDIUM)

```python
# super_page.py, line 541
self.text = self.text.replace("<ref>", '<ref name="ss">', 1)
```

Permanently alters `self.text` for the instance -- a hidden side effect that can corrupt page content.

### 6. Inconsistent Return Types from `handle_err` (MEDIUM)

Returns `False`, `"articleexists"`, a description string, or the original error `dict` depending on the error type. Callers must handle all these types.

### 7. Empty String Treated as "Yes" (LOW)

```python
# ask_bot.py, line 57
yes_list = ["y", "a", "", "Y", "A", "all", "aaa"]
```

Empty string `""` (user pressing Enter without intent) is treated as confirmation.

---

## Areas That Need Attention

- **Missing `__init__.py` re-exports**: Add `__all__` and re-export key classes/functions from each sub-package.
- **Missing docstrings**: Many methods in `MainPage` and `NewApi` lack docstrings.
- **Missing type annotations**: Functions like `get_text()`, `get_qid()`, `purge()` lack return types.
- **File naming**: Rename `handel_errors.py` to `handle_errors.py`; rename `botEdit.py` to `bot_edit_utils.py`.
- **`tqdm` coupling**: Progress bar is hardcoded in `category_db.py` with no way to suppress or replace.
- **Arabic template prefix hardcoded**: `"قالب:"` in `txtlib.py` will be incorrect for non-Arabic wikis.
- **No unit tests**: This entire sub-package has zero dedicated test coverage.

---

## Improvement Plan

### Quick Wins
1. Fix mutable default argument in `get_one_temp_params` (`templates=None`).
2. Fix the bare `raise` in `super_page.py`.
3. Remove empty string `""` from `ask_bot.py`'s yes_list.
4. Remove duplicated `change_codes` definition.
5. Add `__all__` to each `__init__.py`.

### Medium-Term Improvements
1. Rename misspelled/misnamed files (`handel_errors.py`, `botEdit.py`).
2. Standardize method naming to `snake_case`.
3. Add type annotations to all public methods.
4. Make `BOT_USERNAME` configurable via `settings`.
5. Replace `tqdm` with a callback/hook pattern.
6. Fix the `Exists` type to be `bool` instead of `str`.

### Long-Term Refactoring
1. Split `super_page.py` (1000+ lines) into focused modules.
2. Implement proper error handling with typed exceptions instead of mixed return types.
3. Add comprehensive unit tests for all modules.
4. Make the Arabic template prefix configurable.
5. Clear global caches (`Bot_Cache`, `_save_or_ask`) between runs.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **6/10** |
| **Production Readiness** | Moderate -- functional but has bugs and no tests |
| **Technical Debt** | High -- naming inconsistencies, global state, code duplication |
| **Risk Assessment** | Medium -- mutable default bug and type mismatches can cause subtle failures |
| **Maintainability** | 5/10 -- large files, inconsistent naming, empty init files |
