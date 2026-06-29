# api_client -- MediaWiki API Client

## Project Overview

The `api_client` package provides a robust, authenticated HTTP client for the MediaWiki API, built on top of `mwclient`. It handles session persistence, bot authentication, automatic retry on transient errors, and continuation pagination.

### Main Modules

| Module | Purpose |
|---|---|
| `client.py` | Core client classes: `RequestsHandler` (retry/transport), `CookiesClient` (cookie I/O), `WikiLoginClient` (business layer) |
| `cookies.py` | Cookie file path resolution, staleness checks, and cleanup |
| `exceptions.py` | Custom exception hierarchy rooted at `WikiClientError` |

### Technologies & Dependencies

- **`mwclient`** -- MediaWiki client library (provides `Site` and session management)
- **`requests`** -- HTTP transport (used internally by mwclient)
- **`http.cookiejar.LWPCookieJar`** -- Mozilla-format cookie persistence
- **Standard library:** `copy`, `logging`, `os`, `stat`, `time`, `datetime`, `pathlib`

---

## Architecture & Code Quality Review

### Code Organization

The package follows a layered architecture:

1. **Transport layer** (`RequestsHandler`) -- HTTP execution, retry logic, CSRF/maxlag/rate-limit handling
2. **Persistence layer** (`CookiesClient`) -- Cookie file I/O
3. **Business layer** (`WikiLoginClient`) -- Authentication, request enrichment, pagination

### Design Patterns

- **Template Method Pattern**: `RequestsHandler` defines the retry loop skeleton and calls abstract hooks (`_session`, `_refresh_csrf_token`, `_on_assertnameduserfailed`) that `WikiLoginClient` implements.
- **Mixin / Multiple Inheritance**: `WikiLoginClient` inherits from both `CookiesClient` and `RequestsHandler`.
- **Facade**: Wraps `mwclient.Site` and `requests.Session` behind a simplified interface.
- **Strategy-like error handling**: The retry loop dispatches on error code to distinct handlers (CSRF, maxlag, assertnameduserfailed, ratelimited).

### Maintainability

**Moderate.** The class hierarchy is clear, but `client_request_retry` is a near-exact copy-paste of `_client_request`, creating a maintenance hazard. The 850+ line `client.py` file would benefit from splitting.

### Readability

**Good.** Method names are descriptive, logging is consistent (`%s` formatting), and the retry loop is well-structured with clear error dispatch.

### Scalability Considerations

The client is single-threaded with no connection pooling configuration beyond what mwclient provides. No proactive rate limiting exists -- only reactive handling after receiving `ratelimited` errors.

---

## Strengths

- **Robust retry logic**: Handles CSRF token invalidation, maxlag, rate limiting, and session expiry with configurable retry counts and exponential backoff.
- **Cookie persistence**: Sessions survive process restarts via LWPCookieJar with automatic staleness invalidation (3-day max age).
- **Write-action safety**: Automatically injects `bot=1` and `assertuser` parameters for mutating API requests.
- **Clean exception hierarchy**: Well-structured custom exceptions with a common base class.
- **Continuation pagination**: `post_continue` handles multi-page API responses transparently.

---

## Weaknesses

- **Code duplication**: `client_request_retry` (lines 693-766) is a copy-paste of `_client_request` logic. Any bug fix in one must be manually replicated in the other.
- **Unused exceptions**: `MaxRetriesExceededError` and `CookieError` are defined and exported but never raised anywhere in the codebase.
- **Shadowed builtins**: The `max` parameter in `post_continue` shadows Python's built-in `max()`.
- **Hardcoded domain workaround**: `mdwiki.org` special case baked into the general-purpose client (line 442).
- **Unused `**kwargs`**: All three request methods accept `**kwargs` but never pass them downstream.

---

## Critical Issues

### 1. Infinite Loop on Persistent Rate Limiting (HIGH)

```python
# client.py, lines 236-239
if error_code == "ratelimited":
    time.sleep(3)
    continue  # <-- attempt is NEVER incremented
```

Every other error handler increments `attempt` before `continue`. The `ratelimited` handler does not, creating an infinite loop if the server persistently returns rate-limit errors.

### 2. `_ensure_logged_in` Does Not Actually Log In (HIGH)

The method only checks cookie-based revival. If cookies are absent or stale, it silently does nothing. The caller `__init__` proceeds with an unauthenticated session despite the class docstring claiming authentication is ensured.

### 3. No HTTP Timeout (MEDIUM)

`_execute_request` calls `self._session.request(...)` without any `timeout` parameter. A stalled server will hang the client indefinitely.

### 4. `client_request_safe` Silently Swallows All Exceptions (MEDIUM)

```python
# client.py, lines 674-691
except Exception:
    logger.exception("...")
    return {}
```

This catches `LoginError`, `CSRFError`, and even programming bugs. Callers cannot distinguish "API returned empty data" from "critical failure occurred."

### 5. `post_continue` Returns Partial Results Silently (MEDIUM)

Uses `client_request_safe` for continuation pages. If a continuation page fails, the method returns incomplete data without any indication.

### 6. Cookie Directory Permissions (LOW)

`os.chmod` sets `0o770` on the cookies directory, making it readable/writable by any user in the group. Cookie files themselves inherit the default umask (potentially world-readable).

---

## Areas That Need Attention

- **Missing HTTP timeout**: Add `timeout=(connect, read)` to all HTTP requests.
- **Missing `__init__.py` exports**: `_delete_cookie_file` is a private-underscore function imported across modules -- rename or make public.
- **No context manager**: The client holds resources (`requests.Session`, cookie jar) but provides no `__enter__`/`__exit__` for clean release.
- **No abstract base class**: `RequestsHandler` uses `raise NotImplementedError` instead of `abc.ABC` with `@abstractmethod`.
- **No input validation**: `lang` and `family` parameters are not validated -- empty strings or special characters produce malformed URLs.
- **No structured error context**: Exceptions carry only a message string. Adding `error_code`, `url`, `attempt_count` fields would aid debugging.
- **f-string in logger call** (line 575): Inconsistent with the rest of the module's `%s` formatting and defeats lazy evaluation.

---

## Improvement Plan

### Quick Wins
1. Increment `attempt` in the `ratelimited` handler to prevent infinite loops.
2. Add `timeout` parameter to `_execute_request`.
3. Remove `client_request_retry` duplication -- delegate to `_client_request`.
4. Raise unused exceptions (`MaxRetriesExceededError`, `CookieError`) or remove them.
5. Fix the f-string logger call to use `%s` formatting.

### Medium-Term Improvements
1. Implement `_ensure_logged_in` to actually trigger login when cookies are absent.
2. Add `__enter__`/`__exit__` context manager support.
3. Use `abc.ABC` and `@abstractmethod` for `RequestsHandler`.
4. Add proactive rate limiting (minimum delay between requests).
5. Validate `lang` and `family` parameters in the constructor.
6. Make the `mdwiki.org` workaround configurable.

### Long-Term Refactoring
1. Split `client.py` into separate modules: `transport.py`, `auth.py`, `pagination.py`.
2. Add structured error context to all exceptions.
3. Configure `urllib3.util.retry.Retry` and `HTTPAdapter` at the transport level.
4. Add request/response timing instrumentation.
5. Implement connection pooling configuration.

---

## Comprehensive Review

| Metric | Score |
|---|---|
| **Overall Rating** | **6.5/10** |
| **Production Readiness** | Moderate -- functional but has infinite loop bug and missing timeouts |
| **Technical Debt** | Medium -- code duplication, unused exceptions, hardcoded workarounds |
| **Risk Assessment** | Medium-High -- the ratelimited infinite loop and missing timeouts are production risks |
| **Maintainability** | 6/10 -- clear architecture but duplicated code and 850+ line file |
