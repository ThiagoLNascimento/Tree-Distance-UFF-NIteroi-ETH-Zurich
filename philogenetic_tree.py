import distance
import networkx as nx
from networkx.algorithms import isomorphism
from networkx_algo_common_subtree.tree_isomorphism import *
from networkx_algo_common_subtree.utils import graph_str
from itertools import combinations
import time
import sys

# Read input file (format Newick)
def input_trees():
    
    f = open("datasets/dataHou78.txt", "r")

    lines = f.readlines()
    trees = []

    leaves = 0

    for line in lines:
        trees.append(nx.DiGraph())
        newick = line.split()
        trees[-1].add_node(0, value= 0, moved= 0, label= 0)
        current_node = 0
        new_node = 0
        for i in range(len(newick)):

            if newick[i] == "(":
                new_node += 1
                trees[-1].add_edge(current_node, new_node)
                trees[-1].nodes[new_node]["value"] = 0
                trees[-1].nodes[new_node]["moved"] = 0
                trees[-1].nodes[new_node]["label"] = 0
                current_node = new_node
        
            elif newick[i] == ")":
                current_node = next(trees[-1].predecessors(current_node))
            
            else:
                number = int(newick[i])
                new_node += 1
                trees[-1].add_edge(current_node, new_node)
                trees[-1].nodes[new_node]["value"] = number
                trees[-1].nodes[new_node]["moved"] = 0
                trees[-1].nodes[new_node]["label"] = 0
                leaves = leaves + 1

    return trees, leaves / len(trees)


if __name__ == '__main__':
    trees, number_leaves = input_trees()
    combination = list(combinations(range(len(trees)), 2))
    start = time.time()

    first_interation = 0
    closest = 0
    sum_distance = 0
    a = 0

    while len(combination) > 1:

        min = sys.maxsize
        combination = list(combinations(range(len(trees)), 2))
        current_index = 0
        combination_index = 0
        distances = []
        for i in combination:
            new = [trees[i[0]].copy(),trees[i[1]].copy()]
                
            total_distance, duration, intermediate_tree = distance.calc_distance(new, number_leaves)
            # print(f'Quantidade de execuções: {a}')
            # print(f'Duração : {duration}')


            try:
                if len(intermediate_tree) == 0:
                    distances.append([i[0], i[1], trees[i[0]].copy()])
                elif len(intermediate_tree) == 1:
                    distances.append([i[0], i[1], intermediate_tree[0][0].copy()])
                else:
                    distances.append([i[0], i[1], intermediate_tree[total_distance//2][0].copy()])
            except IndexError:
                distances.append([i[0], i[1], intermediate_tree[-2][0].copy()])

            if total_distance <= min:
                min = total_distance
                combination_index = current_index

            if first_interation == 0 :
                sum_distance += total_distance
                if closest < total_distance:
                    closest = total_distance
                

            current_index += 1
        
        first_interation = 1
        a += 1
        print(f'Execution of number {a}')

        trees.pop(distances[combination_index][1]) 
        trees.pop(distances[combination_index][0])
        trees.append(distances[combination_index][2])

    end = time.time()

    f = open("output/Output_dataHou78.txt", "w")
    # f.write("Consensus tree =")
    consensus = trees[0].copy()
    # f.write(graph_str(consensus))

    f.write("Duration = ")
    f.write(str(end - start))

    # Calcute the maximum distance between the inputs and the consensus
    max = 0
    sum = 0
    trees, number_leaves = input_trees()
    for i in trees:
        new = [i.copy(),consensus.copy()]    
        total_distance, duration, intermediate_tree = distance.calc_distance(new, number_leaves)

        if total_distance > max:
            max = total_distance

        sum += total_distance

    f.write("\nClosest = ")
    f.write(str(max - (closest)/2))

    f.write("\nMedian = ")
    f.write(str(sum - (sum_distance)/2))