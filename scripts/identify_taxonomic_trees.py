import json
import re
import sys
import distutils.util
from pathlib import Path
from pprint import pprint
import wikidata_utils
from multiprocessing import Pool, Value
from functools import partial
from itertools import zip_longest


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


def check_subclass(entities, entity):
    for e in entities:
        querySubclass = wikidata_utils.query_subclass_stardog(e, entity)
        isSubclass = bool(
            distutils.util.strtobool(
                querySubclass["results"]["bindings"][0]["isSubclass"]["value"]
            )
        )
        print(f"\n  - Is {e} subclass of {entity}? {isSubclass}", end=" ")
        if isSubclass:
            subclassEntities[entity].append(e)
            pprint(subclassEntities[entity])
        global counter
        with counter.get_lock():
            counter.value += 1
        print("\ncounter.value:", counter.value)


if __name__ == "__main__":
    try:
        fileIn = Path(sys.argv[2])
        groupByN = Path(sys.argv[3])
    except:
        fileIn = Path("output/AP1_minusQ23958852_items_ranking.txt")
        groupByN = 100

    with open(fileIn, "r") as rankingFile:
        entities = parse_ranking_file(rankingFile)

    subclassEntities = {}
    for entity in entities:
        subclassEntities[entity] = []

    nEntities = group(groupByN, entities)
    entitiesSquared = [entities for entity in entities]

    for entity in entities[4:]:
        print(f"\nChecking taxonomic tree for {entity}:", end="")
        for nEntities in group(groupByN, entities):
            querySubclass = wikidata_utils.query_subclass_stardog(entity, nEntities)
            for i, auxEntity in enumerate(nEntities):
                print(i)
                isSubclass = bool(
                    distutils.util.strtobool(
                        querySubclass["results"]["bindings"][0][f"isSubclass{i}"][
                            "value"
                        ]
                    )
                )
                if isSubclass:
                    print(
                        f"\n  - Is {nEntities[i]} subclass of {entity}? {isSubclass}",
                        end=" ",
                    )
                    subclassEntities[entity].append(nEntities[i])
                    # pprint(subclassEntities[entity])

    with open(Path("output/AP1_trees_incomplete.json"), "w+", encoding="utf8") as jsonFile:
        json.dump(subclassEntities, jsonFile)
