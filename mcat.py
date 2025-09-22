import distance
import networkx as nx
from networkx.algorithms import isomorphism
from networkx_algo_common_subtree.tree_isomorphism import *
from networkx_algo_common_subtree.utils import write_network_text
import time
import sys

# Read input file (format Newick)
def input_trees(file_name, folder_name):
    
    f = open("datasets/" + folder_name + "/" + file_name +".txt", "r")

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

# Compare if from two nodes it is possible to find and isomphic subtree
# Input: two nodes
# Output: If both nodes form an isomorphic subtree, list with the pair of nodes mapping the tree1 to tree2. Otherwise an empty list
def isomorphism_subtree(node1, node2, tree1, tree2):

    isomorphic = isomorphism.rooted_tree_isomorphism(tree1, node1, tree2, node2)
    list_leaves = [[], []]
    leaves = 0

    if len(isomorphic) != 0:
        for k in range (len(isomorphic)):
            if tree1.nodes[isomorphic[k][0]]["value"] != 0 or tree2.nodes[isomorphic[k][1]]["value"] != 0:
                list_leaves[0].append(tree1.nodes[isomorphic[k][0]]["value"])
                list_leaves[1].append(tree2.nodes[isomorphic[k][1]]["value"])
                leaves += 1

        list_leaves[0].sort()
        list_leaves[1].sort()

        if list_leaves[0] == list_leaves[1] and leaves > 0:
            return isomorphic, leaves
        
    return [], -1


# Get the isomorphic subtree rotted in father1 in tree 1 and father2 in tree 2
def v_tree(father1, father2, tree1, tree2):  
    iso, leaves = isomorphism_subtree(father1, father2, tree1, tree2)
    return iso, leaves


def mcat(trees, current_number_leaves):

    auxiliary_trees = []
    

    while current_number_leaves > 0:

        number_leaves = -1
        for i in trees[0]:
            iso = []
            for k in range(1, len(trees), 1):
                exist_isomorphism = 0
                for j in trees[k]:
                    current_isomorphism, number_leaves = v_tree(i, j, trees[0], trees[k])

                    if number_leaves != -1:
                        iso.append(current_isomorphism)
                        exist_isomorphism = 1
                        break
                
                if exist_isomorphism == 0:
                    break
            
            if number_leaves != -1:
                break
        
        if number_leaves != -1:
            current_number_leaves -= number_leaves

            # Dict for where each leaf appears, key the number of the node and the value is a list of lists, where the the first element is the value
            # and the second the number of times it appears
            position_leaves = dict()
            leaves_to_add = []
            for i in range(len(iso)):
                for j in range(len(iso[i])):
                    if trees[0].nodes[iso[i][j][0]]["value"] != 0:
                        if i == 0:
                            position_leaves[iso[i][j][0]] = [[trees[0].nodes[iso[i][j][0]]["value"], 1]]
                            leaves_to_add.append(trees[0].nodes[iso[i][j][0]]["value"])
                        added = 0
                        for k in position_leaves[iso[i][j][0]]:
                            if k[0] == trees[i + 1].nodes[iso[i][j][1]]["value"]:
                                k[1] += 1
                                added = 1
                                break
                        if added == 0:
                            position_leaves[iso[i][j][0]].append([trees[i + 1].nodes[iso[i][j][1]]["value"], 1])
            for i in position_leaves:
                aux = position_leaves.get(i)
                size = len(position_leaves.get(i))
                for l in range(0, size):
                    for j in range(0, size-l-1):
                        if (aux[j][1] < aux[j + 1][1]):
                            temp = aux[j]
                            aux[j] = aux[j + 1]
                            aux[j + 1] = temp

            remove_keys = []
            for i in position_leaves:
                if position_leaves.get(i)[0][1] == len(trees):
                    leaves_to_add.remove(position_leaves.get(i)[0][0])
                    remove_keys.append(i)

            for i in remove_keys:
                position_leaves.pop(i)
            
            while len(leaves_to_add) > 0:
                index = -1
                max = 0
                for i in position_leaves:
                    while (len(position_leaves.get(i)) > 0) and (not position_leaves.get(i)[0][0] in leaves_to_add):
                        position_leaves.get(i).remove(position_leaves.get(i)[0]) 
                    if len(position_leaves.get(i)) > 0:
                        if position_leaves.get(i)[0][1] > max:
                            index = i
                            max = position_leaves.get(i)[0][1]

                if index != -1:
                    trees[0].nodes[index]["value"] = position_leaves.get(index)[0][0]
                    leaves_to_add.remove(position_leaves.get(index)[0][0])
                    position_leaves.pop(index)
                else:
                    for i in position_leaves:
                        trees[0].nodes[i]["value"] = leaves_to_add[0]
                        leaves_to_add.pop(0)


            new_tree = nx.DiGraph()
            try:
                temp_node = next(trees[0].predecessors(iso[0][0][0]))
            except StopIteration:
                temp_node = -1
            for j in range(len(iso[0])):
                new_tree.add_node(iso[0][j][0], value = trees[0].nodes[iso[0][j][0]]["value"], label = trees[0].nodes[iso[0][j][0]]["label"], height = trees[0].nodes[iso[0][j][0]]["height"])
                iterator = trees[0].successors(iso[0][j][0])
                while True:
                    try: 
                        new_tree.add_edge(iso[0][j][0], next(iterator))
                    except StopIteration:
                        break

                if j > 0:
                    try:
                        new_tree.add_edge(next(trees[0].predecessors(iso[0][j][0])), iso[0][j][0])
                    except StopIteration:
                        continue

            auxiliary_trees.append([new_tree, temp_node])

            for i in range(len(iso)):
                for j in range(len(iso[i])):
                    if i == 0: 
                        trees[0].remove_node(iso[0][j][0]) 
                    trees[i + 1].remove_node(iso[i][j][1])
    

    for i in range (len(auxiliary_trees) - 1, -1, -1):
        trees[0].add_nodes_from(auxiliary_trees[i][0].nodes(data=True))
        trees[0].add_edges_from(auxiliary_trees[i][0].edges())
        if auxiliary_trees[i][1] != -1:
            trees[0].add_edge(auxiliary_trees[i][1], list(auxiliary_trees[i][0])[0])
        
    return trees[0]

if __name__ == '__main__':
    file_name = sys.argv[2]
    folder_name = sys.argv[1]
    trees, number_leaves = input_trees(file_name, folder_name)

    number_trees = len(trees)
    max_distance_input = 0
    sum_distance_input = 0
    pior_mediana = 0
    
    for i in range(number_trees):
        somatorio_distancia_atual = 0
        for j in range(number_trees):
            if i != j: 
                new = [trees[i].copy(),trees[j].copy()]
                total_distance, duration, intermediate_tree = distance.calc_distance(new, number_leaves, 0)

                if j > i:
                    sum_distance_input += total_distance
                if max_distance_input < total_distance:
                    max_distance_input = total_distance

            
                somatorio_distancia_atual += total_distance

        if pior_mediana < somatorio_distancia_atual:
            pior_mediana = somatorio_distancia_atual

    start = time.time()
    consensus = mcat(trees, number_leaves)
    end = time.time()
    trees, number_leaves = input_trees(file_name, folder_name)

    max = 0
    sum = 0
    array = []
    for i in trees:
        new = [i.copy(),consensus.copy()]    
        total_distance, duration, intermediate_tree = distance.calc_distance(new, number_leaves, 0)

        if total_distance > max:
            max = total_distance

        sum += total_distance


    f = open("output/Output_MCAT" + folder_name + ".txt", "a")
    f.write("Max distance among input = " + str(max_distance_input))
    f.write("\nSum of distance between all input = " + str(sum_distance_input))
    f.write("\nDuration = " + str(end - start))
    f.write("\nMaximun distance between the conseunsus and all input: " + str(max))
    f.write("\nSum of the distance between the consensus and all input: " + str(sum))
    f.write("\nClosest = " + str((max) - (max_distance_input / 2)))
    f.write("\nMedian = " + str((sum) - ((sum_distance_input / (len(trees) - 1)))))
    f.write("\nNormalized gap (closest) = " + str(((max) - ((max_distance_input / 2))) / (max_distance_input - ((max_distance_input / 2)))))
    f.write("\nNormalized gap (median) = " + str(((sum) - ((sum_distance_input) / (len(trees) - 1))) / (pior_mediana - ((sum_distance_input) / (len(trees) - 1)))))