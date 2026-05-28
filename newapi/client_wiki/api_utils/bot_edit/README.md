# bot_edit -- Bot Edit Permission System

## Project Overview

The `bot_edit` sub-package determines whether a bot is allowed to edit a specific wiki page, based on two complementary strategies: time-based restrictions and template-based restrictions.

### Main Modules

| Module | Purpose |
|---|---|
| `bot_edit_by_time.py` | Checks if a page was recently created or edited (within a delay window) |
| `bot_edit_by_templates.py` | Checks for `{{nobots}}`, `{{bots}}`, and stop-edit templates in page content |

### How It Works

The entry point is `botEdit.py` (parent directory), which calls:

```python
def bot_May_Edit(text, title_page, botjob, page, delay):
    # 1. Check time-based restrictions
    if not check_create_time(page, title_page): return False
    if not check_last_edit_time(page, title_page, delay): return False
    # 2. Check template-based restrictions
    if not is_bot_edit_allowed(text, title_page, botjob): return False
    return True
```

### Technologies & Dependencies

- **`wikitextparser`** (`wtp`) -- Template extraction from page content
- **Internal**: `config.settings` for bot configuration

---

## Architecture & Code Quality Review

### Code Organization

**Good.** Clear separation between time-based and template-based checks.

### Design Patterns

- **Strategy**: Two independent strategies composed in sequence.
- **Caching**: Manual dict caches (`Bot_Cache`, `_created_cache`) for repeated lookups.

### Maintainability

**Moderate.** Files are focused and manageable, but global mutable caches and hardcoded values reduce flexibility.

---

## Strengths

- **Multi-layered protection**: Combines time-based and template-based checks.
- **Comprehensive template detection**: Handles `{{nobots}}`, `{{bots|allow/disallow}}`, and language-specific stop-edit templates.
- **Caching**: Avoids redundant API calls for repeated page checks.

---

## Weaknesses

- **Global mutable caches**: `Bot_Cache` and `_created_cache` never expire or clear.
- **Hardcoded bot username**: `BOT_USERNAME = "Mr.Ibrahembot"` should be configurable.
- **No tests for `bot_edit_by_time.py`**: The test file exists but contains only imports.

---

## Critical Issues

### 1. Stale Cache Entries (MEDIUM)

`_created_cache` in `bot_edit_by_time.py` never expires. If a page is deleted and re-created, the stale cache returns incorrect results.

### 2. Hardcoded Bot Username (LOW)

```python
# bot_edit_by_templates.py, line 23
BOT_USERNAME = "Mr.Ibrahembot"
```

Any bot using this library must have this exact username, or the `{{bots}}` template check will fail.

---

## Areas That Need Attention

- **Make caches configurable** with TTL or clear-between-runs semantics.
- **Make `BOT_USERNAME` configurable** via `settings`.
- **Add tests for `bot_edit_by_time.py`**.

---

## Improvement Plan

### Quick Wins
1. Make `BOT_USERNAME` read from `settings` instead of hardcoding.
2. Add cache clearing mechanism.

### Medium-Term Improvements
1. Add TTL to caches.
2. Add unit tests for `bot_edit_by_time.py`.

### Long-Term Refactoring
1. Convert caches to instance-level state instead of module globals.
2. Make template names configurable per wiki language.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **6.5/10** |
| **Production Readiness** | Moderate -- works but has stale cache and hardcoded values |
| **Technical Debt** | Medium -- global state, missing tests |
| **Risk Assessment** | Low-Medium -- stale cache can cause incorrect edit decisions |
| **Maintainability** | 6/10 -- clean separation but global state |
