import subprocess
import ast
import sys

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/"
GET_LABEL_SPARQL = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subjectLabel
WHERE
{{
    wd:{entity} rdfs:label ?subjectLabel .
    FILTER (lang(?subjectLabel) = "" || lang(?subjectLabel) = "en") .
}}
"""


def remove_instances_Q23958852(entitiesList, instancesof_Q23958852_FILE):
    # Open file with instances of Q23958852 and adjust strings for comparison
    with open(instancesof_Q23958852_FILE, "r", encoding="utf-8") as fAP1P:
        instancesOfQ23958852 = fAP1P.readlines()
        instancesOfQ23958852 = list(
            map(lambda line: line.strip(), instancesOfQ23958852)
        )

    entitiesList = list(
        map(lambda x: remove_prefix(x, WIKIDATA_ENTITY_PREFIX), entitiesList)
    )
    entitiesList = list(map(lambda x: remove_prefix(x, "wd:"), entitiesList))

    # Remove instances of Q23958852 from entities list
    print("Before removing Q23958852:", len(entitiesList))
    entitiesList = [
        entity for entity in entitiesList if entity not in instancesOfQ23958852
    ]
    print("After removing Q23958852: ", len(entitiesList))

    return entitiesList


def get_entity_label(entity):
    query = query_stardog(entity)
    return query["results"]["bindings"][0]["subjectLabel"]["value"]


def query_stardog(entity):
    query_string = GET_LABEL_SPARQL.format(entity=entity)
    query = subprocess.run(
        ["stardog", "query", "-f", "json", "WD_749", query_string],
        capture_output=True,
        text=True,
    )
    return ast.literal_eval(query.stdout)


def parse_argv():
    try:
        lo = int(sys.argv[1])
    except IndexError:
        lo = 0
    try:
        hi = int(sys.argv[2])
    except IndexError:
        hi = 20

    return (lo, hi)


def remove_prefix(str, prefix):
    if str.startswith(prefix):
        return str[len(prefix) :]
    else:
        return str


def add_prefix_wd(str):
    return f"wd:{str}"
