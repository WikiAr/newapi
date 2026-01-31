Python module for Wikimedia API:

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/WikiAr/newapi)

----
# Usage

The recommended way to use the library is via the `ALL_APIS` class, which serves as the central entry point. It handles authentication, session management, and configuration for you.

```python
from newapi import ALL_APIS

# Initialize the API with your credentials
# This creates a session that will be used for all subsequent operations
api = ALL_APIS(
    lang='en',
    family='wikipedia',
    username='your_username',
    password='your_password'
)
```

# Core Components

## MainPage

The ````MainPage```` class is a core component of the newapi framework that provides a high-level interface for interacting with individual wiki pages. Use the `api` instance to create page objects.

For general API operations that don't target specific pages, see NEW_API. For category-specific operations, see CatDepth.

See [Doc/MainPage.md](Doc/MainPage.md)

```` python
# Create a MainPage instance using the initialized API
# Language and family are inherited from the api instance
page = api.MainPage("Earth")

# Check if the page exists
if page.exists():
    # Get the page content
    text = page.get_text()

    # Get metadata
    namespace = page.namespace()
    timestamp = page.get_timestamp()
    user = page.get_user()

    # Analyze page content
    categories = page.get_categories()
    templates = page.get_templates()
    links = page.page_links()
    word_count = page.get_words()

````

## CatDepth
The CategoryDepth system provides functionality for traversing MediaWiki categories and retrieving category members recursively.

See [Doc/CatDepth.md](Doc/CatDepth.md)

```` python
# Get members of a category using the api instance
cat_members = api.CatDepth("Living people")

# Process the results
print(f"Found {len(cat_members)} members")
for title, info in cat_members.items():
    print(f"Title: {title}, NS: {info.get('ns')}")
````

## NEW_API
The NEW_API class provides a robust, high-level interface to the MediaWiki API, abstracting away the complexities of direct API interaction.

See [Doc/NEW_API.md](Doc/NEW_API.md)

```` python
# Access the API interface via your initialized instance
api_new = api.NEW_API()

# Search for pages containing "python programming"
search_results = api_new.Search(value="python programming", ns="0", srlimit="10")

# Process the results
for title in search_results:
    print(f"Found page: {title}")

# Search with more options and return detailed results
detailed_results = api_new.Search(
    value="python programming",
    ns="0",
    srlimit="5",
    RETURN_dict=True,
    addparams={"srinfo": "totalhits"}
)

````

----
# newapi.wd_sparql Module:
See [Doc/wd_sparql.md](Doc/wd_sparql.md)

```` python
from newapi.wd_sparql import get_query_result

# Query for items with English label containing "python"
query = """
SELECT ?item ?itemLabel
WHERE {
    ?item rdfs:label ?label.
    FILTER(CONTAINS(LCASE(?label), "python") && LANG(?label) = "en")
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 10
"""

results = get_query_result(query)
for result in results:
    print(f"Item: {result['itemLabel']['value']}")
````
# newapi.db_bot Module:
The LiteDB class in db_bot.py provides a wrapper around SQLite operations, offering:

- Table creation and management
- Data insertion and querying
- Schema introspection
See [Doc/db_bot.md](Doc/db_bot.md)

```` python
from newapi.db_bot import LiteDB

# Initialize database
db = LiteDB("/path/to/database.db")

# Create table
db.create_table(
    "page_cache",
    {"id": int, "title": str, "content": str, "timestamp": str},
    pk="id"
)

# Insert data
db.insert("page_cache", {
    "title": "Example Page",
    "content": "Page content...",
    "timestamp": "2023-07-15T12:34:56Z"
})

# Query data
results = db.select("page_cache", {"title": "Example Page"})

````

# newapi.pymysql_bot Module:
The pymysql_bot module provides functions for connecting to MySQL databases and executing queries:

See [Doc/pymysql_bot.md](Doc/pymysql_bot.md)

```` python
from newapi import pymysql_bot

# Execute query
from newapi import pymysql_bot

# Simple query
results = pymysql_bot.sql_connect_pymysql(
    "SELECT * FROM wiki_pages WHERE page_id > %s",
    values=(1000,),
    credentials={
        "host": "localhost",
        "user": "username",
        "password": "password",
        "database": "wiki_db"
    }
)

# Query with dictionary results
dict_results = pymysql_bot.sql_connect_pymysql(
    "SELECT page_id, page_title FROM wiki_pages LIMIT 10",
    return_dict=True,
    credentials={
        "host": "localhost",
        "user": "username",
        "password": "password",
        "database": "wiki_db"
    }
)
````



# Combined Examples for Real-World Tasks

## Finding Uncategorized Articles
```` python
from newapi import ALL_APIS

# Initialize API
api = ALL_APIS(lang='en', family='wikipedia', username='user', password='pwd')

# Access NEW_API for queries
api_new = api.NEW_API()

# Get uncategorized pages
uncategorized = api_new.querypage_list(qppage="Uncategorizedpages", qplimit="50")

# Process each page to add appropriate categories
for page_info in uncategorized:
    title = page_info.get("title")
    # Create page object through main api instance
    page = api.MainPage(title)

    if page.exists() and page.can_edit(script='categorizer'):
        # Get text and add categories based on content analysis
        text = page.get_text()
        # ... logic to determine appropriate categories ...
        new_text = text + "\n[[Category:Appropriate Category]]"
        page.save(newtext=new_text, summary="Added missing category")
````

## Updating Interlanguage Links
```` python
from newapi import ALL_APIS

# Initialize API
api = ALL_APIS(lang='en', family='wikipedia', username='user', password='pwd')

# Get pages in a category
category_members = api.CatDepth("Articles needing interlanguage links", ns="0")

# Process each page
for title in category_members:
    page = api.MainPage(title)

    if page.exists():
        # Find potential language links through search on other wikis
        # Initialize another API instance for the target wiki
        other_lang_api = ALL_APIS(lang='es', family='wikipedia', username='user', password='pwd')
        api_es = other_lang_api.NEW_API()

        search_results = api_es.Search(value=title, ns="0", srlimit="1")
        if search_results:
            print(f"Possible match for {title}: {search_results[0]} (es)")
````

## Batch Processing Template Changes

```` python
from newapi import ALL_APIS

# Initialize API
api = ALL_APIS(lang='en', family='wikipedia', username='user', password='pwd')
api_new = api.NEW_API()

# Get pages using a specific template
template_pages = api_new.Get_template_pages("Template:Outdated", namespace="0", Max=100)

# Process each page to update the template
for title in template_pages:
    page = api.MainPage(title)

    if page.exists() and page.can_edit(script='template-updater'):
        text = page.get_text()

        # Replace old template format with new format
        # For example, change {{outdated}} to {{update|date=January 2023}}
        new_text = text.replace("{{outdated}}", "{{update|date=January 2023}}")

        if new_text != text:
            page.save(newtext=new_text, summary="Updated outdated template to update template with date")
````
