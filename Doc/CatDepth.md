
# CatDepth
The CategoryDepth system provides functionality for traversing MediaWiki categories and retrieving category members recursively. It allows users to retrieve pages within categories, including subcategories up to a specified depth, with powerful filtering options based on namespace, templates, language links, and other criteria.


## Basic usage:
```` python
from newapi.page import CatDepth

results = CatDepth(
    title="Example Category",
    sitecode="en",
    family="wikipedia",
    depth=1,
    ns="all"
)
cat_members = CatDepth("Category title", sitecode='en', family="wikipedia", depth=0, ns="all", nslist=[], tempyes=[])

````
## Advanced Usage Scenarios
### Template Filtering

Filter pages by the presence of specific templates:

```` python
# Get pages using the "Infobox scientist" template
results = CatDepth("Physicists", tempyes=["Template:Infobox scientist"])
````

### Namespace Filtering

The system can filter results by namespace in several ways:

```` python
# Get only articles (namespace 0) in the category
articles = CatDepth("Example Category", ns="0")

# Get only subcategories (namespace 14)
subcategories = CatDepth("Example Category", ns="14")

# Get only pages from specific namespaces
pages = CatDepth("Example Category", nslist=[0, 10])  # Articles and templates

````

### Language Link Filtering
Filter pages based on interlanguage links:

```` python
# Only pages with French language links
pages = CatDepth("Example Category", with_lang="fr")

# Exclude pages with Spanish language links
pages = CatDepth("Example Category", without_lang="es")
````

### Deep Category Traversal

```` python
# Get all pages in the category and 2 levels of subcategories
all_pages = CatDepth("Example Category", depth=2)

````

### Getting Only Page Titles

```` python
# Get just the titles, without metadata
titles = CatDepth(
    "Python libraries",
    only_titles=True,
    sitecode="en",
    family="wikipedia"
)

````

### Result Format
The results are returned as a dictionary where:
- Keys are page titles
- Values are dictionaries containing metadata about each page

Example result structure:

```` json
{
    "Page Title 1": {
        "ns": 0,                             # Namespace number
        "revid": 12345678,                   # Latest revision ID
        "templates": ["Template:Example1"],  # Templates used (if requested)
        "langlinks": {"fr": "Titre français"} # Language links (if requested)
    },
    "Page Title 2": {
        "ns": 14,
        "revid": 87654321
    }
}
````


# Advanced Usage Examples

## Example 1: Recursive Category Traversal
To retrieve all pages within a category and its subcategories (and their subcategories), use the depth parameter:

```` python
# Get category members up to 2 levels deep
football_categories = CatDepth(
    "Association football players by nationality",
    sitecode="en",
    family="wikipedia",
    depth=2,  # Include subcategories and their subcategories
    ns="all"
)
````

## Example 2: Filtering by Namespace
To retrieve only pages or only subcategories:
```` python
# Get only the subcategories
subcategories = CatDepth(
    "Association football players by nationality",
    sitecode="en",
    family="wikipedia",
    depth=0,
    ns="14"  # Category namespace
)

# Get only articles (main namespace)
articles = CatDepth(
    "Association football players by nationality",
    sitecode="en",
    family="wikipedia",
    depth=1,
    ns="0"  # Main/article namespace
)
````

## Example 3: Filtering by Template Usage
To retrieve only pages that use certain templates:
```` python
# Get pages that use the "Infobox football biography" template
footballer_pages = CatDepth(
    "Association football players by nationality",
    sitecode="en",
    family="wikipedia",
    depth=1,
    tempyes=["Template:Infobox football biography"]
)
````

## Example 4: Cross-Language Filtering
To filter pages based on whether they have certain language links:
```` python
# Get only pages that have a French equivalent
with_french = CatDepth(
    "Association football players by nationality",
    sitecode="en",
    family="wikipedia",
    depth=1,
    with_lang="fr"  # Only pages with French language links
)

# Get pages that don't have a Spanish equivalent
without_spanish = CatDepth(
    "Association football players by nationality",
    sitecode="en",
    family="wikipedia",
    depth=1,
    without_lang="es"  # Only pages without Spanish language links
)
````

## Example 5: Limiting Results
To limit the number of results returned:
```` python
# Get at most 100 results
limited_results = CatDepth(
    "Association football players by nationality",
    sitecode="en",
    family="wikipedia",
    depth=1,
    limit=100  # Return at most 100 results
)
````
