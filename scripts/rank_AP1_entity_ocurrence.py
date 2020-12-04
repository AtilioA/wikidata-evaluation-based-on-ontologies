import re
import csv
import json
from pathlib import Path
from pprint import pprint
from collections import Counter

import wikidata_utils


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


if __name__ == "__main__":
    with open("AP1P_objects.txt", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        Aentities = [row[0] for row in reader]

    # Read start and stop arguments from argv
    lo, hi = wikidata_utils.parse_lo_hi()

    Aentities = wikidata_utils.remove_instances_Q23958852(
        Aentities, "instancesof_Q23958852_prepared.txt"
    )

    # Count most frequent entities with Counter
    topEntities = Counter(Aentities).most_common(hi)
    print(topEntities)

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
