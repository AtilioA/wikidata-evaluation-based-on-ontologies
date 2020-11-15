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


def create_subclass_sparql_string(class_, subclasses):
    CHECK_SUBCLASS_SPARQL = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT *
    WHERE
    {
    """
    for i, subclass in enumerate(subclasses):
        CHECK_SUBCLASS_SPARQL += f"    BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass{i} ) .\n"
    CHECK_SUBCLASS_SPARQL += "}"

    return CHECK_SUBCLASS_SPARQL


CHECK_SUBCLASS_SPARQL = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT *
WHERE
{{
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass ) .
}}
"""
