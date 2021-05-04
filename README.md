# An evaluation of the Wikidata platform based on ontologies
Some SPARQL queries and Python scripts I've written during my undergraduate research (Scientific Initiation) in 2020-2021.

Running scripts does not require any external libraries except for `graphviz` (as stated in `requirements.txt`) if you want to generate graphs with `scripts/identify_taxonomic_trees.py`.
Stardog is only required for labels to be added to the ranking and to find subclasses before generating graphs, so it is possible to generate rankings without it, but labels for entities will be missing. Stardog was used to query local Wikidata dump and `stardog` is required to be set on your `PATH` variable. It is also required having a Stardog server up and running (`stardog-admin server start`) for queries to be served. These scripts were only tested and executed on Linux distributions (especifically, Linux Mint 20) and may not work on other operating systems.

## Directory structure

`queries/`: .sparql files for queries;

&nbsp;&nbsp;&nbsp;&nbsp;`queries/results`: queries results;

&nbsp;&nbsp;&nbsp;&nbsp;`queries/other`: old/unused .sparql files;

<br/>

`scripts/`: scripts that manipulate queries results, etc;

&nbsp;&nbsp;&nbsp;&nbsp;`queries/output`: scripts outputs;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`queries/output/dots`: graphs produced with graphviz;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`queries/output/ranking`: rankings for AP1 and AP2;

&nbsp;&nbsp;&nbsp;&nbsp;`queries/other`: old/unused files.

