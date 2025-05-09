# Tree-Distance-UFF-ETH
Algorithm proposed in the article Determining distances and consensus between trees

For a better explanation for this algortihm consults the article named above.
This implementation uses the python package Networkx to find the isomorphism between two tree, used to find the almost v-tree, as explained before.

## Input
For input, use the file "Input.txt" and edit it with the need trees.
The format used for this trees is the Newick format, note that the algorithm will not work if both trees does not have the same number of leaves,
Note that each tree should be in a single line and onlye the first two lines of the txt are considered.
Also note that between each element, let it be "(", ")" or a number, it needs to be separated by a space.

## Output
The distance calculated for the input will be found on the file "Output.txt". Along with the distance, the respective input will also be there.
