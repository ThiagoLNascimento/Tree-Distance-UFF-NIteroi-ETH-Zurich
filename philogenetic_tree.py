import distance
import networkx as nx
from networkx.algorithms import isomorphism
from networkx_algo_common_subtree.tree_isomorphism import *
from networkx_algo_common_subtree.utils import graph_str
from itertools import chain, combinations
import time
import sys

# Read input file (format Newick)
def input_trees():
    
    f = open("Input.txt", "r")

    lines = f.readlines()
    trees = []

    leaves = 0

    for line in lines:
        level = 0
        trees.append(nx.DiGraph())
        newick = line.split()
        trees[-1].add_node(0, value= 0, moved= 0, level= 0)
        current_node = 0
        new_node = 0
        for i in range(len(newick)):

            if newick[i] == "(":
                new_node += 1
                level += 1
                trees[-1].add_edge(current_node, new_node)
                trees[-1].nodes[new_node]["value"] = 0
                trees[-1].nodes[new_node]["moved"] = 0
                trees[-1].nodes[new_node]["level"] = level
                current_node = new_node
        
            elif newick[i] == ")":
                current_node = next(trees[-1].predecessors(current_node))
                level -= 1
            
            else:
                number = int(newick[i])
                new_node += 1
                trees[-1].add_edge(current_node, new_node)
                trees[-1].nodes[new_node]["value"] = number
                trees[-1].nodes[new_node]["moved"] = 0
                trees[-1].nodes[new_node]["level"] = level + 1
                leaves = leaves + 1

        # print(graph_str(trees[-1]))
    
    return trees, leaves / len(trees)


if __name__ == '__main__':
    trees, number_leaves = input_trees()
    min = sys.maxsize
    distances = []
    elements = []
    combination = list(combinations(range(len(trees)), 2))

    for i in combination:
        distances.append([i[0], i[1]])
    
        new = [trees[i[0]].copy(),trees[i[1]].copy()]    

        total_distance, duration, intermediate_tree = distance.calc_distance(new, number_leaves)
    
        if total_distance <= min:
            min = total_distance
            elements = i

        distances[-1].append(total_distance) 

    # while len(combination) > 1:
    #     pass
