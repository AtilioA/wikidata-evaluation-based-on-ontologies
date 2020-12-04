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

def find_subclasses_between(subclass, superclass):
    subclassesJSON = wikidata_utils.query_subclasses_stardog(superclass, subclass)[
        "results"
    ]["bindings"]

    try:
        subclassesJSON = [result["entity"]["value"] for result in subclassesJSON]
        regex_pattern = re.compile(".*?(Q\d+)")
        subclassesJSON = [
            m.group(1)
            for m in (regex_pattern.match(entity) for entity in subclassesJSON)
            if m
        ]
    except:
        pass

    pprint(f"JSON: {subclassesJSON}")
    subclassesJSON.remove(superclass)
    return subclassesJSON


def graph_from_superclasses_dict(treesDictFilename):
    with open(Path(superclassesDictFilename), "r+", encoding="utf8") as dictFile:
        entitiesDict = json.load(dictFile)

    # Filter out entities without any subclasses in the ranking
    print(f"{len(entitiesDict)} superclasses")
    entitiesDict = dict(
        filter(
            lambda x: x[1]["subclasses"] != []
            and (x[1]["superclasses"] == [] or x[0] in x[1]["superclasses"]),
            entitiesDict.items(),
        )
    )
    print(f"{len(entitiesDict)} superclasses")

    for entity in entitiesDict.items():
        entityLabel = wikidata_utils.get_entity_label(entity[0])
        print(f"Building graph for {entity[0]} ({entityLabel})")

        dot = Digraph(comment=entityLabel, strict=True, encoding="utf8")

        # print(entity[1]["subclasses"])
        for subclass in entity[1]["subclasses"]:
            subclassLabel = wikidata_utils.get_entity_label(subclass)

            # print(subclass, entity[0])

            # If label is unavailable, use ID
            if subclassLabel != "Label unavailable":
                subclassNodeLabel = f"{subclassLabel}\n{subclass}"
            else:
                subclassNodeLabel = subclass

            subclassesBetween = find_subclasses_between(subclass, entity[0])
            if subclassesBetween:
                labels = [
                    wikidata_utils.get_entity_label(subclass)
                    for subclass in subclassesBetween
                ]
                dot.node(
                    f"{labels[0]}\n{subclassesBetween[0]}",
                    shape="square",
                    color="#777777",
                    fontsize="10",
                    fontcolor="#555555",
                )
                dot.edge(
                    f"{labels[0]}\n{subclassesBetween[0]}",
                    subclassNodeLabel,
                    label="P279",
                    dir="back",
                )
                for i, subclassBetween in enumerate(subclassesBetween):
                    if i != 0:
                        if subclassesBetween[i] not in entity[1]["subclasses"]:
                            dot.node(
                                f"{labels[i]}\n{subclassesBetween[i]}",
                                shape="square",
                                color="#777777",
                                fontsize="10",
                                fontcolor="#555555",
                            )
                        dot.edge(
                            f"{labels[i]}\n{subclassesBetween[i]}",
                            f"{labels[i - 1]}\n{subclassesBetween[i - 1]}",
                            label="P279",
                            dir="back",
                        )

                dot.edge(
                    f"{entityLabel}\n{entity[0]}",
                    f"{labels[-1]}\n{subclassesBetween[-1]}",
                    label="P279",
                    dir="back",
                )
            else:
                dot.edge(
                    f"{entityLabel}\n{entity[0]}",
                    subclassNodeLabel,
                    label="P279",
                    dir="back",
                )

            try:
                dot.render(f"output/dots/AP1_{dot.comment}.gv")
            except:
                pass


def get_ranking_entity_set(rankingFile):
    entityList = parse_ranking_file(rankingFile)
    return set(entityList)


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
    except:
        fileIn = Path("output/AP1_minusQ23958852_items_ranking.txt")

    # with open(fileIn, "r") as rankingFile:
    #     entities = parse_ranking_file(rankingFile)
    #     entitiesSet = get_ranking_entity_set(rankingFile)
    # pprint(entitiesSet)

    # build_tree(
    #     entities,
    #     "output/AP1_trees_incomplete.json",
    #     "output/AP1_ranking_entities.json",
    # )

    # entitiesDict = {}
    # for entity in entities:
    #     entitiesDict[entity] = {"superclasses": [], "subclasses": []}

    # graph_from_superclasses_dict("output/AP1_chemical_substance.json")
    graph_from_superclasses_dict("output/AP1_trees_incomplete.json")
  