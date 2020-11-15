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

CHECK_SUBCLASS_SPARQL = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT *
WHERE
{{
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass1 ) .
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass2 ) .
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass3 ) .
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass4 ) .
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass5 ) .
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass6 ) .
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass7 ) .
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass8 ) .
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass9 ) .
  BIND( EXISTS {{ wd:{subclass} wdt:P279+ wd:{class_} . }} as ?isSubclass10 ) .
}}
"""
