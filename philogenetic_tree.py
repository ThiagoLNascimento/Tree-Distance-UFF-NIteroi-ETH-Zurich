import distance
import networkx as nx
from networkx.algorithms import isomorphism
from networkx_algo_common_subtree.tree_isomorphism import *
from networkx_algo_common_subtree.utils import write_network_text
import time
import sys

# Read input file (format Newick)
def input_trees(file_name, folder_name):
    
    # f = open("datasets/" + folder_name + "/" + file_name +".txt", "r")
    f = open("datasets/dataXu.txt", "r")

    lines = f.readlines()
    trees = []

    leaves = 0 
    height = 0

    for line in lines:
        trees.append(nx.DiGraph())
        newick = line.split()
        trees[-1].add_node(0, value= 0, height = 0, label= 0)
        current_node = 0
        new_node = 0
        for i in range(len(newick)):

            if newick[i] == "(":
                new_node += 1
                height += 1
                trees[-1].add_edge(current_node, new_node)
                trees[-1].nodes[new_node]["value"] = 0
                trees[-1].nodes[new_node]["label"] = 0
                trees[-1].nodes[new_node]["height"] = height
                current_node = new_node
        
            elif newick[i] == ")":
                current_node = next(trees[-1].predecessors(current_node))
                height -= 1
            
            else:
                number = int(newick[i])
                new_node += 1
                trees[-1].add_edge(current_node, new_node)
                trees[-1].nodes[new_node]["value"] = number
                trees[-1].nodes[new_node]["label"] = 0
                trees[-1].nodes[new_node]["height"] = height + 1
                leaves = leaves + 1

    return trees, leaves / len(trees)


if __name__ == '__main__':
    file_name = sys.argv[2]
    folder_name = sys.argv[1]
    trees, number_leaves = input_trees(file_name, folder_name)
    number_trees = len(trees)
    start = time.time()

    closest = 0
    sum_distance_input = 0
    max_input = 0
    iterations = 0

    median_trees = []
    for i in range(number_trees):
        median_trees.append([])
        for j in range(number_trees):
            median_trees[i].append([0, sys.maxsize])

    min = sys.maxsize
    index = [0, 0]

    for i in range(number_trees):
        for j in range(i + 1, number_trees):
            if i != j:
                new = [trees[i].copy(),trees[j].copy()]
                total_distance, duration, intermediate_tree = distance.calc_distance(new, number_leaves, 1)

                if len(intermediate_tree) == 0:
                    median_trees[i][j] = [trees[i].copy(), total_distance]
                    median_trees[j][i] = [trees[i].copy(), total_distance]
                elif len(intermediate_tree) == 1:
                    median_trees[i][j] = [intermediate_tree[0][0].copy(), total_distance]
                    median_trees[j][i] = [intermediate_tree[0][0].copy(), total_distance]
                else:
                    aux = total_distance//2
                    while True:
                        try:
                            median_trees[i][j] = [intermediate_tree[aux][0].copy(), total_distance]
                            median_trees[j][i] = [intermediate_tree[aux][0].copy(), total_distance]
                            break
                        except IndexError:
                            aux -= 1
                            if aux == 0:
                                median_trees[i][j] = [trees[i].copy(), total_distance]
                                median_trees[j][i] = [trees[i].copy(), total_distance]
                                break

                if total_distance > max_input:
                    max_input = total_distance

                if total_distance <= min:
                    min = total_distance
                    index[0] = i
                    index[1] = j

                sum_distance_input += total_distance
                if closest < total_distance:
                    closest = total_distance
    
    # f.write("Max distance among input = " + str(max_input))

    trees.pop(index[1])
    trees.pop(index[0])
    trees.append(median_trees[index[0]][index[1]][0])

    for i in trees[-1]:
        trees[-1].nodes[i]["label"] = 0
        if trees[-1].nodes[i]["value"] > number_leaves:
            trees[-1].nodes[i]["value"] = 0
    
    for i in range(number_trees):
        median_trees[i].pop(index[1])
        median_trees[i].pop(index[0])

    median_trees.pop(index[1])
    median_trees.pop(index[0])

    iterations += 1 
    # print(f'Execution of number: {iterations}')
    # print(f'Duration : {time.time() - start}')
    number_trees -= 1
    while number_trees > 1:

        min = sys.maxsize
        index = [0, 0]
        median_trees.append([])
        for i in range(number_trees):
            for j in range(i + 1, number_trees):
                if j == number_trees - 1:
                    new = [trees[i].copy(),trees[j].copy()]
                    total_distance, duration, intermediate_tree = distance.calc_distance(new, number_leaves, 1)
                    if len(intermediate_tree) == 0:
                        median_trees[i].append([trees[i].copy(), total_distance])
                        median_trees[j].append([trees[i].copy(), total_distance])
                    elif len(intermediate_tree) == 1:
                        median_trees[i].append([intermediate_tree[0][0].copy(), total_distance])
                        median_trees[j].append([intermediate_tree[0][0].copy(), total_distance])
                    else:
                        aux = total_distance//2
                        while True:
                            try:
                                median_trees[i].append([intermediate_tree[aux][0].copy(), total_distance])
                                median_trees[j].append([intermediate_tree[aux][0].copy(), total_distance])
                                break
                            except IndexError:
                                aux -= 1
                                if aux == 0:
                                    median_trees[i].append([trees[i].copy(), total_distance])
                                    median_trees[j].append([trees[i].copy(), total_distance])
                                    break
                    if total_distance <= min:
                        min = total_distance
                        index[0] = i
                        index[1] = j

                elif i != j:
                    if median_trees[i][j][1] <= min:
                        min = median_trees[i][j][1]
                        index[0] = i
                        index[1] = j
 
        median_trees[-1].append([0, sys.maxsize])
 
        trees.pop(index[1])
        trees.pop(index[0])
        trees.append(median_trees[index[0]][index[1]][0])

        for i in trees[-1]:
            trees[-1].nodes[i]["label"] = 0
            if trees[-1].nodes[i]["value"] > number_leaves:
                trees[-1].nodes[i]["value"] = 0

        for i in range(number_trees):
            median_trees[i].pop(index[1])
            median_trees[i].pop(index[0])

        median_trees.pop(index[1])
        median_trees.pop(index[0])
        iterations += 1
        # print(f'Execution of number: {iterations}')
        # print(f'Duração : {time.time() - start}')
        number_trees -= 1 
 
    end = time.time()
    
    consensus = trees[0].copy()

    # f.write("\nDuration = ")
    # f.write(str(end - start))

    # Calcute the maximum distance between the inputs and the consensus
    max = 0
    sum = 0
    trees, number_leaves = input_trees(file_name, folder_name)
    array = []
    for i in trees:
        new = [i.copy(),consensus.copy()]    
        total_distance, duration, intermediate_tree = distance.calc_distance(new, number_leaves, 0) 

        if total_distance > max:
            max = total_distance

        sum += total_distance

    # f.write("\nMaximum distance between the conseunsus and all input: " + str(max))
    # f.write("\nSum of the distance between the consensus and all input: " + str(sum))
    # f.write("\nClosest = ")
    # f.write(str(max - (closest) / 2))

    # f.write("\nMedian = ")
    # f.write(str(sum - (sum_distance_input) / (len(trees) - 1)))

    f = open("output/Output_philo_Xu.txt", "w")
    f.write("Max distance among input = " + str(max_input))
    f.write("\nDuration = " + str(end - start))
    f.write("\nMaximum distance between the conseunsus and all input: " + str(max))
    f.write("\nSum of the distance between the consensus and all input: " + str(sum))
    f.write("\nClosest = " + str(max - (closest) / 2))
    f.write("\nMedian = " + str(sum - (sum_distance_input) / (len(trees) - 1)))

    # f = open("output/Output_" + folder_name + "_phylo.txt", "a")
    # f.write("\n" + str(end - start) + " , " + str(abs(max - (closest) / 2)) + " , " + str(abs(sum - (sum_distance_input) / (len(trees) - 1))))