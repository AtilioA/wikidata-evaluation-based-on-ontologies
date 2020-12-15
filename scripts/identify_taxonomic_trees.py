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
    # subclassLabels = [
    #     wikidata_utils.get_entity_label(subclass) for subclass in subclassesList
    # ]
    # print(subclassLabels)
    # print("")

    try:
        # Remove superclass from the list (it is included by SPARQL)
        subclassesList.remove(superclass)
    except:
        pass

    # Return reversed list so we can use it immediately in the right order with graphviz
    return list(reversed(subclassesList))


def graph_from_superclasses_dict(treesDictFilename, **kwargs):
    # PROBLEMA: Dado um dicionário com entidades, suas superclasses e subclasses, construir um grafo, mantendo hierarquia das entidades
    # INPUT: Dicionário com entidades, suas superclasses e subclasses
    # OUTPUT: Grafo que exibe árvores taxonômicas

    # Optional argument; if it exists, will include only entities from the ranking
    rankingEntities = kwargs.get("rankingEntities", None)

    with open(Path(treesDictFilename), "r+", encoding="utf8") as dictFile:
        entitiesDict = json.load(dictFile)

    # Filter out entities without any subclasses in the ranking
    # EntidadesDeInteresse := entidades sem superclasse ou cujas únicas superclasses sejam elas mesmas
    entitiesDict = dict(
        filter(
            lambda x: x[1]["subclasses"] != []
            and (x[1]["superclasses"] == [] or [x[0]] == x[1]["superclasses"]),
            entitiesDict.items(),
        )
    )
    # Number of remaining entities
    print(f"{len(entitiesDict)} superclasses")

    nodesDict = {}
    # Para cada entidade de interesse:
    for entity in entitiesDict.items():
        # Get label for each main entity
        entityLabel = wikidata_utils.get_entity_label(entity[0])
        print(f"\nBuilding graph for {entity[0]} ({entityLabel})")

        # Create graph for each main entity
        dot = Digraph(comment=entityLabel, strict=True, encoding="utf8")

        # Create bigger node for each main entity
        # Criar nó da entidade
        dot.node(f"{entityLabel}\n{entity[0]}", fontsize="24")
        # Adicionar QID da entidade no dicionário de nós
        nodesDict[entity[0]] = True

        # Para cada subclasse da entidade:
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

            # print(f"{subclass} já tem node? {nodesDict.get(subclass, False)}")
            # print(subclassLabel)
            if not nodesDict.get(subclass, False):
                # Criar nó da subclasse
                dot.node(f"{subclassLabel}\n{subclass}")
                # Adicionar QID da subclasse no dicionário de nós
                nodesDict[subclass] = True

            # Realizar uma query para descobrir entidades intermediárias entre a entidade e a subclasse (lista ordenada)
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

                print(f"Our list: {subclassesBetween}")

                #  [
                #     subclass
                #     for subclass in subclassesBetween
                #     if subclass in rankingEntities
                # ]
                # Use no particular styling instead
                subclassNodeArgs = {}
                edgeLabel = "P279+"

            # Se existirem:
            if subclassesBetween:
                # Get labels for each subclass in between
                subclassLabels = [
                    wikidata_utils.get_entity_label(subclass)
                    for subclass in list(subclassesBetween)
                ]

                # Ligar subclasse à primeira entidade intermediária
                # Connect main subclass to its immediate superclass (note the dir="back")
                print(
                    f"(First) Marking {subclassNodeLabel.split(NL)[0]} ({subclassNodeLabel.split(NL)[1]}) as subclass of {subclassLabels[-1]} ({list(subclassesBetween)[-1]})"
                )
                dot.edge(
                    subclassNodeLabel,
                    f"{subclassLabels[-1]}\n{list(subclassesBetween)[-1]}",
                    label="P279+",
                    # dir="back",
                )

                # Para cada entidade intermediária:
                for i, subclassBetween in enumerate(subclassesBetween):
                    # print(
                    #     f"{subclassBetween} já tem node? {nodesDict.get(subclassBetween, False)}"
                    # )
                    if not nodesDict.get(subclassBetween, False):
                        # Criar nó para entidade intermediária
                        # Create node for each subclass
                        dot.node(
                            f"{subclassLabels[i]}\n{subclassBetween}",
                            **subclassStyling,
                        )
                        # Adicionar QID da entidade intermediária no dicionário de nós
                        nodesDict[subclassBetween] = True

                # Para cada entidade intermediária:
                for i, subclassBetween in enumerate(list(subclassesBetween)[:-1]):
                    # # If it isn't in the list, it does not have a node
                    # if list(subclassesBetween)[i] not in entity[1]["subclasses"]:
                    #     # Create it
                    #     dot.node(
                    #         f"{subclassLabels[i]}\n{list(subclassesBetween)[i]}",
                    #         **subclassStyling,
                    #     )

                    # Ligar entidade intermediária à próxima
                    # Connect each subclass to its immediate superclass

                    # print(subclassesBetween[list(subclassesBetween)[i]])
                    # print(subclassesBetween[list(subclassesBetween)[i + 1]])
                    # If both entries are active
                    # if (
                    #     subclassesBetween[list(subclassesBetween)[i]]
                    #     and subclassesBetween[list(subclassesBetween)[i + 1]]
                    # ):

                    # Check if should be connected
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
                                f"    (For) Marking {checkSubclassLabel} ({checkSubclass}) as subclass of {subclassLabels[i + j]} ({entityAbove})"
                            )
                            dot.edge(
                                f"{checkSubclassLabel}\n{checkSubclass}",
                                f"{subclassLabels[i + j]}\n{entityAbove}",
                                label="P279+",
                                # dir="back",
                            )

                        # print(
                        #     f"  (For) Marking {subclassLabels[i]} ({list(subclassesBetween)[i]}) as subclass of {subclassLabels[i + 1]} ({list(subclassesBetween)[i + 1]})"
                        # )
                        # dot.edge(
                        #     f"{subclassLabels[i]}\n{list(subclassesBetween)[i]}",
                        #     f"{subclassLabels[i + 1]}\n{list(subclassesBetween)[i + 1]}",
                        #     label="P279+",
                        #     # dir="back",
                        # )

                # Ligar última entidade intermediária à entidade
                # Connect the topmost superclass to the main superclass, i.e., the entity
                print(
                    f"(Last) Marking {subclassLabels[0]} as subclass of {entityLabel}"
                )
                dot.edge(
                    f"{subclassLabels[0]}\n{list(subclassesBetween)[0]}",
                    f"{entityLabel}\n{entity[0]}",
                    label="P279+",
                    # dir="back",
                )

            # Caso contrário:
            else:
                # Ligar entidade a subclasse diretamente
                # If there are no subclasses in between, connect subclass and entity directly
                print(
                    f"Joining {subclassNodeLabel.split(NL)[0]} ({subclassNodeLabel.split(NL)[1]}) and {entityLabel} ({entity[0]})"
                )
                dot.edge(
                    f"{entityLabel}\n{entity[0]}",
                    subclassNodeLabel,
                    label="P279+",
                    dir="back",
                )

            # Not having graphviz properly installed might raise an exception
            try:
                if rankingEntities:
                    dot.render(f"output/dots/AP1_{dot.comment}.gv")
                else:
                    dot.render(f"output/dots/AP1_{dot.comment}_intermediary.gv")
            except:
                pass


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

        # build_tree(
        #     entities,
        #     "output/AP1_trees_incomplete.json",
        #     "output/AP1_ranking_entities.json",
        # )

        graph_from_superclasses_dict(
            "output/AP1_product copy.json", rankingEntities=entities
        )
        # graph_from_superclasses_dict("output/AP1_trees_incomplete.json")
        # graph_from_superclasses_dict(
        # "output/AP1_trees_incomplete.json", rankingEntities=entities
        # )

