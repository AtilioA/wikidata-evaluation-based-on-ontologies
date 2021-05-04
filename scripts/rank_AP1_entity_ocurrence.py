import re
import csv
import json
from pathlib import Path
from pprint import pprint
from collections import Counter

import wikidata_utils


if __name__ == "__main__":
    # AP1T = AP1 with transitivity
    with open("../queries/results/AP1T.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        Aentities = [row[1] for row in reader]

    # Read start and stop arguments from argv
    lo, hi = wikidata_utils.parse_lo_hi()

    # Filter out instances of Q23958852 (subjects)
    Aentities = wikidata_utils.remove_instances_Q23958852(
        Aentities, "other/instancesof_Q23958852.txt"
    )

    # Count most frequent entities with Counter
    topEntities = Counter(Aentities).most_common(hi)
    print("Top entities and their # of occurrences: ", topEntities)

    # Open output file
    with open(
        "output/ranking/AP1_minus_Q23958852_ranking.txt", "a+", encoding="utf-8"
    ) as fRanking:
        for i, (entity, frequency) in enumerate(topEntities[lo:]):
            try:
                label = wikidata_utils.get_entity_label(entity)

                fRanking.write(f"{i + 1} - {entity} ({label}): {frequency}\n")
                print(f"{i + 1} - Wrote {entity} ({label}).")
            except Exception as exception:
                pprint(f"Failed for {entity}, ({exception})")
                fRanking.write(f"{i + 1} - {entity} (label unavailable): {frequency}\n")
