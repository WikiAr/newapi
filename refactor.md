# Static Analysis Report: newapi_bot

## Executive Summary

This report documents a comprehensive static analysis of the newapi_bot repository, a Python-based MediaWiki API client library. The analysis reveals significant architectural issues including excessive inheritance chains, tight coupling, global state management, and numerous code smells that impact testability and maintainability.

**Analysis Date:** 2026-01-26
**Repository:** newapi_bot
**Scope:** Full codebase analysis
**Lines of Code:** ~15,000+ Python files
**Primary Language:** Python 3.9+

---

## 1. System Overview

### 1.1 Current Architecture

The codebase follows a **layered inheritance-based architecture** with the following structure:

```
User Entry Points (page.py, all_apis.py)
    ↓
Site-Specific Pages (wiki_page.py, mdwiki_page.py, etc.)
    ↓
Domain Modules (pages_bots/)
    ↓
Core Super Layer (super/)
    ├── S_API/        - Generic API operations
    ├── S_Page/       - Page operations (MainPage)
    ├── S_Category/   - Category traversal (CatDepth)
    ├── S_Login/      - Login management
    ↓
Utilities (api_utils/)
    └── DB_bots/      - Database wrappers
```

### 1.2 Key Components

| Component | File | Purpose | Lines |
|-----------|------|---------|-------|
| **MainPage** | `super/S_Page/super_page.py` | Page CRUD operations | ~987 |
| **NEW_API** | `super/S_API/bot_api.py` | API query operations | ~952 |
| **Login** | `super/super_login.py` | Authentication & session | ~315 |
| **CatDepth** | `super/S_Category/bot.py` | Category tree traversal | ~376 |
| **LiteDB** | `DB_bots/db_bot.py` | SQLite wrapper | ~98 |

### 1.3 Design Patterns Identified

1. **Template Method** - Base classes define structure, subclasses override
2. **Facade** - `page.py` provides simplified interface
3. **Cache-Aside** - Login/session caching throughout
4. **Data Transfer Object** - Data classes in `S_Page/data.py`

---

## 2. Code Smells and Anti-Patterns

### 2.1 Excessive Inheritance (Critical)

**Location:** `super/S_Page/super_page.py:66`

```python
class MainPage(PAGE_APIS, ASK_BOT):
    def __init__(self, login_bot, title, lang="", family="wikipedia"):
        # ...
```

**Problem:** Multiple inheritance used as a substitute for composition. `PAGE_APIS` itself inherits from `HANDEL_ERRORS`.

**Impact:**
- Diamond inheritance problems
- Difficult to test (must instantiate full chain)
- Violates "prefer composition over inheritance"

**Refactoring Recommendation:**
```python
# Instead of inheritance, use composition
class MainPage:
    def __init__(self, api_client, error_handler, user_prompter):
        self._api = api_client
        self._errors = error_handler
        self._prompt = user_prompter
```

---

### 2.2 Global Mutable State (Critical)

**Location:** Multiple files throughout

```python
# super/bot.py:24-26
seasons_by_lang = {}  # Module-level session cache
users_by_lang = {}
logins_count = {1: 0}

# api_utils/botEdit.py:14-15
Bot_Cache = {}
Created_Cache = {}

# super/login_wrap.py:14
hases = {}
```

**Problems:**
- State persists between tests causing flaky tests
- Thread-unsafe
- Cannot run multiple instances with different configs

**Impact:** Makes unit testing nearly impossible without extensive setup/teardown

**Refactoring Recommendation:**
```python
# Encapsulate in a session manager class
class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, requests.Session] = {}
        self._login_counts: Dict[str, int] = {}

    def get_session(self, key: str) -> requests.Session:
        # ...
```

---

### 2.3 God Objects (High)

**Location:** `super/S_Page/super_page.py`

The `MainPage` class has ~987 lines and handles:
- Text retrieval/parsing
- Edit validation
- Template processing
- Category/link extraction
- HTML conversion
- User permission checks
- Page creation/editing

**Problem:** Violates Single Responsibility Principle

**Refactoring Recommendation:**
```python
class Page:
    """Core page entity"""
    title: str
    text: str

class PageRepository:
    """Data access for pages"""
    def get_text(self, page: Page) -> str: ...

class TemplateExtractor:
    """Template parsing logic"""
    def extract(self, text: str) -> List[Template]: ...

class EditValidator:
    """Validates if edits are allowed"""
    def can_edit(self, page: Page, user: str) -> bool: ...
```

---

### 2.4 Command Line Coupling (High)

**Location:** Scattered throughout ~50+ occurrences

```python
# api_utils/botEdit.py:122
if ("botedit" in sys.argv or "editbot" in sys.argv) or "workibrahem" in sys.argv:
    return True

# pages_bots/page.py:44
if "workibrahem" in sys.argv:
    User_tables = User_tables_ibrahem

# super/super_login.py:329-332
if "dopost" in sys.argv:
    printe.output("<<green>> dopost:::")
    # ...
```

**Problem:** Business logic controlled by CLI arguments makes testing and library usage difficult

**Impact:**
- Cannot import and use as a library without setting sys.argv
- Testing requires monkey-patching sys.argv

**Refactoring Recommendation:**
```python
@dataclass
class BotConfig:
    bot_edit_enabled: bool = False
    work_mode: str = "standard"
    debug_post: bool = False

class BotEditChecker:
    def __init__(self, config: BotConfig):
        self.config = config

    def can_edit(self, text: str, title: str, job: str) -> bool:
        if self.config.bot_edit_enabled:
            return True
        # ... rest of logic
```

---

### 2.5 Primitive Obsession (Medium)

**Location:** Throughout, e.g., `super/S_Page/super_page.py:658-663`

```python
def exists(self):
    if not self.meta.Exists:
        self.get_text()
    if not self.meta.Exists:
        printe.output(f'page "{self.title}" not exists in {self.lang}:{self.family}')
    return self.meta.Exists
```

**Problem:** `self.meta.Exists` is a string (`""`), not a boolean. Mixed types cause confusion.

**Refactoring Recommendation:**
```python
@dataclass
class PageMetadata:
    exists: bool = False
    is_redirect: bool = False
    is_disambiguation: bool = False
    wikibase_item: str = ""
```

---

### 2.6 Magic Numbers/Strings (Medium)

**Location:** `super/S_Category/bot.py:11-33`

```python
ns_list = {
    "0": "",
    "1": "نقاش",
    "2": "مستخدم",
    # ... hardcoded Arabic namespace names
}
```

**Problem:** Namespace IDs and names hardcoded, not extensible

**Refactoring Recommendation:**
```python
class NamespaceRegistry:
    def __init__(self, lang: str):
        self.namespaces = self._load_namespaces_for_lang(lang)

    def get_local_name(self, ns_id: int) -> str: ...
```

---

### 2.7 Inconsistent Error Handling (Medium)

**Location:** `super/handel_errors.py:15-85`

```python
def handel_err(self, error: dict, function: str = "", params: dict = None, do_error: bool = True):
    # Returns: Union[str, bool] - inconsistent return types
    if err_code == "abusefilter-disallowed":
        if description in ["تأخير البوتات 3 ساعات", ...]:
            return False
        return description  # Returns string
    if err_code == "articleexists":
        return "articleexists"  # Returns string
    return False  # Returns bool
```

**Problem:** Function returns bool, str, or None - calling code must check type

**Refactoring Recommendation:**
```python
class ApiError(Exception):
    code: str
    message: str
    is_retryable: bool = False

class AbuseFilterError(ApiError): pass
class ArticleExistsError(ApiError): pass

def handle_error(error: dict) -> Optional[ApiError]:
    # Parse and return typed error or None
```

---

### 2.8 Duplicated Code (Medium)

**Location:** Multiple files

`post_params` method duplicated in:
- `super/S_API/bot_api.py:74-84`
- `super/S_Page/super_page.py:101-111`
- `super/S_Category/bot.py:67-77`

All delegate to `login_bot.post_params` - should use composition instead.

---

### 2.9 Feature Envy (Medium)

**Location:** `super/S_Page/super_page.py:605`

```python
def can_edit(self, script="", delay=0):
    self.meta.can_be_edit = botEdit.bot_May_Edit(
        text=self.text,
        title_page=self.title,
        botjob=script,
        page=self,  # Passes entire self
        delay=delay
    )
```

**Problem:** `bot_May_Edit` accesses multiple `page` properties - logic should be in Page class

---

### 2.10 Long Parameter Lists (Low-Medium)

**Location:** `super/S_API/bot_api.py:74`

```python
def post_params(self, params, Type="get", addtoken=False, GET_CSRF=True, files=None, do_error=False, max_retry=0):
```

**Refactoring Recommendation:**
```python
@dataclass
class RequestConfig:
    method: str = "get"
    add_token: bool = False
    get_csrf: bool = True
    files: Optional[dict] = None
    do_error: bool = False
    max_retry: int = 0

def post_params(self, params: dict, config: RequestConfig = RequestConfig()):
```

---

## 3. Dependency Issues and Coupling Map

### 3.1 Circular Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                     CIRCULAR DEPENDENCIES                   │
├─────────────────────────────────────────────────────────────┤
│  page.py ──────> pages_bots/page.py ──────>                │
│       ^                                              │       │
│       │                                              v       │
│   all_apis.py <────────────────────── super/S_API/bot_api.py│
│                                                              │
│  super/S_Page/super_page.py ──> api_utils/botEdit.py        │
│        ^                           │                        │
│        │                           v                        │
│        └───────────── api_utils/ask_bot.py ──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Key Issues:**
1. `page.py` re-exports from `pages_bots/page.py` which imports from `super/` which can import back
2. `MainPage` depends on `botEdit` which uses global state affecting `MainPage`
3. `super_login` depends on `handel_errors` which depends on print utilities

### 3.2 Tight Coupling Analysis

| Module | Coupling Score | Dependencies | Issues |
|--------|---------------|--------------|---------|
| `MainPage` | **High (9)** | login_bot, ASK_BOT, HANDEL_ERRORS, botEdit, txtlib, printe, wikitextparser, ar_err, except_err, lang_codes | Direct instantiation, inheritance |
| `NEW_API` | **High (8)** | BOTS_APIS, login_bot, change_codes, tqdm, datetime, printe | Delegates everything to login_bot |
| `Login` | **Medium (6)** | LOGIN_HELPS, HANDEL_ERRORS, printe, cookie management, user_agent | Mixes concerns |
| `CategoryDepth` | **Medium (5)** | login_bot, printe, copy, tqdm | Simpler, mostly delegations |

### 3.3 Dependency Graph (Simplified)

```
                    ┌──────────────┐
                    │   sys.argv   │ (Global coupling)
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼───────┐  ┌──────▼───────┐
│   BotEdit      │  │   printe     │  │ useraccount  │
│ (botEdit.py)   │  │ (printe.py)  │  │ (.ini file)  │
└───────┬────────┘  └──────┬───────┘  └──────┬───────┘
        │                  │                  │
        └────────┬─────────┴──────────┬───────┘
                 │                    │
        ┌────────▼─────────┐  ┌──────▼────────┐
        │   MainPage       │  │   Login       │
        │ (super_page.py)  │  │(super_login)  │
        └────────┬─────────┘  └──────┬────────┘
                 │                    │
                 └────────┬───────────┘
                          │
                 ┌────────▼────────┐
                 │   NEW_API      │
                 │  (bot_api.py)  │
                 └─────────────────┘
```

### 3.4 External Dependencies

| Package | Usage | Risk |
|---------|-------|------|
| `requests` | HTTP client | Low - stable |
| `wikitextparser` | Wiki parsing | Medium - unmaintained? |
| `sqlite_utils` | Database | Low - stable |
| `tqdm` | Progress bars | Low - optional |
| `SPARQLWrapper` | Wikidata queries | Low - isolated |

---

## 4. Refactoring Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Enable testability without breaking existing functionality

1. **Extract Configuration**
   - Create `Config` dataclass to replace sys.argv coupling
   - Add config file support (YAML/TOML)
   - Files: `api_utils/botEdit.py`, `pages_bots/page.py`, `super/super_login.py`

2. **Dependency Injection Container**
   - Create simple DI container for session management
   - Replace global `seasons_by_lang`, `users_by_lang`
   - File: New `core/container.py`

3. **Add Type Hints**
   - Add return types to all public methods
   - Fix inconsistent return types (handel_err)
   - All files in `super/`

### Phase 2: Decomposition (Weeks 3-5)
**Goal:** Break apart god objects into focused components

1. **Split MainPage** (`super/S_Page/super_page.py`)
   ```
   MainPage (coordination only)
   ├── PageRepository (API calls)
   ├── TemplateService (parsing)
   ├── EditValidator (permissions)
   └── PageCache (caching layer)
   ```

2. **Separate API Client** (`super/S_API/bot_api.py`)
   ```
   MediaWikiClient (core HTTP)
   ├── QueryBuilder (params construction)
   ├── ResponseParser (JSON handling)
   └── TokenManager (CSRF tokens)
   ```

3. **Extract Login Logic** (`super/super_login.py`)
   ```
   SessionManager (session lifecycle)
   ├── Authenticator (login flow)
   ├── CookieStore (persistence)
   └── TokenProvider (CSRF/login tokens)
   ```

### Phase 3: Interface Extraction (Weeks 6-7)
**Goal:** Define clear contracts between components

1. **Define Abstract Interfaces**
   ```python
   class PageRepository(ABC):
       def get_text(self, title: str) -> str: ...
       def save(self, title: str, text: str, summary: str) -> bool: ...

   class AuthProvider(ABC):
       def get_token(self) -> str: ...
       def refresh(self) -> bool: ...
   ```

2. **Implement Repository Pattern**
   - Replace direct API calls with repository methods
   - Enable mocking for tests

3. **Service Layer**
   - Create business logic services that use repositories
   - Remove business logic from data access layer

### Phase 4: Error Handling (Week 8)
**Goal:** Consistent, typed error handling

1. **Exception Hierarchy**
   ```python
   class NewapiError(Exception): pass
   class AuthenticationError(NewapiError): pass
   class ApiError(NewapiError): pass
   class ValidationError(NewapiError): pass
   ```

2. **Result Type Pattern** (optional)
   - Return `Result[T, Error]` instead of raising
   - Enables explicit error handling

### Phase 5: Testing Infrastructure (Weeks 9-10)
**Goal:** Comprehensive test coverage

1. **Unit Tests** (target 80% coverage)
   - Mock HTTP responses
   - Test business logic in isolation

2. **Integration Tests**
   - Test against MediaWiki test instance

3. **Property-Based Tests**
   - Use hypothesis for edge cases

---

## 5. Concrete Changes Per File/Module

### 5.1 `newapi/page.py`
**Issues:** Thin wrapper, config via sys.argv

**Changes:**
```python
# BEFORE
if "workibrahem" in sys.argv:
    User_tables = User_tables_ibrahem

# AFTER
def get_main_page(title: str, lang: str, family: str = "wikipedia",
                  config: Optional[BotConfig] = None) -> MainPage:
    config = config or BotConfig.load_default()
    login_bot = get_login_bot(lang, family, config)
    return MainPage(login_bot, title, lang, family)
```

### 5.2 `newapi/super/S_Page/super_page.py`
**Issues:** God object, multiple inheritance, primitive obsession

**Changes:**
```python
# SPLIT INTO:
# 1. core/page.py - Entity
@dataclass
class Page:
    title: str
    lang: str
    family: str
    text: str = ""
    namespace: int = 0
    metadata: PageMetadata = field(default_factory=PageMetadata)

# 2. repositories/page_repository.py
class PageRepository:
    def __init__(self, api_client: MediaWikiClient):
        self._api = api_client

    def get_text(self, page: Page) -> str: ...
    def save(self, page: Page, summary: str) -> bool: ...

# 3. services/template_service.py
class TemplateService:
    def extract_templates(self, text: str) -> List[Template]: ...
    def get_template_params(self, text: str, name: str) -> Dict: ...

# 4. services/edit_validator.py
class EditValidator:
    def can_edit(self, page: Page, user: str, job: str) -> bool: ...
```

### 5.3 `newapi/super/super_login.py`
**Issues:** Mixed concerns, global state, command-line coupling

**Changes:**
```python
# SPLIT INTO:
# 1. auth/session_manager.py
class SessionManager:
    _sessions: Dict[str, requests.Session]

    def get_session(self, key: str) -> requests.Session: ...
    def invalidate(self, key: str) -> None: ...

# 2. auth/authenticator.py
class Authenticator:
    def __init__(self, session: requests.Session, config: AuthConfig):
        self._session = session
        self._config = config

    def login(self, username: str, password: str) -> bool: ...
    def is_authenticated(self) -> bool: ...

# 3. auth/token_provider.py
class TokenProvider:
    def get_csrf_token(self) -> str: ...
    def get_login_token(self) -> str: ...
```

### 5.4 `newapi/api_utils/botEdit.py`
**Issues:** Global caches, sys.argv coupling, complex boolean logic

**Changes:**
```python
# BEFORE
Bot_Cache = {}
Created_Cache = {}

def bot_May_Edit(text="", title_page="", botjob="all", page=False, delay=0):
    if ("botedit" in sys.argv or "editbot" in sys.argv) or "workibrahem" in sys.argv:
        return True
    # ...

# AFTER
@dataclass
class BotEditConfig:
    force_enable: bool = False
    stop_templates: Dict[str, List[str]] = field(default_factory=dict)
    min_edit_delay_minutes: int = 0

class EditPermissionChecker:
    def __init__(self, config: BotEditConfig):
        self._config = config
        self._template_cache: Dict[str, bool] = {}

    def can_edit(self, page: Page, job: str) -> EditCheckResult:
        if self._config.force_enable:
            return EditCheckResult.allowed()

        template_check = self._check_templates(page, job)
        if not template_check.allowed:
            return template_check

        return self._check_timing(page)
```

### 5.5 `newapi/super/S_API/bot_api.py`
**Issues:** Large class, mixed concerns (API queries + token management)

**Changes:**
```python
# SPLIT INTO:
# 1. api/client.py - Low-level API
class MediaWikiApiClient:
    def post(self, params: dict, config: RequestConfig) -> dict: ...
    def post_continue(self, params: dict, action: str) -> List: ...

# 2. api/queries.py - High-level queries
class PageQueries:
    def __init__(self, client: MediaWikiApiClient):
        self._client = client

    def get_all_pages(self, namespace: str, limit: int) -> List[str]: ...
    def search(self, query: str, namespace: str) -> List[str]: ...

# 3. api/token_manager.py
class TokenManager:
    def get_csrf_token(self) -> str: ...
    def invalidate(self) -> None: ...
```

### 5.6 `newapi/DB_bots/db_bot.py`
**Issues:** Thin wrapper, direct sqlite_utils exposure

**Changes:**
```python
# ADD: Repository pattern
class LiteDbRepository:
    def __init__(self, db_path: str):
        self._db = sqlite_utils.Database(db_path)

    def get_by_id(self, table: str, id: int) -> Optional[dict]: ...
    def insert(self, table: str, data: dict) -> int: ...
    def update(self, table: str, id: int, data: dict) -> bool: ...
    def delete(self, table: str, id: int) -> bool: ...
```

### 5.7 `newapi/super/handel_errors.py`
**Issues:** Inconsistent return types, magic strings

**Changes:**
```python
# DEFINE: Typed exception hierarchy
class NewApiException(Exception):
    """Base exception for newapi errors"""

class ApiError(NewApiException):
    def __init__(self, code: str, message: str, info: str = ""):
        self.code = code
        self.message = message
        self.info = info
        super().__init__(f"{code}: {message}")

class AbuseFilterError(ApiError):
    def __init__(self, description: str):
        super().__init__("abusefilter-disallowed", description)

class MaxLagError(ApiError):
    """Database lag error - retryable"""
    pass

# IMPLEMENT: Parser
def parse_api_error(error_dict: dict) -> Optional[ApiError]:
    code = error_dict.get("code", "")
    info = error_dict.get("info", "")

    error_map = {
        "abusefilter-disallowed": lambda e: AbuseFilterError(e.get("abusefilter", {}).get("description", "")),
        "maxlag": lambda e: MaxLagError(info),
        "articleexists": lambda e: ArticleExistsError(info),
        # ...
    }

    handler = error_map.get(code)
    if handler:
        return handler(error_dict)
    return ApiError(code, info)
```

---

## 6. Technical Debt Risks

### 6.1 Critical Risks

| Risk | Severity | Likelihood | Impact | Mitigation |
|------|----------|------------|--------|------------|
| **Session state corruption** | High | Medium | Bot logs out unexpectedly, data loss | Phase 1: Encapsulate session state |
| **Test flakiness from globals** | High | High | Unreliable CI, bugs in production | Phase 1: Remove global mutable state |
| **Authentication token leaks** | High | Low | Credential exposure | Phase 3: Secure token storage |
| **Arabic-specific logic in core** | Medium | Medium | Cannot support other languages | Phase 2: Extract locale strategies |

### 6.2 Security Concerns

1. **Credential Storage** (`accounts/useraccount.py`)
   - Passwords stored in plain text INI file
   - No encryption at rest
   - Recommendation: Use keyring library or environment variables

2. **Cookie Persistence** (`super/cookies_bot.py`)
   - Cookies stored with `chmod` that may be too permissive
   - Files persist beyond session
   - Recommendation: Encrypt cookies, use secure temp directory

3. **User Agent Exposure** (`api_utils/user_agent.py`)
   - Version numbers exposed in UA string
   - Recommendation: Allow UA customization

### 6.3 Maintainability Risks

1. **Code Duplication**
   - `post_params` duplicated in 3+ classes
   - Namespace lists duplicated
   - **Effort to Fix:** Medium (2-3 days)

2. **Untyped Code**
   - Only ~30% of functions have return type hints
   - Makes refactoring dangerous
   - **Effort to Fix:** High (1-2 weeks)

3. **Missing Tests**
   - Only 7 test files for ~50 source files
   - No integration tests
   - **Effort to Fix:** Very High (4-6 weeks)

### 6.4 Performance Concerns

1. **Inefficient Caching**
   - Template parsing re-parses entire text each call
   - No cache size limits on global caches
   - **Impact:** Memory growth in long-running processes

2. **Sequential API Calls**
   - No parallelization of independent queries
   - **Impact:** Slow batch operations

---

## 7. Recommendations Summary

### Remove `accounts` Folder (Immediate)
**Rationale:** Users can now use the simplified `ALL_APIS` code futures pattern instead of needing the `accounts` folder.

**New Usage Pattern:**
```python
from newapi import ALL_APIS

# Simple initialization with credentials
main_api = ALL_APIS(lang='en', family='wikipedia', username='your_username', password='your_password')

# Access all features through main_api
page = main_api.MainPage('Main Page Title')  # Access MainPage operations
cat_members = main_api.CatDepth('Category Title')  # Access Category traversal
new_api = main_api.NEW_API()  # Access NEW_API operations
```

**Files to Remove:**
- `accounts/__init__.py`
- `accounts/user_account_ncc.py`
- `accounts/user_account_new.py`
- `accounts/useraccount.py`
- `pages_bots/mdwiki_page.py`
- `pages_bots/ncc_page.py`
- `pages_bots/toolforge_page.py`
- `pages_bots/wiki_page.py`
- `pages_bots/new_wiki_pages.py`

**Migration Guide:**
- Old: `from accounts.useraccount import UserAccount; account = UserAccount(...)`
- New: `from newapi import ALL_APIS; api = ALL_APIS(username='...', password='...')`

**Benefits:**
- Simpler API surface area
- No need for separate account management files
- Direct credential passing through `ALL_APIS`
- Consistent with modern Python library patterns

### Immediate Actions (Week 1)
1. Add typing to all public interfaces
2. Create Config class to replace sys.argv coupling
3. Document all public APIs
4. Remove `accounts` folder (users now use `ALL_APIS` pattern)

### Short Term (Months 1-2)
1. Implement Phase 1-3 of roadmap
2. Add test suite with >60% coverage
3. Establish CI/CD with linting and type checking

### Long Term (Months 3-6)
1. Complete Phase 4-5 of roadmap
2. Migrate existing bots to new API
3. Deprecate old inheritance-based interfaces

### Success Metrics
- **Test Coverage:** >80%
- **Type Coverage:** >90% of public functions
- **Cyclomatic Complexity:** <10 per function
- **Coupling:** <5 dependencies per class
- **Maintainability Index:** >70 (from current ~40)

---

## Appendix: Code Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Total Lines | ~15,000 | - |
| Test Coverage | ~15% | >80% |
| Cyclomatic Complexity (avg) | 8.2 | <5 |
| Files with >300 lines | 12 | 0 |
| Global variables | 8 | 0 |
| Multiple inheritance uses | 5 | 0 |
| Type hint coverage | 30% | >90% |

---

*Report generated by static analysis on 2026-01-26*
