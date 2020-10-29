import sys
import time
from pprint import pprint
from collections import Counter
import requests


WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

OUTPUT_FILENAME = "instancesof_Q23958852.txt"
if __name__ == "__main__":
    # Open output file
    with open(OUTPUT_FILENAME, "w+", encoding="utf-8") as fInstances:
        # SPARQL query to retrieve updated entities labels (in English)
        getLabelSPARQLQuery = f"""
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            SELECT ?item
            WHERE
            {{
                ?item wdt:P31 wd:Q23958852
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
                # Read entities from response
                entities = data["results"]["bindings"]
                print(f"Found {len(entities)} entities, writing to {OUTPUT_FILENAME}")

                for entity in entities:
                    fInstances.write(f"{entity['item']['value']}\n")
            except Exception as exception:
                pprint(f"Failed to write")
                # fRanking.write(f"{entity} - (label unavailable): {frequency}\n")
        else:
            print(f"Query has failed")
            # fRanking.write(f"{entity} - (label unavailable): {frequency}\n")
