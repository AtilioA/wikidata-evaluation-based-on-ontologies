import json
import re
import sys
from pathlib import Path
from pprint import pprint

import wikidata_utils
from graphviz import Digraph


def find_subclasses_between(subclass, superclass):
    # Query Stardog for subclasses
    subclassesJSON = wikidata_utils.query_subclasses_stardog(superclass, subclass)[
        "results"
    ]["bindings"]

    subclassesList = []
    try:
        # Parse JSON for results
        subclassesList = [result["entity"]["value"] for result in subclassesJSON]

        # Look for QID in all the strings
        regex_pattern = re.compile(".*?(Q\d+)")
        subclassesList = [
            m.group(1)
            for m in (regex_pattern.match(entity) for entity in subclassesList)
            if m
        ]
    except:
        pass

    # print(f"Subclasses between '{subclass}' and '{superclass}':\n{subclassesList}")

    try:
        # Remove superclass from the list (it is included by SPARQL)
        subclassesList.remove(superclass)
    except:
        pass

    # Return reversed list so we can use it immediately in the right order with graphviz
    return list(reversed(subclassesList))


def graph_from_superclasses_dict(treesDictFilename, **kwargs):
    # Optional argument; if it exists, will include only entities from the ranking
    rankingEntities = kwargs.get("rankingEntities", None)

    with open(Path(treesDictFilename), "r+", encoding="utf8") as dictFile:
        entitiesDict = json.load(dictFile)

    # Filter out entities without any subclasses in the ranking
    entitiesDict = dict(
        filter(
            lambda x: x[1]["subclasses"] != []
            and (x[1]["superclasses"] == [] or x[0] in x[1]["superclasses"]),
            entitiesDict.items(),
        )
    )
    # Number of remaining entities
    print(f"{len(entitiesDict)} superclasses")

    for entity in entitiesDict.items():
        # Get label for each main entity
        entityLabel = wikidata_utils.get_entity_label(entity[0])
        print(f"\nBuilding graph for {entity[0]} ({entityLabel})")

        # Create graph for each main entity
        dot = Digraph(comment=entityLabel, strict=True, encoding="utf8")

        # Create bigger node for each main entity
        dot.node(f"{entityLabel}\n{entity[0]}", fontsize="24")

        for subclass in entity[1]["subclasses"]:
            # Get label for each subclass
            subclassLabel = wikidata_utils.get_entity_label(subclass)

            # If label is unavailable, use ID
            if subclassLabel != "Label unavailable":
                subclassNodeLabel = f"{subclassLabel}\n{subclass}"
            else:
                subclassNodeLabel = subclass

            print(
                f'\nFinding subclasses between "{subclassLabel}" and "{entityLabel}"...'
            )

            subclassesBetween = find_subclasses_between(subclass, entity[0])
            # Default styling for intermediary subclasses
            subclassStyling = {
                "shape": "square",
                "color": "#777777",
                "fontsize": "10",
                "fontcolor": "#555555",
            }

            if rankingEntities:
                # Filter out subclasses that aren't from the ranking
                subclassesBetween = [
                    subclass
                    for subclass in subclassesBetween
                    if subclass in rankingEntities
                ]
                # Use no particular styling instead
                subclassStyling = {}

            if subclassesBetween:
                # Get labels for each subclass in between
                subclassLabels = [
                    wikidata_utils.get_entity_label(subclass)
                    for subclass in subclassesBetween
                ]

                # Create node for each subclass
                dot.node(
                    f"{subclassLabels[0]}\n{subclassesBetween[0]}", **subclassStyling
                )

                # Connect main subclass to its immediate superclass (note the dir="back")
                dot.edge(
                    f"{subclassLabels[0]}\n{subclassesBetween[0]}",
                    subclassNodeLabel,
                    label="P279",
                    dir="back",
                )
                for i, subclassBetween in enumerate(subclassesBetween):
                    # Skip the first (see above)
                    if i != 0:
                        # If it isn't in the list, it does not have a node
                        if subclassesBetween[i] not in entity[1]["subclasses"]:
                            # Create it
                            dot.node(
                                f"{subclassLabels[i]}\n{subclassesBetween[i]}",
                                **subclassStyling,
                            )

                        # Connect each subclass to its immediate superclass
                        dot.edge(
                            f"{subclassLabels[i]}\n{subclassesBetween[i]}",
                            f"{subclassLabels[i - 1]}\n{subclassesBetween[i - 1]}",
                            label="P279",
                            dir="back",
                        )

                # Connect the topmost superclass to the main superclass, i.e., the entity
                dot.edge(
                    f"{entityLabel}\n{entity[0]}",
                    f"{subclassLabels[-1]}\n{subclassesBetween[-1]}",
                    label="P279",
                    dir="back",
                )
            else:
                # If there are no subclasses in between, connect subclass and entity directly
                dot.edge(
                    f"{entityLabel}\n{entity[0]}",
                    subclassNodeLabel,
                    label="P279",
                    dir="back",
                )

            # Not having graphviz properly installed might raise an exception
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

    # Look for the QID in all strings
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

    with open(fileIn, "r") as rankingFile:
        entities = parse_ranking_file(rankingFile)
    #     entitiesSet = get_ranking_entity_set(rankingFile)

    # build_tree(
    #     entities,
    #     "output/AP1_trees_incomplete.json",
    #     "output/AP1_ranking_entities.json",
    # )

    # graph_from_superclasses_dict("output/AP1_system.json", rankingEntities=entities)
    graph_from_superclasses_dict("output/AP1_trees_incomplete.json")

