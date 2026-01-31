"""

from newapi.api_utils import wd_sparql

get_query_result = wd_sparql.get_query_result
get_query_data = wd_sparql.get_query_data

"""

import logging
import sys

from SPARQLWrapper import JSON, SPARQLWrapper

logger = logging.getLogger(__name__)


def get_query_data(query):
    """Retrieve query data from the Wikidata SPARQL endpoint.

    This function sends a SPARQL query to the Wikidata endpoint and
    retrieves the results in JSON format. It constructs a user agent string
    based on the Python version and uses the SPARQLWrapper library to handle
    the query execution. If an error occurs during the query process, it
    logs the exception for debugging purposes.

    Args:
        query (str): A SPARQL query string to be executed against the
            Wikidata database.

    Returns:
        dict: The data retrieved from the SPARQL query, formatted as a
            dictionary.
    """
    # TODO: https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/WDQS_graph_split/Rules#Scholarly_Articles

    # endpoint_url = "https://query-main.wikidata.org/sparql"
    endpoint_url = "https://query.wikidata.org/sparql"
    # ---
    user_agent = "WDQS-example Python/%s.%s" % (
        sys.version_info[0],
        sys.version_info[1],
    )
    # ---
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    # ---
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # ---
    data = {}
    # ---
    try:
        data = sparql.query().convert()
    except Exception as e:
        logger.error(f"API/tools.py get_query_data: Exception: {e}")
    # ---
    return data


def get_query_result(query):
    # ---
    data = get_query_data(query)
    # ---
    lista = [x for x in data.get("results", {}).get("bindings", [])]
    # ---
    return lista
