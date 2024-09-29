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
    combination = list(combinations(range(len(trees)), 2))

    while len(combination) > 1:

        min = sys.maxsize
        combination = list(combinations(range(len(trees)), 2))
        current_index = 0
        combination_index = 0
        distances = []

        for i in combination:
            print(current_index)
            
            new = [trees[i[0]].copy(),trees[i[1]].copy()]    
            total_distance, duration, intermediate_tree = distance.calc_distance(new, number_leaves)

            try:
                if len(intermediate_tree) == 0:
                    distances.append([i[0], i[1], trees[i[0]].copy()])
                else:
                    distances.append([i[0], i[1], intermediate_tree[total_distance//2][0].copy()])
            except IndexError:
                distances.append([i[0], i[1], trees[intermediate_tree[-2]].copy()])

            if total_distance <= min:
                min = total_distance
                combination_index = current_index

            current_index += 1

        trees.pop(distances[combination_index][1]) 
        trees.pop(distances[combination_index][0])
        trees.append(distances[combination_index][2])