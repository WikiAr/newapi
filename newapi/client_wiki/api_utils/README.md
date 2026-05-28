# api_utils -- Wiki Bot Utility Functions

## Project Overview

The `api_utils` package provides shared utility functions for the MediaWiki bot client, including bot edit permission checking, error handling, wikitext parsing, logging, and Wikidata SPARQL queries.

### Main Modules

| Module | Purpose |
|---|---|
| `botEdit.py` | Entry point for bot edit permission checks (`bot_May_Edit`) |
| `bot_edit/bot_edit_by_time.py` | Time-based edit restrictions (creation time, last edit time) |
| `bot_edit/bot_edit_by_templates.py` | Template-based edit restrictions (nobots, bots, stop-edit templates) |
| `handel_errors.py` | `HandleErrors` class for MediaWiki API error processing |
| `printe.py` | Colored console output and logging helpers (`output`, `error`, `warn`, etc.) |
| `ask_bot.py` | `AskBot` class for interactive user confirmation prompts |
| `txtlib.py` | Wikitext template extraction and parameter parsing |
| `user_agent.py` | User agent string generation |
| `lang_codes.py` | Legacy-to-standard language code mapping (`change_codes`) |
| `wd_sparql.py` | Wikidata SPARQL query execution |

### Technologies & Dependencies

- **`wikitextparser`** (`wtp`) -- Wikitext parsing in `txtlib.py` and `bot_edit_by_templates.py`
- **`SPARQLWrapper`** -- Wikidata SPARQL queries in `wd_sparql.py`
- **`pywikibot`** -- Diff display in `printe.py` and `ask_bot.py`

---

## Architecture & Code Quality Review

### Code Organization

**Fair.** Related files are grouped (`bot_edit/` sub-package), but the flat structure of the parent makes it hard to see logical groupings. The misspelled filename `handel_errors.py` and camelCase `botEdit.py` break conventions.

### Design Patterns

- **Strategy**: Bot edit checks compose time-based and template-based strategies.
- **Caching**: `lru_cache` in `txtlib.py`, `user_agent.py`; manual dict caches in `bot_edit/`.
- **Mixin**: `HandleErrors` and `AskBot` are designed as mixins for multiple inheritance.

### Maintainability

**Moderate.** Individual files are focused and manageable, but naming inconsistencies and global mutable state reduce maintainability.

### Readability

**Mixed.** Some files are clean (`user_agent.py`), while others have inconsistent naming and missing docstrings.

---

## Strengths

- **Multi-layered bot edit safety**: Time-based + template-based permission checking prevents editing protected pages.
- **Cached parsing**: `extract_templates_and_params` uses `lru_cache` for performance.
- **Flexible error handling**: `HandleErrors.handle_err` processes diverse API error types.
- **Colored output**: Custom `<<color>>text<<previous>>` tag system for terminal output.

---

## Weaknesses

- **Misspelled filename**: `handel_errors.py` should be `handle_errors.py`.
- **camelCase filename**: `botEdit.py` should be `bot_edit.py` or `bot_edit_utils.py`.
- **Global mutable caches**: `Bot_Cache` and `_save_or_ask` never cleared between runs.
- **Hardcoded bot username**: `BOT_USERNAME = "Mr.Ibrahembot"` in `bot_edit_by_templates.py`.
- **Hardcoded Arabic prefix**: `"قالب:"` (Template:) in `txtlib.py` breaks non-Arabic wikis.
- **Duplicated `change_codes`**: Defined identically in both `__init__.py` and `lang_codes.py`.

---

## Critical Issues

### 1. Mutable Default Argument in `get_one_temp_params` (HIGH)

```python
# txtlib.py, line 52
def get_one_temp_params(text, tempname="", templates=[], ...):
    temps = templates
    temps.append(tempname)  # Mutates shared default!
```

### 2. Destructive Mutation in `handle_err` (MEDIUM)

```python
# handel_errors.py, lines 108-110
params["data"] = {}
params["text"] = {}
```

Mutates the caller's params dict as a side effect.

### 3. SPARQL Injection Risk (MEDIUM)

`wd_sparql.py` passes queries directly to `SPARQLWrapper.setQuery()` without sanitization.

### 4. Empty String as "Yes" Confirmation (LOW)

```python
# ask_bot.py, line 57
yes_list = ["y", "a", "", "Y", "A", "all", "aaa"]
```

---

## Areas That Need Attention

- **Rename files**: `handel_errors.py` -> `handle_errors.py`, `botEdit.py` -> `bot_edit_utils.py`.
- **Fix mutable default** in `txtlib.py`.
- **Make `BOT_USERNAME` configurable** via `settings`.
- **Remove duplicated `change_codes`**.
- **Add `__all__`** to all `__init__.py` files.
- **Add type annotations** to functions missing them.

---

## Improvement Plan

### Quick Wins
1. Fix mutable default argument in `get_one_temp_params`.
2. Remove empty string from `ask_bot.py`'s yes_list.
3. Remove duplicated `change_codes`.
4. Add `__all__` to `__init__.py`.

### Medium-Term Improvements
1. Rename misspelled/misnamed files.
2. Make `BOT_USERNAME` configurable.
3. Make Arabic template prefix configurable.
4. Clear global caches between runs.

### Long-Term Refactoring
1. Replace `handle_err` return-value pattern with exception-based error handling.
2. Replace `tqdm` coupling with callback pattern.
3. Add unit tests for all modules.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **6/10** |
| **Production Readiness** | Moderate -- functional but has naming issues and global state |
| **Technical Debt** | Medium-High -- misspellings, duplication, hardcoded values |
| **Risk Assessment** | Medium -- mutable default bug can cause subtle failures |
| **Maintainability** | 5/10 -- naming inconsistencies, no tests, global state |
