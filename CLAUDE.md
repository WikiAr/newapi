# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python library for automated bot operations on MediaWiki projects (Wikipedia, Wikidata). Provides authenticated API access, page reading/editing/creation, recursive category traversal, Wikidata SPARQL queries, and local database storage via SQLite and MySQL. Used as a dependency by other bot repositories in this ecosystem.

## Commands

### Run Tests

```bash
pytest                                    # All tests (network disabled by default)
pytest -m unit                            # Unit tests only
pytest -m network                         # Network-dependent tests
pytest -k "test_name"                     # Single test by name
pytest --cov=newapi --cov-report=term-missing --cov-branch  # With coverage
```

`pytest.ini` sets `pythonpath = newapi`, `testpaths = tests`, `--maxfail=25`, `--durations=10`, `--strict-markers`. Network tests excluded by default via `-m "not network"`.

The `conftest.py` autouse fixture disables all network sockets via `pytest-socket`.

### Lint & Format

```bash
ruff check .              # Lint
ruff check --fix .        # Lint with auto-fix
ruff format .             # Format
black .                   # Format (alternative)
isort .                   # Sort imports
mypy .                    # Type check
```

Line length is 120 across all tools. Target Python 3.13.

### Install Dependencies

```bash
pip install -r requirements.in       # Runtime
pip install -r requirements-dev.txt  # Testing
```

Runtime: `PyMySQL`, `Requests`, `sqlite_utils`, `tqdm`, `wikitextparser`, `mwclient`, `ratelimiter`, `SPARQLWrapper`, `colorlog`, `python-dotenv`, `pywikibot`.
Dev: `pytest`, `pytest-cov`, `pytest-mock`, `pytest-socket`.

## Architecture

Three-layer architecture:

```
Layer 1: Transport + Auth (newapi/api_client/)
  RequestsHandler (retry/CSRF/maxlag) -> WikiLoginClient (auth, cookies, pagination)
  Exceptions: WikiClientError -> LoginError, CSRFError, MaxlagError, MaxRetriesExceeded, CookieError

Layer 2: Wiki Business Logic (newapi/client_wiki/)
  AllAPIS (main facade) -> MainPage (page ops), CategoryDepth (recursive traversal), NewApi (bulk ops)
  api_utils/: AskBot, HandleErrors, botEdit, txtlib, wd_sparql, lang_codes

Layer 3: High-Level Operations (newapi/super/S_API/bot_api.py)
  NewApi class: 30+ methods (search, listing, contributions, upload, move, langlinks, etc.)
```

### Key Abstractions

- **`AllAPIS`** (`client_wiki/all_apis.py`) -- Main facade. `AllAPIS(lang, family, username, password)` creates authenticated client. Methods: `.MainPage(title)`, `.CatDepth(category)`, `.NewApi()`.
- **`WikiLoginClient`** (`api_client/client.py`) -- Authenticated HTTP client wrapping `mwclient.Site`. Handles CSRF tokens, maxlag backoff, session recovery, cookie persistence.
- **`MainPage`** (`client_wiki/pages/super_page.py`) -- Page-level operations: read, edit, create, get categories/templates/links, check editability. Inherits `HandleErrors` and `AskBot`.
- **`CategoryDepth`** (`client_wiki/categories/category_db.py`) -- Recursive category member retrieval with depth, namespace, template, and language-link filtering.
- **`NewApi`** (`super/S_API/bot_api.py`) -- 30+ high-level operations delegating to `WikiLoginClient`.
- **`Settings`** (`config.py`) -- Dataclass singleton loaded from env vars. Sections: `WikidataConfig`, `ApiClientConfig`, `DatabaseConfig`, `DebugConfig`, `BotConfig`, `QueryConfig`, `SiteConfig`.

### Usage Pattern

```python
from newapi import AllAPIS

api = AllAPIS(lang='en', family='wikipedia', username='user', password='pass')
page = api.MainPage("Article Title")
text = page.get_text()
page.save(newtext, summary="Edit summary")
```

Legacy convenience (deprecated):
```python
from newapi.page import load_main_api
api = load_main_api("en", "wikipedia")
```

### Cookie Management

Sessions persisted as Mozilla-format cookie jar files. Auto-expire after 3 days. Path: `{cookies_dir}/{family}_{lang}_{username}.mozilla`. `COOKIES_DIR` env var or defaults to `~/tmp/cookies`.

### Error Handling

Two parallel exception hierarchies:
1. `api_client/exceptions.py`: `WikiClientError` -> `LoginError`, `CSRFError`, `MaxlagError`, `MaxRetriesExceeded`, `CookieError`
2. `core/exceptions.py`: `NewApiException` -> `ApiError` -> `AbuseFilterError`, `MaxLagError`, `ArticleExistsError`, `ProtectedPageError`, etc. Includes `parse_api_error()` for mapping API error dicts.

### Patterns to Know

- **`{1: value}` mutable dict pattern** -- used for module-level mutable state.
- **Module-level side effects** -- importing modules can trigger login, computation, or sys.argv modification.
- **Mixed naming conventions** -- PascalCase classes, snake_case functions, some camelCase mixed in.
- **Mixed Arabic/English** in comments and string literals.

## Environment

Credentials from environment variables:
- `WIKIPEDIA_BOT_USERNAME` / `WIKIPEDIA_BOT_PASSWORD` -- primary bot account
- `WIKIPEDIA_HIMO_USERNAME` / `WIKIPEDIA_HIMO_PASSWORD` -- alternate account (when `workibrahem` setting active)

## CI/CD

- **Tests**: GitHub Actions (`pytest.yaml`) runs `pytest` on PRs to `main` (Python 3.11 in CI, 3.13 locally).
- **Publish**: `python-publish.yml` for PyPI releases.
