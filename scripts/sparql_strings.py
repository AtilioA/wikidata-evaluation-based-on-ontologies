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

SUBCLASSOF_GET_ENTITIES_BETWEEN_SPARQL = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?entity
WHERE
{{
    wd:{subclass} wdt:P279+ ?entity .
    ?entity wdt:P279* wd:{superclass}
}}
"""

CHECK_SUBCLASS_SPARQL = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT *
WHERE
{{
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass ) .
}}
"""


def create_subclass_sparql_string(entity, subclasses, transitive=True):
    # Create query string to check if one or more subclasses are subclasses of an entity

    CHECK_SUBCLASS_SPARQL = """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT *
    WHERE
    {
    """
    if transitive:
        P279Property = "P279+"
    else:
        P279Property = "P279"
    
    if isinstance(subclasses, str):
        CHECK_SUBCLASS_SPARQL += f"    BIND( EXISTS {{ wd:{subclasses} wdt:{P279Property} wd:{entity} . }} as ?isSubclass0 ) .\n"
    else:
        for i, subclass in enumerate(subclasses):
            CHECK_SUBCLASS_SPARQL += f"    BIND( EXISTS {{ wd:{subclass} wdt:{P279Property} wd:{entity} . }} as ?isSubclass{i} ) .\n"
            
    CHECK_SUBCLASS_SPARQL += "}"

    return CHECK_SUBCLASS_SPARQL


def create_subclasses_sparql_string(superclass, subclasses):
    # Create query string to check for subclasses between a superclass and one or more subclasses

    if isinstance(subclasses, str):
        query_string = SUBCLASSOF_GET_ENTITIES_BETWEEN_SPARQL.format(
            subclass=subclasses, superclass=superclass
        )
    else:
        query_string = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>

        SELECT *
        WHERE
        {
        """
        for i, subclass in enumerate(subclasses):
            query_string += f"wd:{subclass} wdt:P279+ ?entity{i} .\n?entity{i} wdt:P279* wd:{superclass} .\n"
        query_string += "}"

    return query_string
