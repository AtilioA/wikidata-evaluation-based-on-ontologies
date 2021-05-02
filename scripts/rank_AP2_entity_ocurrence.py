from pprint import pprint
from collections import Counter
import csv
import wikidata_utils

if __name__ == "__main__":
    with open("../queries/results/AP2.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        Aentities = [row[0] for row in reader]
        print(Aentities)

    # Read start and stop arguments from argv
    lo, hi = wikidata_utils.parse_lo_hi()

    Aentities = wikidata_utils.remove_instances_Q23958852(
        Aentities, "other/instancesof_Q23958852.txt"
    )

    # Count most frequent entities with Counter
    topEntities = Counter(Aentities).most_common(hi)
    print(topEntities)

    # Open output file
    with open(
        "output/ranking/AP2_minus_Q23958852_ranking.txt", "a+", encoding="utf8"
    ) as fRanking:
        for i, (entity, frequency) in enumerate(topEntities[lo:]):
            try:
                label = wikidata_utils.get_entity_label(entity)

                fRanking.write(f"{i + 1} - {entity} ({label}): {frequency}\n")
                print(f"{i + 1} - Wrote {entity} ({label}).")
            except Exception as exception:
                pprint(f"Failed for {entity}, ({exception})")
                fRanking.write(f"{entity} (label unavailable): {frequency}\n")
