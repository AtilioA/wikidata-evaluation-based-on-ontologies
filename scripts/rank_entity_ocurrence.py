import sys
import time
from pprint import pprint
from collections import Counter
import requests


WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"


if __name__ == "__main__":
    # Read start and stop arguments from argv
    lo = int(sys.argv[1])
    hi = int(sys.argv[2])

    # Read file with one 'object' (see AP1P.sparql) per line in it
    with open("AP1P_objects.txt", "r", encoding="utf-8") as fAP1P:
        entitiesList = fAP1P.readlines()
        entitiesList = list(map(lambda line: line.strip(), entitiesList))

    # Count most frequent entities with Counter
    topEntities = Counter(entitiesList).most_common(hi)

    # Open output file
    with open("AP1P_objects_ranking.txt", "a+", encoding="utf-8") as fRanking:
        for i, (entity, frequency) in enumerate(topEntities[lo:]):
            # SPARQL query to retrieve updated entities labels (in English)
            getLabelSPARQLQuery = f"""
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?subjectLabel
            WHERE
            {{
                {entity} rdfs:label ?subjectLabel .
                FILTER (lang(?subjectLabel) = "" || lang(?subjectLabel) = "en") .
            }}
            """

            # GET request to Wikidata's SPARQL endpoint
            res = requests.get(
                WIKIDATA_SPARQL_ENDPOINT,
                params={"query": getLabelSPARQLQuery, "format": "json"},
            )

            if res.status_code == 200:
                data = res.json()
                try:
                    # Read label from response
                    label = data["results"]["bindings"][0]["subjectLabel"]["value"]

                    fRanking.write(
                        f"{entity} - {label}: {frequency}\n"
                    )
                    print(f"{i + 1} - Wrote {entity} ({label}).")
                except Exception as exception:
                    pprint(f"Failed for {entity}, {res} ({exception})")
                    fRanking.write(f"{entity} - (label unavailable): {frequency}\n")
            else:
                print(f"Query has failed for {entity}")
                fRanking.write(f"{entity} - (label unavailable): {frequency}\n")

            # To avoid Too Many Requests (HTTP 429)
            time.sleep(1)
