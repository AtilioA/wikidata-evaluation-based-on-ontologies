import json
import re
import sys
import json
import distutils.util
from pathlib import Path
from pprint import pprint
from functools import partial
from itertools import zip_longest

import wikidata_utils
from graphviz import Digraph


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


def graph_from_superclasses_dict(superclassesDictFilename):
    with open(Path(superclassesDictFilename), "r+", encoding="utf8") as dictFile:
        entitiesDict = json.load(dictFile)
    # Filter out entities without any subclasses in the ranking
    entitiesDict = dict(
        filter(
            lambda x: x[1]["subclasses"] != [] or x[1]["subclasses"] == x[1],
            entitiesDict.items(),
        )
    )
    print(len(entitiesDict))

    dots = []
    for entity in entitiesDict.items():
        entityLabel = wikidata_utils.get_entity_label(entity[0])
        print(f"Building graph for {entity[0]} ({entityLabel})")

        dot = Digraph(comment=entityLabel)

        print(entity[1]["subclasses"])
        for subclass in entity[1]["subclasses"]:
            subclassLabel = wikidata_utils.get_entity_label(subclass)

            # If label is unavailable, use ID
            if subclassLabel != "Label unavailable":
                dot.node(subclass, f"{subclassLabel}\n{subclass}")
            else:
                dot.node(subclass, subclass)

            dot.edge(f"{entityLabel}\n{entity[0]}", subclass, label="P279", dir="back")
            
        dots.append(dot)
        
        try:
            dot.render(f"output/dots/AP1_{dot.comment}.gv")
        except:
            pass


def get_ranking_entity_set(rankingFile):
    entityList = parse_ranking_file(rankingFile)
    return set(entityList)


def build_tree(entities, dictFilename, ocurrencesFilename):
    with open(Path(dictFilename), "r+", encoding="utf8") as dictFile:
        entitiesDict = json.load(dictFile)
    with open(Path(ocurrencesFilename), "r+", encoding="utf8") as ocurrencesFile:
        entitiesOccurrencesDict = json.load(ocurrencesFile)
    # print(entitiesDict)
    filteredEntities = dict(
        filter(
            lambda x: x[1]["superclasses"] == [] or x[1]["superclasses"] == x[1],
            entitiesDict.items(),
        )
    )
    print(filteredEntities)

    # dots = []
    # for entity in filteredEntities.items():
    #     entityLabel = wikidata_utils.get_entity_label(entity[0])

    #     dot = Digraph(comment=entityLabel)

    #     dot.node(entity[0], entityLabel)
    #     for subclass in entitiesOccurrencesDict[entity[0]]["subclasses"]:

    #         # If label is unavailalble, use ID
    #         if subclass["subjectLabel"] != "Label unavailable":
    #             dot.node(subclass["subject"], subclass["subjectLabel"])
    #         else:
    #             dot.node(subclass["subject"], subclass["subject"])

    #         dot.edge(subclass["subject"], entity[0])
    #     dots.append(dot)

    # for dot in dots:
    #     try:
    #         dot.render(f"output/dots/AP1_{dot.comment}.gv")
    #     except:
    #         pass

    # dot.node('A', 'King Arthur')

    # for entity in entitiesDict.items():
    #     for subclass in entity[1]["subclasses"]:
    #         find_subclasses(entities, subclass)

    # with open(Path(dictFilename + "_out.json"), "w+", encoding="utf8") as outDict:
    #     json.dump(filteredEntities, outDict)


def group(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return list(zip_longest(fillvalue=fillvalue, *args))


def parse_ranking_file(rankingFile):
    lines = rankingFile.readlines()
    lines = list(map(lambda line: line.strip(), lines))

    regex_pattern = re.compile(".*?(Q\d+)")
    rankEntities = [
        m.group(1) for m in (regex_pattern.match(line) for line in lines) if m
    ]

    return rankEntities


if __name__ == "__main__":
    try:
        fileIn = Path(sys.argv[2])
        groupByN = Path(sys.argv[3])
    except:
        fileIn = Path("output/AP1_minusQ23958852_items_ranking.txt")
        groupByN = 100

    with open(fileIn, "r") as rankingFile:
        entities = parse_ranking_file(rankingFile)
    # entitiesSet = get_ranking_entity_set(rankingFile)
    # pprint(entitiesSet)
    # read_AP1_results(entitiesSet)
    #     entities = parse_ranking_file(rankingFile)

    # build_tree(
    #     entities,
    #     "output/AP1_trees_incomplete.json",
    #     "output/AP1_ranking_entities.json",
    # )

    entitiesDict = {}
    for entity in entities:
        entitiesDict[entity] = {"superclasses": [], "subclasses": []}

    # nEntities = group(groupByN, entities)
    # entitiesSquared = [entities for entity in entities]

    # filteredEntities = dict(
    #     filter(
    #         lambda x: x[1]["superclasses"] == [] or x[1]["superclasses"] == x[1],
    #         entitiesDict.items(),
    #     )
    # )
    graph_from_superclasses_dict("output/AP1_trees_superclasses.json")
    # with open(
    #     Path("output/AP1_trees_superclasses.json"), "r+", encoding="utf8"
    # ) as jsonFile:
    #     filteredEntities = json.load(jsonFile)
    #     # Filter out entities without any subclasses in the ranking
    #     filteredEntities = dict(
    #         filter(
    #             lambda x: x[1]["subclasses"] != [] or x[1]["subclasses"] == x[1],
    #             filteredEntities.items(),
    #         )
    #     )
    #     print(f"{len(filteredEntities)} entities.")

    # entitiesDict
    # for entity in filteredEntities.items():
    #     print(f"\nChecking taxonomic tree for {entity[0]}:")
    #     for subclass in entity[1]["subclasses"]:
    #         print(f"Is {subclass} subclass of {entity[0]}?")
    #         querySubclass = wikidata_utils.query_subclasses_stardog(entity[0], subclass)
    #         pprint(querySubclass["results"]['bindings'])
    #         if querySubclass["results"]['bindings']:

    #         # Find all classes between
    #         for i, auxEntity in enumerate(nEntities):
    #             # print(i)
    #             if querySubclass["results"]["bindings"][0][f"isSubclass{i}"][
    #                         "entity"
    #                     ]:
    #                 isSubclass = True
    #             if isSubclass:
    #                 print(
    #                     f"\n  - Is {nEntities[i]} subclass of {entity}? {isSubclass}",
    #                     end=" ",
    #                 )
    #                 entitiesDict[entity]["subclasses"].append(nEntities[i])
    #                 entitiesDict[nEntities[i]]["superclasses"].append(entity)
    #                 # pprint(entitiesDict[entity])

    # with open(
    #     Path("output/AP1_trees_incomplete.json"), "w+", encoding="utf8"
    # ) as jsonFile:
    #     json.dump(entitiesDict, jsonFile)
