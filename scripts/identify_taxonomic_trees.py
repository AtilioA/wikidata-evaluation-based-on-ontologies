import re
import sys
import distutils.util
from pathlib import Path
from pprint import pprint
import wikidata_utils
from multiprocessing import Pool, Value
from functools import partial


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



counter = Value('i', 0)
if __name__ == "__main__":
    try:
        fileIn = Path(sys.argv[2])
    except:
        fileIn = Path("output/AP1_minusQ23958852_items_ranking.txt")

    with open(fileIn, "r") as rankingFile:
        entities = parse_ranking_file(rankingFile)

    subclassEntities = {}
    for entity in entities:
        subclassEntities[entity] = []
    pprint(subclassEntities)

    # entitySquared = [i, entity in enumerate(entities)]
    # pprint(entitySquared)

    # func = partial(check_subclass, entities)
    # with Pool(12) as p:
    #     p.map(func, entities)

    # for entity in entities:
    #     print(f"\nChecking taxonomic tree for {entity}:", end="")
    #     for entityBelow in entities:
    #         querySubclass = wikidata_utils.query_subclass_stardog(entity, entityBelow)
    #         isSubclass = bool(distutils.util.strtobool(
    #             querySubclass["results"]["bindings"][0]["isSubclass"]["value"]
    #         ))
    #         print(f"\n  - Is {entityBelow} subclass of {entity}? {isSubclass}", end=" ")
    #         if isSubclass:
    #             subclassEntities[entity].append(entityBelow)
    #             pprint(subclassEntities[entity])

    exit(0)
    # Open output file
    with open(
        "output/AP1_minusQ23958852_items_ranking.txt", "a+", encoding="utf-8"
    ) as fRanking:
        for i, (entity, frequency) in enumerate(topEntities[lo:]):
            try:
                label = wikidata_utils.get_entity_label(entity)

                fRanking.write(f"{i + 1} - {entity} ({label}): {frequency}\n")
                print(f"{i + 1} - Wrote {entity} ({label}).")
            except Exception as exception:
                pprint(f"Failed for {entity}, ({exception})")
                fRanking.write(f"{entity} (label unavailable): {frequency}\n")
