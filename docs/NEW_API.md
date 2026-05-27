## NEW_API

The NEW_API class provides a robust, high-level interface to the MediaWiki API, abstracting away the complexities of direct API interaction. By providing methods for common operations like searching, retrieving pages, working with templates, and handling user contributions, it enables developers to create sophisticated tools and bots for MediaWiki platforms with minimal code.

### list of pages

```` python
from newapi import ALL_APIS

# Initialize API with language and family
api = ALL_APIS(lang='en', family='wikipedia')
api_new = api.NEW_API()

# get list of pages:
# pages_info = api_new.Get_All_pages_generator(start="A", namespace="0", limit="max")
# pages    = api_new.Get_All_pages(start='', namespace="0", limit="max", apfilterredir='', limit_all=0)

# Get up to 5000 contributions from User:Example in all namespaces
contribs = api_new.UserContribs("User:Example", limit=5000, namespace="*", ucshow="")

# Find pages with titles starting with "Python"
results = api_new.PrefixSearch("Python", ns="0", pslimit="max")

newpages = api_new.Get_Newpages(limit="max", namespace="0", rcstart="", user='', three_houers=False)

# Process each page
for title in newpages:
    page = api.MainPage(title)

    # Skip redirects and non-existent pages
    if not page.exists() or page.isRedirect():
        continue

    # Get page content
    text = page.get_text()

    # Process the page as needed
    # ...

````
### Search

```` python
results = api_new.Search(value="solar system", ns="0", srlimit="10", RETURN_dict=False, addparams={})

# Results will be a list of page titles matching the search query
for title in results:
    print(title)

````

### Find_pages_exists_or_not
```` python
# Check if multiple pages exist
pages_to_check = ["Earth", "Mars", "NonExistentPage123"]
existence_info = api_new.Find_pages_exists_or_not(pages_to_check)

# existence_info will be a dictionary mapping titles to boolean values
for title, exists in existence_info.items():
    status = "exists" if exists else "does not exist"
    print(f"Page '{title}' {status}")
````

### move

```` python
# Move a page (requires appropriate permissions)
result = api_new.move(
    old_title="Draft:MyArticle",
    to="MyArticle",
    reason="Article ready for mainspace",
    noredirect=False
)

if result is True:
    print("Move successful")
else:
    print(f"Move failed: {result}")

````
### Other funcations:

```` python
# Get information about users
info = api_new.users_infos(ususers=["User1", "User2"])

# Get all pages using Template:Infobox
pages = api_new.Get_template_pages("Template:Infobox", namespace="*", Max=10000)

# Get German equivalents for English pages
lang_links = api_new.Get_langlinks_for_list(["Page1", "Page2"], targtsitecode="de")

# Get wanted categories
wanted = api_new.querypage_list(qppage="Wantedcategories", qplimit="max")

# Get pages with unlinked Wikibase IDs
pages = api_new.pageswithprop(pwppropname="unlinkedwikibase_id", Max=10000)

l_links  = api_new.Get_langlinks_for_list(["Page1", "Page2"], targtsitecode="", numbes=50)
text_w   = api_new.expandtemplates("Template text")
subst    = api_new.Parse_Text('{{subst:page_name}}', "Page Title")
extlinks = api_new.get_extlinks("Page Title")
revisions= api_new.get_revisions("Page Title")
json1    = api_new.post_params({"action": "query"}, addtoken=False)

````

### Files
```` python

# Get detailed information about an image
info = api_new.Get_imageinfo("Example.jpg")

# Get URL for an image file
url = api_new.Get_image_url("Example.jpg")

# Uploading a File
result = api_new.upload_by_file(
    'Example.jpg',
    '{{Information|description=Example image}}',
    '/path/to/local/file.jpg',
    comment='Uploading example image'
)

````

### Adding Text to a Page without using MainPage
```` python
# added    = api_new.Add_To_Bottom(text, summary, title, poss="Head|Bottom")

result = api_new.Add_To_Bottom(
    '== New section ==\nSome new content.',
    'Adding new section',
    'Page Title'
)

````

