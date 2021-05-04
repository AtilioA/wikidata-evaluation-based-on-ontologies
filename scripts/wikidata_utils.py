import random
import re
import subprocess
import ast
import sys
from pprint import pprint
import sparql_strings

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/"


def regex_match_QID(entitiesList):
    # Matches QIDs in a list of strings

    regex_pattern = re.compile(".*?(Q\d+)")

    parsedQIDList = [
        match.group(1)
        for match in (regex_pattern.match(entity) for entity in entitiesList)
        if match
    ]

    return parsedQIDList


def is_instanceof_Q23958852(entity, instancesof_Q23958852_FILE):
    # Check if entity is instance of Q23958852 based on a list of instances of Q23958852

    # Open file with instances of Q23958852 and adjust strings for comparison
    with open(instancesof_Q23958852_FILE, "r", encoding="utf-8") as fAP1P:
        instancesOfQ23958852 = fAP1P.readlines()
        instancesOfQ23958852 = list(
            map(lambda line: line.strip(), instancesOfQ23958852)
        )

    # Remove Wikidata URL
    entity = remove_prefix(entity, WIKIDATA_ENTITY_PREFIX)
    # Remove wd: entity prefix
    entity = remove_prefix(entity, 'wd:')

    # print(entity, entity in instancesOfQ23958852)

    return (entity in instancesOfQ23958852)


def remove_instances_Q23958852(entitiesList, instancesof_Q23958852_FILE):
    # Remove Q23958852 instances from a list of entities

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
    print("# of entities before removing instances of Q23958852:", len(entitiesList))
    entitiesList = [
        entity for entity in entitiesList if entity not in instancesOfQ23958852
    ]
    print("# of entities after removing instances of Q23958852: ", len(entitiesList))

    return entitiesList


def get_entity_label(entity):
    # Get label for an entity

    query = query_label_stardog(entity)
    try:
        return query["results"]["bindings"][0]["subjectLabel"]["value"]
    except IndexError:
        return "Label unavailable"


def query_label_stardog(entity):
    # Query stardog for an entity's label

    query_string = sparql_strings.GET_LABEL_SPARQL.format(entity=entity)
    query = subprocess.run(
        ["stardog", "query", "-f", "json", "WD_749", query_string],
        capture_output=True,
        text=True,
    )

    return ast.literal_eval(query.stdout)


def query_subclass_stardog(entity, subclasses, transitive=True):
    # Query to check if one or more subclasses are subclasses of an entity

    CHECK_SUBCLASS_SPARQL = sparql_strings.create_subclass_sparql_string(
        entity, subclasses, transitive
    )

    query_string = CHECK_SUBCLASS_SPARQL
    query = subprocess.run(
        ["stardog", "query", "-f", "json", "WD_749", query_string],
        capture_output=True,
        text=True,
    )

    return ast.literal_eval(query.stdout)


def query_subclasses_stardog(superclass, subclass):
    # Query to check for subclasses between a superclass and one subclass

    query_string = sparql_strings.create_subclasses_sparql_string(superclass, subclass)

    query = subprocess.run(
        ["stardog", "query", "-f", "json", "WD_749", query_string],
        capture_output=True,
        text=True,
    )

    return ast.literal_eval(query.stdout)


def create_subclasses_sparql_string(subclass, superclass):
    # Create query string to check for subclasses between a superclass and one or more subclasses

    if isinstance(subclasses, str):
        query_string = SUBCLASSOF_GET_ENTITIES_BETWEEN_SPARQL.format(
            subclass=subclass, superclass=superclass
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


def parse_lo_hi():
    # Parse lo and hi arguments from argv

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
    # Remove a prefix from a string

    if str.startswith(prefix):
        return str[len(prefix) :]
    else:
        return str


def add_prefix_wd(str):
    # Add wd: prefix to a string

    return f"wd:{str}"


def random_color_hex():
    colors = []
    rgb = ""
    
    while sum(colors) > 660 or rgb == "":
        colors = []
        rgb = ""
        for _ in "RGB":
            colors.append(random.randrange(0, 2 ** 8))
            rgb += colors[-1].to_bytes(1, "big").hex()
            
    return f"#{rgb}"


def find_occurrences_entity(entity, resultsJson):
    occurrences = {
        "superclasses": [],
        "subclasses": [],
    }

    for result in resultsJson:
        if entity in result["subject"]:
            occurrences["superclasses"].append(
                {"object": result["object"], "objectLabel": ""}
            )
        elif entity in result["object"]:
            occurrences["subclasses"].append(
                {"subject": result["subject"], "subjectLabel": result["subjectLabel"]}
            )

    return occurrences


def improve_AP1_json_file(resultsPath="../queries/results/AP1P.json"):
    with open(Path(resultsPath), "r", encoding="utf8") as fAP1:
        resultsJson = json.load(fAP1)["results"]["bindings"][:5000000]
        regex_pattern = re.compile(".*?(Q\d+)")

        for i, result in enumerate(resultsJson):
            resultsJson[i]["object"] = re.search(
                regex_pattern, resultsJson[i]["object"]["value"]
            ).group(1)
            resultsJson[i]["subject"] = re.search(
                regex_pattern, resultsJson[i]["subject"]["value"]
            ).group(1)
            try:
                resultsJson[i]["subjectLabel"] = resultsJson[i]["subjectLabel"]["value"]
            except:
                resultsJson[i]["subjectLabel"] = "Label unavailable"
        with open("../queries/results/AP1P_light.json", "w+", encoding="utf8") as fAP1L:
            json.dump(resultsJson, fAP1L)
    return resultsJson


def read_AP1_results(entitiesSet, resultsPath="../queries/results/AP1P_light.json"):
    try:
        with open(Path(resultsPath), "r", encoding="utf8") as fAP1:
            resultsJson = json.load(fAP1)
    except FileNotFoundError:
        resultsJson = improve_AP1_json_file(resultsPath="../queries/results/AP1P.json")

    print(len(entitiesSet))
    entitiesOccurrences = {}
    for i, entity in enumerate(list(entitiesSet)):
        entitiesOccurrences[entity] = find_occurrences_entity(entity, resultsJson)
        print(i)
    with open("output/AP1_ranking_entities.json", "w+", encoding="utf8") as fOccurrence:
        json.dump(entitiesOccurrences, fOccurrence)
