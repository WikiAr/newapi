# Wikimedia API Python Module

## Overview
This project is a Python module designed to interact with the Wikimedia API. It provides a unified, programmable interface for common Wikimedia actions such as:
- Logging in
- Retrieving and editing pages
- Working with categories and templates
- Performing various Wikimedia API actions

The module abstracts the Wikimedia API into user-friendly functions and classes, reducing the need for direct HTTP request handling and token management.

## Features
- **API Interface Layer**: Encapsulates core Wikimedia interactions, handling requests and responses.
- **Login Module**: Simplifies authentication with multiple bot-based login implementations.
- **Page Management Module**: Offers functionality to check page existence, edit pages, and manage page elements.
- **Category and Template Handling**: Supports category depth processing and template handling.
- **Bot Modules**: Automates API interactions and page operations.
- **MWClient Wrappers**: Provides lower-level API communication support.
- **Database & Utility Bots**: Manages database interactions and caching.
- **Testing & CI/CD Support**: Includes a test suite and GitHub workflows for automated validation.

## System Architecture
The project follows a modular and layered architecture:
1. **Client/Consumer Applications** interact with the module.
2. **API Interface Layer** (e.g., `NEW_API` class) abstracts direct Wikimedia API calls.
3. **Login Module** handles session authentication.
4. **Page Management Module** enables page retrieval, editing, and processing.
5. **Category and Template Handling** supports Wikimedia-specific structures.
6. **Bot Modules** automate repetitive Wikimedia tasks.
7. **MWClient Wrappers** facilitate low-level API interactions.
8. **Database & Utility Bots** provide storage and session support.
9. **Testing & CI/CD** ensures reliability through automated testing and configuration management.

## File Mapping
### API Interface Layer
- `wiki_page.py`, `page.py`, `mdwiki_page.py`, `ncc_page.py`
- `super/super_page.py`

### Login Module
- `super/super_login.py`
- `super/S_Login/` (including `bot.py`, `bot_new.py`, `cookies_bot.py`)

### Page Management Module
- `wiki_page.py`, `page.py`, `mdwiki_page.py`, `ncc_page.py`
- `super/super_page.py`

### Category and Template Handling
- `super/catdepth_new.py`

### Bot Modules
- API bots: `super/botapi_bots/`
- Page bots: `super/page_bots/`
- Additional bot utilities: `botEdit.py`, `super/bots/`

### MWClient Wrappers
- `super/S_Login/mwclient/` (including `client.py`, `page.py`, `errors.py`, `image.py`, `listing.py`, `sleep.py`, `util.py`)

### Database & Utility Bots
- `db_bot.py`, `pymysql_bot.py`

### Testing Suite
- `tests/` (e.g., `tests/test_bot_api.py`, `tests/test_db_bot.py`)

### CI/CD & Configuration
- `.github/` (GitHub workflows and issue templates)
- YAML configuration: `sweep.yaml`, `.coderabbit.yaml`
- Dependencies: `requirements.in`

## System Design Diagram Guidelines
To accurately visualize the architecture:
1. **Identify Main Components**: Include API layers, login, page management, bots, and utility modules.
2. **Map Relationships**:
   - Client → Login Module → MWClient Wrapper → API Interface → Page Management
   - Bots interact with API Interface and Page Management
3. **Use Layered Representation**:
   - High-level API components (NEW_API, MainPage)
   - Mid-level modules (bot handlers, database utilities)
   - Low-level API wrappers (MWClient interactions)
4. **Diagram Elements**:
   - Labeled boxes for components
   - Directional arrows to indicate data flow
   - Different colors for API layers, bots, and utility modules
   - Sub-diagrams for clusters like the `super` directory

## Installation & Usage
### Installation
```sh
pip install -r requirements.in
```

### Usage Example
```python
from newapi.page import MainPage

# Initialize API
page = MainPage("Example_Page")

# Check if the page exists
if page.exists():
    print("Page found!")

# Edit a page
page.edit("Updated content")
```

## Contribution
1. Fork the repository
2. Create a new branch
3. Make changes and commit
4. Submit a pull request

## License
This project is licensed under the MIT License.
