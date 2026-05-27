# pages -- Wiki Page Abstraction

## Project Overview

The `pages` sub-package provides the `MainPage` class, the central abstraction for interacting with a single MediaWiki wiki page. It supports reading, editing, creating, purging, and querying page metadata.

### Main Modules

| Module | Purpose |
|---|---|
| `super_page.py` | `MainPage` class (1000+ lines, 40+ methods) and `find_edit_error` helper |
| `data.py` | Dataclasses for structured page metadata |

### Dataclasses (`data.py`)

| Class | Fields |
|---|---|
| `Content` | `text_html`, `summary`, `words`, `length` |
| `Meta` | `is_disambig`, `can_be_edit`, `userinfo`, `create_data`, `info`, `username`, `Exists`, `is_redirect`, `flagged`, `wikibase_item` |
| `RevisionsData` | `revid`, `newrevid`, `pageid`, `timestamp`, `revisions`, `touched` |
| `LinksData` | `back_links`, `extlinks`, `iwlinks`, `links_here`, `links`, `links2` |
| `CategoriesData` | `categories`, `hidden_categories`, `all_categories_with_hidden` |
| `TemplateData` | `templates`, `templates_api` |

### Technologies & Dependencies

- **`wikitextparser`** (`wtp`) -- Template extraction in `get_templates()`
- **Internal**: `WikiLoginClient`, `HandleErrors`, `AskBot`

---

## Architecture & Code Quality Review

### Code Organization

**Fair.** Two files, but `super_page.py` at 1000+ lines is a god class with 40+ methods.

### Design Patterns

- **Lazy Loading**: Data fetched only when requested, cached within the instance.
- **Mixin Composition**: `MainPage(HandleErrors, AskBot)` composes error handling and user prompts.
- **Data Transfer Objects**: Dataclasses in `data.py` provide structured metadata.

### Maintainability

**Low-Moderate.** The 1000+ line class with mixed naming conventions is hard to navigate.

---

## Strengths

- **Comprehensive page API**: 40+ methods covering read, edit, create, purge, metadata, links, categories, templates.
- **Lazy loading**: Data fetched only when needed.
- **Structured metadata**: Dataclasses provide clear data shapes.

---

## Weaknesses

- **God class**: `MainPage` at 1000+ lines with 40+ methods.
- **Inconsistent naming**: `get_text` (snake_case) vs `isRedirect` (camelCase) vs `Get_tags` (PascalCase).
- **Type mismatch**: `Exists` field is `str` but set to `True` (bool).
- **Side effects**: `Get_tags()` permanently mutates `self.text`.

---

## Critical Issues

### 1. Bare `raise` With No Exception Context (HIGH)

```python
# super_page.py, line 1024
raise  # noqa: PLE0704
```

### 2. Type Mismatch in `exists()` (MEDIUM)

`self.meta.Exists` typed as `str`, default `""`, set to `True` (bool).

### 3. Destructive Side Effect in `Get_tags()` (MEDIUM)

```python
self.text = self.text.replace("<ref>", '<ref name="ss">', 1)
```

---

## Areas That Need Attention

- **Split `MainPage`** into focused mixins or separate classes.
- **Fix type mismatch** for `Exists`.
- **Standardize naming** to `snake_case`.
- **Add type annotations** to all public methods.
- **Add `__all__`** to `data.py`.

---

## Improvement Plan

### Quick Wins
1. Fix the bare `raise`.
2. Change `Exists` type to `bool`.
3. Add `__all__` to `data.py`.

### Medium-Term Improvements
1. Standardize naming to `snake_case`.
2. Add type annotations.
3. Split read and write operations.

### Long-Term Refactoring
1. Split `MainPage` into `PageReader`, `PageWriter`, `PageMetadata` mixins.
2. Add comprehensive unit tests.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **6/10** |
| **Production Readiness** | Moderate -- functional but has bugs and is hard to maintain |
| **Technical Debt** | High -- god class, naming issues, type mismatches |
| **Risk Assessment** | Medium -- bare raise, type mismatches, side effects |
| **Maintainability** | 5/10 -- 1000+ line class, no tests, mixed naming |
