import networkx as nx
from networkx.algorithms import isomorphism
from networkx_algo_common_subtree.tree_isomorphism import *
from networkx_algo_common_subtree.utils import graph_str
from itertools import chain, combinations
import time

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
    
    return trees, leaves / len(trees)


# Return all subsets of a list
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))


# Compare if from two nodes it is possible to find and isomphic subtree
# Input: two nodes
# Output: If both nodes form an isomorphic subtree, list with the pair of nodes mapping the tree1 to tree2. Otherwise an empty list
def isomorphism_subtree(node1, node2, trees):

    isomorphic = isomorphism.rooted_tree_isomorphism(trees[0], node1, trees[1], node2)
    leaves = 0

    if len(isomorphic) != 0:
        label1_aux = []
        label2_aux = []
        for k in range (len(isomorphic)):
            try:
                next(trees[0].successors(isomorphic[k][0]))
            except StopIteration:
                if trees[0].nodes[isomorphic[k][0]]["value"] != 0:
                    leaves += 1
                    label1_aux.append(trees[0].nodes[isomorphic[k][0]]["value"])
                    label2_aux.append(trees[1].nodes[isomorphic[k][1]]["value"])
        
        return isomorphic, label1_aux, label2_aux, leaves
        
    return -1, -1, -1, -1


# For a defined pair of nodes, will verify if there ir an isomorphic subtree in the almost v tree
# Input: two nodes v1 and v2
# Output: all pairs of nodes that return an isomorphic subtree and 1 if it is a v tree, 0 if it is an almost v tree
def almost_v_tree(father1, father2, trees):

    # Index 0 refers to tree 1 while index 1 refers to tree 2
    set_sons = [[], []]
    size = 0

    # Index 0 refers to tree 1 while index 1 refers to tree 2, 
    # Inside index 0 are for the sons of the input that forms an almost v tree and index 1 are for the values of the leaves for each pair
    compatible_pair = [[],[]], [[],[]]
    isomorphic = []
    
    iterator = trees[0].successors(father1)

    while True:
        try:
            set_sons[0].append(next(iterator))
        except StopIteration:
            break
    
    iterator = trees[1].successors(father2)
    while True:
        try:
            set_sons[1].append(next(iterator))
        except StopIteration:
            break
    
    for i in set_sons[0]:
        for j in set_sons[1]:
            values_1 = []
            values_2 = []
            iso, values_1, values_2 = isomorphism_subtree(i, j)
            if isinstance(iso, int) == False:
                size += 1 
                compatible_pair[0][0].append(i)
                compatible_pair[1][0].append(j)
                # compatible_pair[0][1].append(values_1)
                # compatible_pair[1][1].append(values_2)
                isomorphic.append(iso)
                break


    if size == len(set_sons[1]):
        # compatible_pair[0][0].append(father1)
        # compatible_pair[1][0].append(father2)
        isomorphic.append([(father1, father2)])
        return compatible_pair, isomorphic, 1
    
    return compatible_pair, isomorphic, 0


# Get the isomorphic subtree rotted in father1 in tree 1 and father2 in tree 2
def v_tree(father1, father2, trees):  
    isomorphic = []
    iso, values_1, values_2, leaves = isomorphism_subtree(father1, father2, trees)
    if iso != -1:
        for i in iso:
            trees[0].nodes[i[0]]["moved"] = 1
            trees[1].nodes[i[1]]["moved"] = 1
        isomorphic.append(iso)
    return isomorphic, 0, leaves


# Move all leaves to the same position in both trees in relation to its subgraph
# Input: A matrix where the elements in the first index corresponds to the ones in the second index
# the idea is to modify the first tree in order to the leaves be in the same position as in the second tree
# for this, for each leave in the first tree it need to see where the corresponding leave with the same value is in the second tree 
def path_leaves(nodes_to_move, trees):

    # Dict for all move to be made in the tree
    # The keys are the nodes that the leaves will move
    # The value of each key is which leaves will move in that node 
    path_up = dict()
    path_down = dict()

    # If the element is a leaf then it needs to find where it should be
    for i in range(len(nodes_to_move[0])):
        value_node_1 = trees[0].nodes[nodes_to_move[0][i]]["value"]

        if value_node_1 != 0:

            for j in range(len(nodes_to_move[0])):
                value_node_2 = trees[1].nodes[nodes_to_move[1][j]]["value"]
                
                if value_node_1 == value_node_2:
                    current_path_up = []
                    current_path_down = []
                    initial_pos = trees[0].predecessors(nodes_to_move[0][i])
                    final_pos = trees[0].predecessors(nodes_to_move[0][j])

                    # Will get all predecessors of the leaf that needs to be moved
                    while True:
                        try:
                            aux = next(initial_pos)
                            current_path_up.append(aux)
                            initial_pos = trees[0].predecessors(aux)
                        except StopIteration:
                            break

                    # When the path to go down collides 
                    while True:
                        try:
                            aux = next(final_pos)
                            if aux in current_path_up:
                                index = current_path_up.index(aux)
                                while True:
                                    try:
                                        current_path_up.pop(index)
                                    except IndexError:
                                        break
                                break
                            current_path_down.append(aux)
                            final_pos = trees[0].predecessors(aux)
                        except StopIteration:
                            break
                    
                    keys = path_up.keys()
                    for k in current_path_up:
                        if k not in keys:
                            path_up[k] = [nodes_to_move[0][i]]
                        else:
                            path_up[k].append(nodes_to_move[0][i])

                    keys = path_down.keys()
                    for k in current_path_down:
                        if k not in keys:
                            path_down[k] = [nodes_to_move[0][i]]
                        else:
                            path_down[k].append(nodes_to_move[0][i])

    return path_up, path_down


# Get all sucessors of a node in a determined tree
# Input: an integer for the tree, an integer for the node and an empty list
# Output: the list with all sucessors of the node
def get_all_successors(tree, node, list, trees):
    if tree == 1:
        iterator = trees[0].successors(node)
    else:
        iterator = trees[1].successors(node)

    while True:
        try:
            atual = next(iterator)
            list.append(atual)
            get_all_successors(list, atual, list)
        except StopIteration:
            break

    return


def calc_distance(trees, number_leaves):

    initial_size_tree1 = len(trees[0])
    initial_size_tree2 = len(trees[1])

    if initial_size_tree1 < initial_size_tree2:
        trees[0], trees[1], initial_size_tree1, initial_size_tree2 = trees[1], trees[0], initial_size_tree2, initial_size_tree1


    distance = 0
    nodes = [0, 0]
    intermediate_tree = []
    for i in trees[0]:
        trees[0].nodes[i]["moved"] = 0

    for i in trees[1]:
        trees[1].nodes[i]["moved"] = 0
    start = time.time()

    # print(list(trees[0].nodes(data=True)))
    # print(list(trees[1].nodes(data=True)))

    while number_leaves != 0:

        try:
            trees[1].nodes[nodes[1]]
        except KeyError:
            nodes[0] += 1
            nodes[1] = 0
            try:
                trees[0].nodes[nodes[0]]
            except:
                break

            
        if trees[0].nodes[nodes[0]]["moved"] == 0 and trees[1].nodes[nodes[1]]["moved"] == 0:
                
            # List of element to remove from both trees 
            # index 0 refers to the first tree while index 1 refers to the second tree
            set_tree = [[], []]

            iso, is_v_tree, leaves = v_tree(nodes[0], nodes[1], trees)
            
            
            if leaves != -1:
                number_leaves -= leaves
                for i in iso:
                    for j in range(len(i)):
                        set_tree[0].append(i[j][0])
                        set_tree[1].append(i[j][1])

                path_up, path_down = path_leaves(set_tree, trees)

                for i in path_up:
                    aux = path_up.get(i)
                    distance += 1

                    for j in aux:
                        try:
                            trees[0].remove_edge(i, j)
                        except:
                            pass
                        trees[0].add_edge(next(trees[0].predecessors(i)), j)

                    intermediate_tree.append([trees[0].copy(), distance])

                path_down_sorted = list(path_down.keys())
                path_down_sorted.sort()

                for i in path_down_sorted:
                    aux = path_down.get(i)
                    distance += 1

                    for j in aux:
                        trees[0].remove_edge(next(trees[0].predecessors(j)), j)
                        trees[0].add_edge(i, j)

                    intermediate_tree.append([trees[0].copy(), distance])

            nodes[1] += 1

        elif trees[1].nodes[nodes[1]]["moved"] == 1:
            nodes[1] += 1
            if nodes[1] >= len(trees[1]):
                nodes[0] += 1
                nodes[1] = 0
        
        else:
            nodes[0] += 1
            nodes[1] = 0            
    

    distance += initial_size_tree1 - initial_size_tree2
    end = time.time()


    return distance, end - start, intermediate_tree

if __name__ == '__main__':
    trees, number_leaves = input_trees()
    total_distance, duration, intermediate_tree = calc_distance(trees, number_leaves)