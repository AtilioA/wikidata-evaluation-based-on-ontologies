import time
import json
import sys
from pathlib import Path
from pprint import pprint

import wikidata_utils
from graphviz import Digraph

NL = "\n"


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
        subclassesList = wikidata_utils.regex_match_QID(subclassesList)
    except:
        pass

    print(f"Subclasses between '{subclass}' and '{superclass}':\n{subclassesList}")
    # print(subclassLabels)

    try:
        # Remove superclass from the list (it is included by SPARQL)
        subclassesList.remove(superclass)
    except:
        pass

    # Return reversed list so we can use it immediately in the right order with graphviz
    return list(reversed(subclassesList))


def graph_from_superclasses_dict(treesDictFilename, **kwargs):
    # PROBLEM: Given a dictionary with entities, their superclasses and subclasses, create a "maximal" graph that displays the relation between entities
    dotsTime = int(time.time())

    # Optional argument; if it exists, will include only entities from the ranking
    rankingEntities = kwargs.get("rankingEntities", None)

    remainingEntities = set(rankingEntities)
    totalEntities = len(remainingEntities)

    with open(Path(treesDictFilename), "r+", encoding="utf8") as dictFile:
        entitiesDict = json.load(dictFile)

    # Filter out entities without any subclasses in the ranking
    # Entities of interest here are entities without superclasses or whose superclasses are themselves
    entitiesDict = dict(
        filter(
            lambda x: x[1]["subclasses"] != []
            and (x[1]["superclasses"] == [] or [x[0]] == x[1]["superclasses"]),
            entitiesDict.items(),
        )
    )
    # Number of entities to be processed
    print(f"{len(entitiesDict)} superclasses")

    nodesDict = {}
    for entity in entitiesDict.items():
        # Get label for each main entity
        entityLabel = wikidata_utils.get_entity_label(entity[0])
        nSubclasses = len(entity[1]["subclasses"])

        print(f"\nBuilding graph for {entity[0]} ({entityLabel}).")
        print(f"{entityLabel.capitalize()} has at least {nSubclasses} subclasses from the ranking.\n")

        # Create graph for each main entity
        nodesep = "0.25"
        ranksep = "1"
        if nSubclasses > 50:
            nodesep = "0.2"
            ranksep = "4"
        dot = Digraph(
            comment=entityLabel,
            strict=True,
            encoding="utf8",
            graph_attr={"nodesep": nodesep, "ranksep": ranksep},
        )

        # Create a bigger node for each main entity
        dot.node(f"{entityLabel}\n{entity[0]}", fontsize="24")
        # Add entity QID to nodes' dict
        nodesDict[entity[0]] = True

        print(
            f"{totalEntities - len(remainingEntities)} entities (of {totalEntities}) from the ranking processed so far."
        )

        for subclass in entity[1]["subclasses"]:
            # Get label for each subclass
            subclassLabel = wikidata_utils.get_entity_label(subclass)

            # If label is unavailable, use ID
            if subclassLabel != "Label unavailable":
                subclassNodeLabel = f"{subclassLabel}\n{subclass}"
            else:
                subclassNodeLabel = subclass

            print(
                f'Finding subclasses between "{subclassLabel}" and "{entityLabel}"...'
            )

            # Get random color for each subclass
            argsColor = wikidata_utils.random_color_hex()
            if not nodesDict.get(subclass, False):
                # Create subclass node
                dot.node(f"{subclassLabel}\n{subclass}", color=argsColor)
                # Add subclass QID to nodes' dict
                nodesDict[subclass] = True

            # Query intermediary entities between "subclass" and "entity" (returns ordered list)
            subclassesBetween = find_subclasses_between(subclass, entity[0])

            # Default styling for intermediary subclasses
            subclassNodeArgs = {
                "shape": "square",
                "color": "#777777",
                "fontsize": "10",
                "fontcolor": "#555555",
            }
            edgeLabel = "P279"

            if rankingEntities:
                # Filter out subclasses that aren't from the ranking
                subclassesBetween = {
                    subclass: True
                    for subclass in subclassesBetween
                    if subclass in rankingEntities
                }

                print(f"Subclasses between: {subclassesBetween}")

                # Use no particular styling instead
                subclassNodeArgs = {}
                edgeLabel = "P279+"

            if subclassesBetween:
                # Get labels for each subclass in between
                subclassLabels = [
                    wikidata_utils.get_entity_label(subclass)
                    for subclass in list(subclassesBetween)
                ]

                # Connect "main" subclass to its immediate superclass
                print(
                    f"(First) Marking {subclassNodeLabel.split(NL)[0]} ({subclassNodeLabel.split(NL)[1]}) as subclass of {subclassLabels[-1]} ({list(subclassesBetween)[-1]})"
                )
                dot.edge(
                    subclassNodeLabel,
                    f"{subclassLabels[-1]}\n{list(subclassesBetween)[-1]}",
                    label="P279+",
                    color=argsColor,
                )

                try:
                    remainingEntities.remove(list(subclassesBetween)[-1])
                except KeyError:
                    pass

                for i, subclassBetween in enumerate(subclassesBetween):
                    if not nodesDict.get(subclassBetween, False):
                        # Create node for each subclass
                        dot.node(
                            f"{subclassLabels[i]}\n{subclassBetween}",
                            **subclassNodeArgs,
                            color=argsColor,
                        )
                        # Add intermediary entity QID to nodes' dict
                        nodesDict[subclassBetween] = True

                for i, subclassBetween in enumerate(list(subclassesBetween)[:-1]):

                    # Connect each subclass to its immediate superclass
                    # First, check if they should be connected
                    for j, entityAbove in enumerate(list(subclassesBetween)[i:]):
                        checkSubclass = list(subclassesBetween)[i]
                        checkSubclassLabel = subclassLabels[i]
                        if i == 0:
                            checkSubclass = subclass
                            checkSubclassLabel = subclassLabel

                        isSubclass = wikidata_utils.query_subclass_stardog(
                            entityAbove, checkSubclass, transitive=True
                        )["results"]["bindings"][0]["isSubclass0"]["value"]
                        isSubclass = isSubclass.lower() == "true"
                        print(
                            f"  (For) Is {checkSubclass} subclass of {entityAbove}? {isSubclass}"
                        )
                        if isSubclass:
                            print(
                                f"  Marking {checkSubclassLabel} ({checkSubclass}) as subclass of {subclassLabels[i + j]} ({entityAbove})"
                            )
                            dot.edge(
                                f"{checkSubclassLabel}\n{checkSubclass}",
                                f"{subclassLabels[i + j]}\n{entityAbove}",
                                label="P279+",
                                color=argsColor,
                            )

                            try:
                                remainingEntities.remove(checkSubclass)
                            except KeyError:
                                pass
                            try:
                                remainingEntities.remove(entityAbove)
                            except KeyError:
                                pass

                    print(
                        f"{totalEntities - len(remainingEntities)} entities (of {totalEntities}) from the ranking processed so far."
                    )

                # Connect the topmost superclass to the main superclass, i.e., the entity
                print(
                    f"(Last) Marking {subclassLabels[0]} as subclass of {entityLabel}"
                )
                dot.edge(
                    f"{subclassLabels[0]}\n{list(subclassesBetween)[0]}",
                    f"{entityLabel}\n{entity[0]}",
                    label="P279+",
                    color=argsColor,
                )

            else:
                # If there are no subclasses in between, connect subclass and entity directly
                print(
                    f"Joining {subclassNodeLabel.split(NL)[0]} ({subclassNodeLabel.split(NL)[1]}) and {entityLabel} ({entity[0]})"
                )
                dot.edge(
                    subclassNodeLabel,
                    f"{entityLabel}\n{entity[0]}",
                    label="P279+",
                    color=argsColor,
                )

            try:
                remainingEntities.remove(subclass)
            except KeyError:
                pass

            # Not having graphviz properly installed might raise an exception
            try:
                if rankingEntities:
                    dot.render(f"output/dots/dots_{dotsTime}/AP1_{dot.comment}.gv")
                else:
                    dot.render(
                        f"output/dots/dots_{dotsTime}/AP1_{dot.comment}_intermediary.gv"
                    )
            except:
                print("\nVerify your Graphviz installation or Digraph args!\n")
                pass

        try:
            remainingEntities.remove(entity[0])
        except KeyError:
            pass

    print(remainingEntities)


def get_ranking_entity_set(rankingFile):
    entityList = parse_ranking_file(rankingFile)
    return set(entityList)


def parse_ranking_file(rankingFile):
    lines = rankingFile.readlines()
    lines = list(map(lambda line: line.strip(), lines))

    # Look for the QID in all strings
    rankEntities = wikidata_utils.regex_match_QID(lines)

    return rankEntities


if __name__ == "__main__":
    try:
        fileIn = Path(sys.argv[2])
    except:
        fileIn = Path("output/AP1_minusQ23958852_items_ranking.txt")

    with open(fileIn, "r") as rankingFile:
        entities = parse_ranking_file(rankingFile)
        #     entitiesSet = get_ranking_entity_set(rankingFile)

        # graph_from_superclasses_dict(
        #     "output/AP1_occurrence.json", rankingEntities=entities
        # )
        graph_from_superclasses_dict(
            "output/AP1_trees_incomplete.json", rankingEntities=entities
        )
