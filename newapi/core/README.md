# core -- Exception Hierarchy for MediaWiki API Errors

## Project Overview

The `core` package defines a structured exception hierarchy for MediaWiki API errors, along with a factory function that maps API error responses to typed exception instances.

### Main Modules

| Module | Purpose |
|---|---|
| `exceptions.py` | Exception classes and `parse_api_error` factory function |

### Exception Hierarchy

```
NewApiException (base)
  +-- ApiError
  |     +-- AbuseFilterError
  |     +-- MaxLagError
  |     +-- ArticleExistsError
  |     +-- NoSuchEntityError
  |     +-- ProtectedPageError
  |     +-- InvalidTokenError
  +-- AuthenticationError
  +-- ValidationError
```

### Technologies & Dependencies

- **Standard library only**: `typing.Any`, `Dict`, `Optional`

---

## Architecture & Code Quality Review

### Code Organization

**Good.** Single file with a clear, well-structured exception hierarchy. The `parse_api_error` factory provides a clean mapping from API error dicts to typed exceptions.

### Design Patterns

- **Exception Hierarchy**: All exceptions inherit from `NewApiException`, enabling catch-all handling at any level.
- **Factory Method**: `parse_api_error(error_dict)` maps raw API error responses to the appropriate exception type.

### Maintainability

**High.** Simple, focused module with minimal complexity.

### Readability

**Good.** Clear class names and inheritance structure.

### Scalability Considerations

Not applicable -- this is a data/exception module with no performance concerns.

---

## Strengths

- **Well-structured hierarchy**: Clear inheritance tree covering common MediaWiki API error types.
- **Factory function**: `parse_api_error` provides a single point for error-to-exception mapping.
- **Structured error data**: Each exception carries `code`, `info`, and `message` fields.
- **No external dependencies**: Pure standard library implementation.

---

## Weaknesses

- **Missing `__init__.py`**: The `core/` directory lacks an `__init__.py`, making it inconsistent with other sub-packages (works as namespace package but is unconventional).
- **No `__all__`**: All classes are implicitly public.
- **Unused in codebase**: The exception hierarchy is defined but largely unused -- the rest of the codebase returns mixed types (`bool`, `str`, `dict`) instead of raising these exceptions.
- **No `__str__` override**: Exceptions use the default `Exception.__str__`, which just returns the message. Adding structured fields to `__repr__` would aid debugging.

---

## Critical Issues

**None.** This is a simple, well-implemented module with no bugs or security concerns.

---

## Areas That Need Attention

- **Add `__init__.py`**: Create `core/__init__.py` with re-exports for consistency.
- **Adopt exceptions throughout codebase**: The rest of `newapi` should raise these exceptions instead of returning mixed error types.
- **Add `__all__`**: Explicitly declare the public API surface.
- **Add docstrings**: Classes and the factory function lack docstrings.

---

## Improvement Plan

### Quick Wins
1. Add `core/__init__.py` with `__all__` and re-exports.
2. Add docstrings to all exception classes.
3. Add `__repr__` to `NewApiException` showing `code` and `info`.

### Medium-Term Improvements
1. Migrate `handle_err` in `handel_errors.py` to raise these exceptions instead of returning mixed types.
2. Add more exception types as needed (e.g., `RateLimitError`, `NetworkError`).
3. Add structured context fields (url, attempt_count) to exceptions.

### Long-Term Refactoring
1. Unify the two exception hierarchies (`core/exceptions.py` and `api_client/exceptions.py`) into one.
2. Implement exception-based error handling throughout the entire codebase.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **7.5/10** |
| **Production Readiness** | High -- simple, correct, well-structured |
| **Technical Debt** | Low -- minor missing init file and docs |
| **Risk Assessment** | Low -- no bugs, no security concerns |
| **Maintainability** | 9/10 -- clean, focused, minimal complexity |
