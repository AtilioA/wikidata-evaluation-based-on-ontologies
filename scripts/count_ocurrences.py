import os
import sys
import re
from pathlib import Path
from functools import reduce


if __name__ == "__main__":
    fileBase = Path(sys.argv[1])
    fileCompare = Path(sys.argv[2])
    print(f"Reading from '{fileBase}' and '{fileCompare}'")
    with open(fileBase, "r", encoding="utf-8") as fBase:
        with open(fileCompare, "r", encoding="utf-8") as fCompare:
            entitiesList = fBase.readlines()
            compareList = fCompare.readlines()
            entitiesList = list(map(lambda line: line.strip(), entitiesList))
            compareList = list(map(lambda line: line.strip(), compareList))

    countEntitiesDict = {}
    for entity in entitiesList:
        countEntitiesDict[entity] = compareList.count(entity)
    print(countEntitiesDict)
    totalCount = reduce(lambda x, y: x + y, countEntitiesDict.values())
    print(f"Number of direct instances of Q23958852 in AP1: {totalCount}")
