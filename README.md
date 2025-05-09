Python module for Wikimedia API:

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/WikiAr/newapi)

----
# Newapi.page Module:

## MainPage

The ````MainPage```` class is a core component of the newapi framework that provides a high-level interface for interacting with individual wiki pages across various MediaWiki sites. It encapsulates all operations related to reading, editing, and analyzing specific pages, abstracting away the complexity of direct API calls.

For general API operations that don't target specific pages, see NEW_API Class. For category-specific operations, see CatDepth.

See [Doc/MainPage.md](Doc/MainPage.md)

```` python
# Import MainPage
from newapi.page import MainPage

# Initialize with page title, language, and wiki family
page = MainPage("Earth", 'en', family='wikipedia')

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
The CategoryDepth system provides functionality for traversing MediaWiki categories and retrieving category members recursively. It allows users to retrieve pages within categories, including subcategories up to a specified depth, with powerful filtering options based on namespace, templates, language links, and other criteria.

See [Doc/CatDepth.md](Doc/CatDepth.md)

```` python
from newapi.page import CatDepth

# Get members of a category (default depth=0 means only direct members)
cat_members = CatDepth(
    "Living people",  # category name
    sitecode='en',    # language code
    family="wikipedia"  # wiki family
)

# Process the results
print(f"Found {len(cat_members)} members")
for title, info in cat_members.items():
    print(f"Title: {title}, NS: {info.get('ns')}")
````

## NEW_API
The NEW_API class provides a robust, high-level interface to the MediaWiki API, abstracting away the complexities of direct API interaction. By providing methods for common operations like searching, retrieving pages, working with templates, and handling user contributions, it enables developers to create sophisticated tools and bots for MediaWiki platforms with minimal code.

See [Doc/NEW_API.md](Doc/NEW_API.md)

```` python
from newapi.page import NEW_API

# Initialize the API
api_new = NEW_API('en', family='wikipedia')
api_new.Login_to_wiki()

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
# Newapi.pformat Module:
For complex edits involving templates, the framework includes utilities to format template syntax in a standard way:

```` python
from newapi import pformat

# Format templates in text
new_text = pformat.make_new_text(text)
````

# Newapi.wd_sparql Module:
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
# Newapi.db_bot Module:
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

# Newapi.pymysql_bot Module:
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
from newapi.page import NEW_API, MainPage

# Initialize API
api = NEW_API('en', family='wikipedia')
api.Login_to_wiki()

# Get uncategorized pages
uncategorized = api.querypage_list(qppage="Uncategorizedpages", qplimit="50")

# Process each page to add appropriate categories
for page_info in uncategorized:
    title = page_info.get("title")
    page = MainPage(title, 'en', family='wikipedia')

    if page.exists() and page.can_edit(script='categorizer'):
        # Get text and add categories based on content analysis
        text = page.get_text()
        # ... logic to determine appropriate categories ...
        new_text = text + "\n[[Category:Appropriate Category]]"
        page.save(newtext=new_text, summary="Added missing category")
````

## Updating Interlanguage Links
```` python
from newapi.page import NEW_API, MainPage, CatDepth

# Get pages in a category
category_members = CatDepth(
    "Articles needing interlanguage links",
    sitecode='en',
    family="wikipedia",
    ns="0"
)

# Initialize API for language link operations
api = NEW_API('en', family='wikipedia')
api.Login_to_wiki()

# Process each page
for title in category_members:
    page = MainPage(title, 'en', family='wikipedia')

    if page.exists():
        # Find potential language links through search on other wikis
        # This is a simplified example - real implementation would be more complex
        other_lang_api = NEW_API('es', family='wikipedia')
        other_lang_api.Login_to_wiki()

        search_results = other_lang_api.Search(value=title, ns="0", srlimit="1")
        if search_results:
            print(f"Possible match for {title}: {search_results[0]} (es)")
````

## Batch Processing Template Changes

```` python
from newapi.page import NEW_API, MainPage

# Initialize API
api = NEW_API('en', family='wikipedia')
api.Login_to_wiki()

# Get pages using a specific template
template_pages = api.Get_template_pages("Template:Outdated", namespace="0", Max=100)

# Process each page to update the template
for title in template_pages:
    page = MainPage(title, 'en', family='wikipedia')

    if page.exists() and page.can_edit(script='template-updater'):
        text = page.get_text()

        # Replace old template format with new format
        # For example, change {{outdated}} to {{update|date=January 2023}}
        new_text = text.replace("{{outdated}}", "{{update|date=January 2023}}")

        if new_text != text:
            page.save(newtext=new_text, summary="Updated outdated template to update template with date")
````
