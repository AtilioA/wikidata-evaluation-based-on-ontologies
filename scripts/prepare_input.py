import os
import sys
import re
from pathlib import Path


if __name__ == "__main__":
    fileIn = Path(sys.argv[1])
    nColumns = int(sys.argv[2])
    print(f"Reading from '{fileIn}'")
    with open(fileIn, "r", encoding="utf-8") as fInput:
        entitiesList = fInput.readlines()
        entitiesList = list(map(lambda line: line.strip(), entitiesList))
        entitiesList = list(map(lambda line: re.findall(r"Q\d+", line), entitiesList))
        # print(entitiesList)

    fileOut = Path(f"{os.path.splitext(fileIn)[0]}_prepared.txt")
    print(f"Writing to '{fileOut}'")
    with open(fileOut, "w+", encoding="utf-8") as fOut:
        if nColumns != 1:
            for line in entitiesList:
                if line:
                    for column in nColumns - 1:
                        fOut.write(f"{line[column]}, ")
                    fOut.write(f"{line[column]}\n")
        else:
            for line in entitiesList:
                if line:
                    fOut.write(f"{line[0]}\n")
