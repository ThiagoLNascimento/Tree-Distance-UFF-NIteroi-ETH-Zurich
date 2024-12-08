import networkx as nx
from networkx.algorithms import isomorphism
from networkx_algo_common_subtree.tree_isomorphism import *
from networkx_algo_common_subtree.utils import write_network_text
import sys
import time

# Read input file (format Newick)
def input_trees():
    
    f = open("Input.txt", "r")

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
def isomorphism_subtree(node1, node2, trees):

    isomorphic = isomorphism.rooted_tree_isomorphism(trees[0], node1, trees[1], node2)
    list_leaves = [[], []]
    leaves = 0

    if len(isomorphic) != 0:
        for k in range (len(isomorphic)):
            if trees[0].nodes[isomorphic[k][0]]["value"] != 0 or trees[1].nodes[isomorphic[k][1]]["value"] != 0:
                list_leaves[0].append(trees[0].nodes[isomorphic[k][0]]["value"])
                list_leaves[1].append(trees[1].nodes[isomorphic[k][1]]["value"])
                leaves += 1

        list_leaves[0].sort()
        list_leaves[1].sort()

        if list_leaves[0] == list_leaves[1] and leaves > 0:
            return isomorphic, leaves
        
    return [], -1


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
    iso, leaves = isomorphism_subtree(father1, father2, trees)
    return iso, leaves


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


def path_general_nodes(path_up, path_down, node1, node2, trees, which_tree):
    current_path_up = []
    current_path_down = []
    initial_pos = trees[which_tree].predecessors(node1)
    final_pos = trees[which_tree].predecessors(node2)

    # Will get all predecessors of the leaf that needs to be moved
    while True:
        try:
            aux = next(initial_pos)
            current_path_up.append(aux)
            initial_pos = trees[which_tree].predecessors(aux)
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
            final_pos = trees[which_tree].predecessors(aux)
        except StopIteration:
            break
    
    keys = path_up.keys()
    for k in current_path_up:
        if k not in keys:
            path_up[k] = [node1]
        else:
            path_up[k].append(node1)

    keys = path_down.keys()
    for k in current_path_down:
        if k not in keys:
            path_down[k] = [node1]
        else:
            path_down[k].append(node1)

    return path_up, path_down


def path_labeled_nodes(nodes_to_move, trees):
 # Dict for all move to be made in the tree
    # The keys are the nodes that the leaves will move
    # The value of each key is which leaves will move in that node 
    path_up = dict()
    path_down = dict()

    # If the element is a leaf then it needs to find where it should be
    for i in range(len(nodes_to_move[0])):
        label_node_1 = trees[0].nodes[nodes_to_move[0][i]]["label"]

        if label_node_1 != 0:

            for j in range(len(nodes_to_move[0])):
                label_node_2 = trees[1].nodes[nodes_to_move[1][j]]["label"]
                
                if label_node_1 == label_node_2:
                    current_path_up = []
                    current_path_down = []
                    initial_pos = trees[0].predecessors(nodes_to_move[0][i])
                    final_pos = trees[0].predecessors(nodes_to_move[0][j])

                    # Will get all predecessors of the leaf that needs to be moved
                    while True:
                        try:
                            aux = next(initial_pos)
                            if aux != trees[0].nodes[nodes_to_move[0][i]]:
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


# Get a dict with the path and will return a list with the keys ordered by height
# The boolean x determines whether it is non-increasing or non-decreasing
def order_by_height(path, up, tree):
    list = []
    if up == 1:
        for i in path:
            added = 0
            for j in range(len(list)):
                if tree.nodes[i]["height"] < tree.nodes[list[j]]["height"]:
                    added = 1 
                    list.insert(j, i)
                    break
            if added == 0:
                list.append(i)
        return list
    if up == 0:
        for i in path: 
            added = 0
            for j in range(len(list)):
                if tree.nodes[i]["height"] > tree.nodes[list[j]]["height"]:
                    added = 1 
                    list.insert(j, i)
                    break
            if added == 0:
                list.append(i)
        return list


def calc_distance(trees, current_number_leaves, get_intermediate):
 
    initial_size_tree1 = len(trees[0])
    initial_size_tree2 = len(trees[1])

    total_leaves = current_number_leaves
    distance = 0
    last_label = 1
    auxiliary_trees = []
    intermediate_tree = []

    start = time.time()
    
    path_up = dict()
    path_down = dict()
    path_up2 = dict()
    path_down2 = dict()

    number_leaves = 0
    
    while current_number_leaves > 0 and len(trees) > 0 and len(trees) > 0:
        for k in trees[0]:
            for l in trees[1]:

                # List of element to remove from both trees  
                # index 0 refers to the first tree while index 1 refers to the second tree
                set_tree = [[], []]

                iso, number_leaves = v_tree(k, l, trees)

                if number_leaves != -1:
                    current_number_leaves -= number_leaves 
                    try:
                        # If both isometric subtrees have fathers with different labels
                        predecessor = [next(trees[0].predecessors(k)), next(trees[1].predecessors(l))]

                        if trees[0].nodes[predecessor[0]]["label"] == 0 and trees[1].nodes[predecessor[1]]["label"] == 0:
                            trees[0].nodes[predecessor[0]]["label"] = last_label 
                            trees[1].nodes[predecessor[1]]["label"] = last_label
                            last_label += 1
                        else:
                            if trees[0].nodes[predecessor[0]]["label"] != trees[1].nodes[predecessor[1]]["label"]:

                                if trees[0].nodes[predecessor[0]]["label"] != 0 and trees[1].nodes[predecessor[1]]["label"] == 0:
                                    correct_label_node = 0
                                    for i in trees[1]:
                                        if trees[0].nodes[predecessor[0]]["label"] == trees[1].nodes[i]["label"]:
                                            correct_label_node = i
                                            break
                                    correct_label_node = next(trees[1].successors(correct_label_node))
                                    if l != i:
                                        path_up2, path_down2 = path_general_nodes(path_up2, path_down2, l, correct_label_node, trees, 1) 
 
                                elif trees[0].nodes[predecessor[0]]["label"] == 0 and trees[1].nodes[predecessor[1]]["label"] != 0:
                                    correct_label_node = 0
                                    for i in trees[0]:
                                        if trees[1].nodes[predecessor[1]]["label"] == trees[0].nodes[i]["label"]:
                                            correct_label_node = i
                                            break
                                    correct_label_node = next(trees[0].successors(correct_label_node))
                                    if k != i:
                                        path_up, path_down = path_general_nodes(path_up, path_down, k, correct_label_node, trees, 0)

                                else:
                                    correct_label_node = 0
                                    for i in trees[0]:
                                        if trees[1].nodes[predecessor[1]]["label"] == trees[0].nodes[i]["label"]:
                                            correct_label_node = i
                                    correct_label_node = next(trees[0].successors(correct_label_node))
                                    if k != i:
                                        path_up, path_down = path_general_nodes(path_up, path_down, k, correct_label_node, trees, 0)

                    except StopIteration:
                        pass

                    for j in range(len(iso)):
                        set_tree[0].append(iso[j][0])
                        set_tree[1].append(iso[j][1])

                    
                    # Movements that all leaves need to do in each isomophic subtree
                    path_up_leaves, path_down_leaves = path_leaves(set_tree, trees)

                    ordered_path_up_leaves = order_by_height(path_up_leaves, 0, trees[0])
                    for i in ordered_path_up_leaves:
                        aux = path_up_leaves.get(i)
                        distance += 1

                        for j in aux:
                            try:
                                trees[0].remove_edge(i, j)
                            except:
                                pass
                            trees[0].add_edge(next(trees[0].predecessors(i)), j)

                        if get_intermediate == 1:
                            new_tree = nx.DiGraph()
                            new_tree.add_nodes_from(trees[0].nodes(data=True))
                            new_tree.add_edges_from(trees[0].edges())


                            for i in range (len(auxiliary_trees) - 1, -1, -1):
                                new_tree.add_nodes_from(auxiliary_trees[i][0].nodes(data=True))
                                new_tree.add_edges_from(auxiliary_trees[i][0].edges())
                                if auxiliary_trees[i][1] != -1:
                                    new_tree.add_edge(auxiliary_trees[i][1], list(auxiliary_trees[i][0])[0])

                            intermediate_tree.append([new_tree.copy(), distance])
                            new_tree.clear()


                    ordered_path_down_leaves = order_by_height(path_down_leaves, 1, trees[0])
                    for i in ordered_path_down_leaves:
                        aux = path_down_leaves.get(i) 
                        distance += 1

                        for j in aux:
                            trees[0].remove_edge(next(trees[0].predecessors(j)), j)
                            trees[0].add_edge(i, j)

                        if get_intermediate == 1:
                            new_tree = nx.DiGraph()
                            new_tree.add_nodes_from(trees[0].nodes(data=True))
                            new_tree.add_edges_from(trees[0].edges())


                            for i in range (len(auxiliary_trees) - 1, -1, -1):
                                new_tree.add_nodes_from(auxiliary_trees[i][0].nodes(data=True))
                                new_tree.add_edges_from(auxiliary_trees[i][0].edges())
                                if auxiliary_trees[i][1] != -1:
                                    new_tree.add_edge(auxiliary_trees[i][1], list(auxiliary_trees[i][0])[0])
                                    
                            intermediate_tree.append([new_tree.copy(), distance])
                            new_tree.clear()

                    path_up_labels, path_down_labels = path_labeled_nodes(set_tree, trees)

                    ordered_path_up_labels = order_by_height(path_up_labels, 0, trees[0])

                    for i in ordered_path_up_labels:
                        aux = path_up_labels.get(i)
                        distance += 1

                        # for j in aux:
                        #     try:
                        #         trees[0].remove_edge(i, j)
                        #     except:
                        #         pass
                        #     trees[0].add_edge(next(trees[0].predecessors(i)), j)

                        # if get_intermediate == 1:
                        #     new_tree = nx.DiGraph()
                        #     new_tree.add_nodes_from(trees[0].nodes(data=True))
                        #     new_tree.add_edges_from(trees[0].edges())


                        #     for i in range (len(auxiliary_trees) - 1, -1, -1):
                        #         new_tree.add_nodes_from(auxiliary_trees[i][0].nodes(data=True))
                        #         new_tree.add_edges_from(auxiliary_trees[i][0].edges())
                        #         if auxiliary_trees[i][1] != -1:
                        #             new_tree.add_edge(auxiliary_trees[i][1], list(auxiliary_trees[i][0])[0])

                        #     if nx.is_tree(new_tree):
                        #         intermediate_tree.append([new_tree.copy(), distance])
                        #     new_tree.clear()


                    ordered_path_down_labels = order_by_height(path_down_labels, 1, trees[0])

                    for i in path_down_labels:
                        if i in path_down_labels[i]:
                            path_down_labels[i].remove(i)

                    for i in ordered_path_down_labels:
                        aux = path_down_labels.get(i) 
                        distance += 1

                        # for j in aux:
                        #     trees[0].remove_edge(next(trees[0].predecessors(j)), j)
                        #     trees[0].add_edge(i, j)

                        # if get_intermediate == 1:
                        #     new_tree = nx.DiGraph()
                        #     new_tree.add_nodes_from(trees[0].nodes(data=True))
                        #     new_tree.add_edges_from(trees[0].edges())


                        #     for i in range (len(auxiliary_trees) - 1, -1, -1):
                        #         new_tree.add_nodes_from(auxiliary_trees[i][0].nodes(data=True))
                        #         new_tree.add_edges_from(auxiliary_trees[i][0].edges())
                        #         if auxiliary_trees[i][1] != -1:
                        #             new_tree.add_edge(auxiliary_trees[i][1], list(auxiliary_trees[i][0])[0])
                            
                        #     if nx.is_tree(new_tree):
                        #         intermediate_tree.append([new_tree.copy(), distance])
                        #     new_tree.clear()
                        
                    break

            if number_leaves != -1:
                break 

        if number_leaves != -1:
            # Remove nodes from the graph and create an auxiliary forest with all subgraph that were removed
            new_tree = nx.DiGraph()
            try:
                temp_node = next(trees[0].predecessors(iso[0][0]))
            except StopIteration:
                temp_node = -1
            for j in range(len(iso)):
                new_tree.add_node(iso[j][0], value = trees[0].nodes[iso[j][0]]["value"], label = trees[0].nodes[iso[j][0]]["label"], height = trees[0].nodes[iso[j][0]]["height"])
                iterator = trees[0].successors(iso[j][0])
                while True:
                    try: 
                        new_tree.add_edge(iso[j][0], next(iterator))
                    except StopIteration:
                        break

                if j > 0:
                    try:
                        new_tree.add_edge(next(trees[0].predecessors(iso[j][0])), iso[j][0])
                    except StopIteration:
                        continue
                    
            for j in range(len(iso)):
                trees[0].remove_node(iso[j][0])
                trees[1].remove_node(iso[j][1])

            auxiliary_trees.append([new_tree, temp_node])
 
    for i in range (len(auxiliary_trees) - 1, -1, -1):
        trees[0].add_nodes_from(auxiliary_trees[i][0].nodes(data=True))
        trees[0].add_edges_from(auxiliary_trees[i][0].edges())
        if auxiliary_trees[i][1] != -1:
            trees[0].add_edge(auxiliary_trees[i][1], list(auxiliary_trees[i][0])[0])

    
    for i in trees[0]:
        trees[0].nodes[i]["label"] = 0
        if trees[0].nodes[i]["value"] > total_leaves:
            trees[0].nodes[i]["value"] = 0

    ordered_path_up = order_by_height(path_up, 0, trees[0])

    for i in ordered_path_up:
        aux = path_up.get(i) 
        distance += 1

        for j in aux:
            try:
                trees[0].remove_edge(i, j)
            except:
                pass
            trees[0].add_edge(next(trees[0].predecessors(i)), j)
        
        if get_intermediate == 1 and  nx.is_tree(trees[0]):
            intermediate_tree.append([trees[0].copy(), distance])

    ordered_path_down = order_by_height(path_down, 1, trees[0])
    for i in ordered_path_down:
        aux = path_down.get(i)
        distance += 1

        for j in aux:
            trees[0].remove_edge(next(trees[0].predecessors(j)), j)
            trees[0].add_edge(i, j)

        if get_intermediate == 1 and nx.is_tree(trees[0]): 
            intermediate_tree.append([trees[0].copy(), distance])

    for i in path_up2:
        aux = path_up2.get(i)
        distance += 1

    for i in path_down2:
        aux = path_down2.get(i)
        distance += 1


    distance += initial_size_tree1 - initial_size_tree2
    end = time.time()

    if len(intermediate_tree) < distance//4  and distance != 0 and get_intermediate == 1:
        trees[0], trees[1] = trees[1], trees[0]
        return calc_distance(trees, current_number_leaves, 1)
    return distance, end - start, intermediate_tree

if __name__ == '__main__':
    # trees, current_number_leaves = input_trees() 
    # print(write_network_text(trees[0], with_labels=False)) 
    # print(write_network_text(trees[1], with_labels=False)) 

    trees = []
    current_number_leaves = 79
    new_tree = nx.DiGraph()
    new_tree.add_nodes_from([(0, {'value': 0, 'height': 0, 'label': 0}), (1, {'value': 0, 'label': 0, 'height': 1}), (2, {'value': 0, 'label': 0, 'height': 2}), (3, {'value': 0, 'label': 0, 'height': 3}), (4, {'value': 0, 'label': 0, 'height': 4}), (5, {'value': 0, 'label': 0, 'height': 5}), (6, {'value': 0, 'label': 0, 'height': 6}), (7, {'value': 0, 'label': 0, 'height': 7}), (8, {'value': 0, 'label': 0, 'height': 8}), (9, {'value': 0, 'label': 0, 'height': 9}), (10, {'value': 0, 'label': 0, 'height': 10}), (11, {'value': 0, 'label': 0, 'height': 11}), (12, {'value': 0, 'label': 0, 'height': 12}), (13, {'value': 0, 'label': 0, 'height': 13}), (14, {'value': 0, 'label': 0, 'height': 14}), (15, {'value': 0, 'label': 0, 'height': 15}), (16, {'value': 0, 'label': 0, 'height': 16}), (17, {'value': 0, 'label': 0, 'height': 17}), (18, {'value': 0, 'label': 0, 'height': 18}), (19, {'value': 0, 'label': 0, 'height': 19}), (20, {'value': 0, 'label': 0, 'height': 20}), (21, {'value': 0, 'label': 0, 'height': 21}), (22, {'value': 0, 'label': 0, 'height': 22}), (23, {'value': 0, 'label': 0, 'height': 23}), (24, {'value': 0, 'label': 0, 'height': 24}), (25, {'value': 0, 'label': 0, 'height': 25}), (26, {'value': 0, 'label': 0, 'height': 26}), (27, {'value': 0, 'label': 0, 'height': 27}), (28, {'value': 0, 'label': 0, 'height': 28}), (29, {'value': 0, 'label': 0, 'height': 29}), (30, {'value': 0, 'label': 0, 'height': 30}), (31, {'value': 0, 'label': 0, 'height': 31}), (32, {'value': 0, 'label': 0, 'height': 32}), (33, {'value': 0, 'label': 0, 'height': 33}), (34, {'value': 0, 'label': 0, 'height': 34}), (35, {'value': 0, 'label': 0, 'height': 35}), (36, {'value': 0, 'label': 0, 'height': 36}), (37, {'value': 0, 'label': 0, 'height': 37}), (38, {'value': 0, 'label': 0, 'height': 38}), (39, {'value': 0, 'label': 0, 'height': 39}), (40, {'value': 0, 'label': 0, 'height': 40}), (41, {'value': 0, 'label': 0, 'height': 41}), (42, {'value': 0, 'label': 0, 'height': 42}), (43, {'value': 0, 'label': 0, 'height': 43}), (44, {'value': 0, 'label': 0, 'height': 44}), (45, {'value': 0, 'label': 0, 'height': 45}), (46, {'value': 0, 'label': 0, 'height': 46}), (47, {'value': 0, 'label': 0, 'height': 47}), (48, {'value': 0, 'label': 0, 'height': 48}), (49, {'value': 0, 'label': 0, 'height': 49}), (50, {'value': 0, 'label': 0, 'height': 50}), (51, {'value': 0, 'label': 0, 'height': 51}), (52, {'value': 0, 'label': 0, 'height': 52}), (53, {'value': 0, 'label': 0, 'height': 53}), (54, {'value': 0, 'label': 0, 'height': 54}), (55, {'value': 0, 'label': 0, 'height': 55}), (56, {'value': 0, 'label': 0, 'height': 56}), (57, {'value': 0, 'label': 0, 'height': 57}), (58, {'value': 0, 'label': 0, 'height': 58}), (59, {'value': 0, 'label': 0, 'height': 59}), (60, {'value': 0, 'label': 0, 'height': 60}), (61, {'value': 0, 'label': 0, 'height': 61}), (62, {'value': 0, 'label': 0, 'height': 62}), (63, {'value': 0, 'label': 0, 'height': 63}), (64, {'value': 0, 'label': 0, 'height': 64}), (65, {'value': 0, 'label': 0, 'height': 65}), (66, {'value': 8, 'label': 0, 'height': 66}), (67, {'value': 0, 'label': 0, 'height': 66}), (68, {'value': 0, 'label': 0, 'height': 67}), (69, {'value': 0, 'label': 0, 'height': 68}), (70, {'value': 0, 'label': 0, 'height': 69}), (71, {'value': 0, 'label': 0, 'height': 70}), (72, {'value': 32, 'label': 0, 'height': 71}), (73, {'value': 0, 'label': 0, 'height': 71}), (74, {'value': 0, 'label': 0, 'height': 72}), (75, {'value': 0, 'label': 0, 'height': 73}), (76, {'value': 0, 'label': 0, 'height': 74}), (77, {'value': 0, 'label': 0, 'height': 75}), (78, {'value': 0, 'label': 0, 'height': 76}), (79, {'value': 10, 'label': 0, 'height': 77}), (80, {'value': 56, 'label': 0, 'height': 76}), (81, {'value': 33, 'label': 0, 'height': 75}), (82, {'value': 2, 'label': 0, 'height': 74}), (83, {'value': 31, 'label': 0, 'height': 73}), (84, {'value': 68, 'label': 0, 'height': 72}), (85, {'value': 63, 'label': 0, 'height': 71}), (86, {'value': 3, 'label': 0, 'height': 70}), (87, {'value': 22, 'label': 0, 'height': 69}), (88, {'value': 71, 'label': 0, 'height': 68}), (89, {'value': 59, 'label': 0, 'height': 67}), (90, {'value': 18, 'label': 0, 'height': 66}), (91, {'value': 19, 'label': 0, 'height': 65}), (92, {'value': 55, 'label': 0, 'height': 64}), (93, {'value': 62, 'label': 0, 'height': 63}), (94, {'value': 49, 'label': 0, 'height': 62}), (95, {'value': 6, 'label': 0, 'height': 61}), (96, {'value': 23, 'label': 0, 'height': 60}), (97, {'value': 42, 'label': 0, 'height': 59}), (98, {'value': 69, 'label': 0, 'height': 58}), (99, {'value': 17, 'label': 0, 'height': 57}), (100, {'value': 36, 'label': 0, 'height': 56}), (101, {'value': 60, 'label': 0, 'height': 55}), (102, {'value': 75, 'label': 0, 'height': 54}), (103, {'value': 11, 'label': 0, 'height': 53}), (104, {'value': 46, 'label': 0, 'height': 52}), (105, {'value': 73, 'label': 0, 'height': 51}), (106, {'value': 20, 'label': 0, 'height': 50}), (107, {'value': 61, 'label': 0, 'height': 49}), (108, {'value': 57, 'label': 0, 'height': 48}), (109, {'value': 12, 'label': 0, 'height': 47}), (110, {'value': 37, 'label': 0, 'height': 46}), (111, {'value': 65, 'label': 0, 'height': 45}), (112, {'value': 16, 'label': 0, 'height': 44}), (113, {'value': 4, 'label': 0, 'height': 43}), (114, {'value': 24, 'label': 0, 'height': 42}), (115, {'value': 48, 'label': 0, 'height': 41}), (116, {'value': 27, 'label': 0, 'height': 40}), (117, {'value': 76, 'label': 0, 'height': 39}), (118, {'value': 50, 'label': 0, 'height': 38}), (119, {'value': 78, 'label': 0, 'height': 37}), (120, {'value': 54, 'label': 0, 'height': 36}), (121, {'value': 67, 'label': 0, 'height': 35}), (122, {'value': 66, 'label': 0, 'height': 34}), (123, {'value': 41, 'label': 0, 'height': 33}), (124, {'value': 53, 'label': 0, 'height': 32}), (125, {'value': 35, 'label': 0, 'height': 31}), (126, {'value': 52, 'label': 0, 'height': 30}), (127, {'value': 26, 'label': 0, 'height': 29}), (128, {'value': 51, 'label': 0, 'height': 28}), (129, {'value': 14, 'label': 0, 'height': 27}), (130, {'value': 29, 'label': 0, 'height': 26}), (131, {'value': 58, 'label': 0, 'height': 25}), (132, {'value': 1, 'label': 0, 'height': 24}), (133, {'value': 9, 'label': 0, 'height': 23}), (134, {'value': 45, 'label': 0, 'height': 22}), (135, {'value': 15, 'label': 0, 'height': 21}), (136, {'value': 74, 'label': 0, 'height': 20}), (137, {'value': 72, 'label': 0, 'height': 19}), (138, {'value': 5, 'label': 0, 'height': 18}), (139, {'value': 21, 'label': 0, 'height': 17}), (140, {'value': 40, 'label': 0, 'height': 16}), (141, {'value': 43, 'label': 0, 'height': 15}), (142, {'value': 38, 'label': 0, 'height': 14}), (143, {'value': 70, 'label': 0, 'height': 13}), (144, {'value': 64, 'label': 0, 'height': 12}), (145, {'value': 44, 'label': 0, 'height': 11}), (146, {'value': 13, 'label': 0, 'height': 10}), (147, {'value': 47, 'label': 0, 'height': 9}), (148, {'value': 30, 'label': 0, 'height': 8}), (149, {'value': 7, 'label': 0, 'height': 7}), (150, {'value': 39, 'label': 0, 'height': 6}), (151, {'value': 34, 'label': 0, 'height': 5}), (152, {'value': 28, 'label': 0, 'height': 4}), (153, {'value': 77, 'label': 0, 'height': 3}), (154, {'value': 25, 'label': 0, 'height': 2}), (155, {'value': 79, 'label': 0, 'height': 1})])
    new_tree.add_edges_from([(0, 1), (0, 155), (1, 2), (1, 154), (2, 3), (2, 153), (3, 4), (3, 152), (4, 5), (4, 151), (5, 6), (5, 150), (6, 7), (6, 149), (7, 8), (7, 148), (8, 9), (8, 147), (9, 10), (9, 146), (10, 11), (10, 145), (11, 12), (11, 144), (12, 13), (12, 143), (13, 14), (13, 142), (14, 15), (14, 141), (15, 16), (15, 140), (16, 17), (16, 139), (17, 18), (17, 138), (18, 19), (18, 137), (19, 20), (19, 136), (20, 21), (20, 135), (21, 22), (21, 134), (22, 23), (22, 133), (23, 24), (23, 132), (24, 25), (24, 131), (25, 26), (25, 130), (26, 27), (26, 129), (27, 28), (27, 128), (28, 29), (28, 127), (29, 30), (29, 126), (30, 31), (30, 122), (31, 32), (31, 124), (31, 125), (32, 33), (32, 123), (33, 34), (34, 35), (34, 121), (35, 36), (35, 120), (36, 37), (36, 119), (37, 38), (37, 118), (38, 39), (38, 117), (39, 40), (39, 116), (40, 41), (40, 115), (41, 42), (41, 114), (42, 43), (42, 113), (43, 44), (43, 112), (44, 45), (44, 111), (45, 46), (45, 110), (46, 47), (46, 109), (47, 48), (47, 108), (48, 49), (48, 107), (49, 50), (49, 106), (50, 51), (50, 105), (51, 52), (51, 104), (52, 53), (52, 103), (53, 54), (53, 102), (54, 55), (54, 101), (55, 56), (55, 100), (56, 57), (56, 99), (57, 58), (57, 98), (58, 59), (58, 97), (59, 60), (59, 96), (60, 61), (60, 95), (61, 62), (61, 94), (62, 63), (62, 93), (63, 64), (63, 92), (64, 65), (64, 91), (65, 66), (65, 67), (65, 90), (67, 68), (67, 89), (68, 69), (68, 88), (69, 70), (69, 87), (70, 71), (70, 86), (71, 72), (71, 73), (71, 85), (73, 74), (73, 84), (74, 75), (74, 83), (75, 76), (75, 82), (76, 77), (76, 81), (77, 78), (77, 80), (78, 79)])

    trees.append(new_tree)
    new_tree1 = nx.DiGraph()
    new_tree1.add_nodes_from([(0, {'value': 0, 'height': 0, 'label': 0}), (1, {'value': 0, 'label': 0, 'height': 1}), (2, {'value': 0, 'label': 0, 'height': 2}), (3, {'value': 0, 'label': 0, 'height': 3}), (4, {'value': 0, 'label': 0, 'height': 4}), (5, {'value': 0, 'label': 0, 'height': 5}), (6, {'value': 0, 'label': 0, 'height': 6}), (7, {'value': 0, 'label': 0, 'height': 7}), (8, {'value': 0, 'label': 0, 'height': 8}), (9, {'value': 0, 'label': 0, 'height': 9}), (10, {'value': 0, 'label': 0, 'height': 10}), (11, {'value': 0, 'label': 0, 'height': 11}), (12, {'value': 0, 'label': 0, 'height': 12}), (13, {'value': 0, 'label': 0, 'height': 13}), (14, {'value': 0, 'label': 0, 'height': 14}), (15, {'value': 0, 'label': 0, 'height': 15}), (16, {'value': 0, 'label': 0, 'height': 16}), (17, {'value': 0, 'label': 0, 'height': 17}), (18, {'value': 0, 'label': 0, 'height': 18}), (19, {'value': 0, 'label': 0, 'height': 19}), (20, {'value': 0, 'label': 0, 'height': 20}), (21, {'value': 0, 'label': 0, 'height': 21}), (22, {'value': 0, 'label': 0, 'height': 22}), (23, {'value': 0, 'label': 0, 'height': 23}), (24, {'value': 0, 'label': 0, 'height': 24}), (25, {'value': 0, 'label': 0, 'height': 25}), (26, {'value': 0, 'label': 0, 'height': 26}), (27, {'value': 0, 'label': 0, 'height': 27}), (28, {'value': 0, 'label': 0, 'height': 28}), (29, {'value': 0, 'label': 0, 'height': 29}), (30, {'value': 0, 'label': 0, 'height': 30}), (31, {'value': 0, 'label': 0, 'height': 31}), (32, {'value': 0, 'label': 0, 'height': 32}), (33, {'value': 0, 'label': 0, 'height': 33}), (34, {'value': 0, 'label': 0, 'height': 34}), (35, {'value': 0, 'label': 0, 'height': 35}), (36, {'value': 0, 'label': 0, 'height': 36}), (37, {'value': 0, 'label': 0, 'height': 37}), (38, {'value': 0, 'label': 0, 'height': 38}), (39, {'value': 0, 'label': 0, 'height': 39}), (40, {'value': 0, 'label': 0, 'height': 40}), (41, {'value': 0, 'label': 0, 'height': 41}), (42, {'value': 0, 'label': 0, 'height': 42}), (43, {'value': 0, 'label': 0, 'height': 43}), (44, {'value': 0, 'label': 0, 'height': 44}), (45, {'value': 0, 'label': 0, 'height': 45}), (46, {'value': 0, 'label': 0, 'height': 46}), (47, {'value': 0, 'label': 0, 'height': 47}), (48, {'value': 0, 'label': 0, 'height': 48}), (49, {'value': 0, 'label': 0, 'height': 49}), (50, {'value': 0, 'label': 0, 'height': 50}), (51, {'value': 0, 'label': 0, 'height': 51}), (52, {'value': 0, 'label': 0, 'height': 52}), (53, {'value': 0, 'label': 0, 'height': 53}), (54, {'value': 0, 'label': 0, 'height': 54}), (55, {'value': 0, 'label': 0, 'height': 55}), (56, {'value': 0, 'label': 0, 'height': 56}), (57, {'value': 0, 'label': 0, 'height': 57}), (58, {'value': 0, 'label': 0, 'height': 58}), (59, {'value': 0, 'label': 0, 'height': 59}), (60, {'value': 0, 'label': 0, 'height': 60}), (61, {'value': 0, 'label': 0, 'height': 61}), (62, {'value': 0, 'label': 0, 'height': 62}), (63, {'value': 0, 'label': 0, 'height': 63}), (64, {'value': 0, 'label': 0, 'height': 64}), (65, {'value': 0, 'label': 0, 'height': 65}), (66, {'value': 8, 'label': 0, 'height': 66}), (67, {'value': 0, 'label': 0, 'height': 66}), (68, {'value': 0, 'label': 0, 'height': 67}), (69, {'value': 0, 'label': 0, 'height': 68}), (70, {'value': 0, 'label': 0, 'height': 69}), (71, {'value': 0, 'label': 0, 'height': 70}), (72, {'value': 32, 'label': 0, 'height': 71}), (73, {'value': 0, 'label': 0, 'height': 71}), (74, {'value': 0, 'label': 0, 'height': 72}), (75, {'value': 0, 'label': 0, 'height': 73}), (76, {'value': 0, 'label': 0, 'height': 74}), (77, {'value': 0, 'label': 0, 'height': 75}), (78, {'value': 0, 'label': 0, 'height': 76}), (79, {'value': 10, 'label': 0, 'height': 77}), (80, {'value': 56, 'label': 0, 'height': 76}), (81, {'value': 33, 'label': 0, 'height': 75}), (82, {'value': 2, 'label': 0, 'height': 74}), (83, {'value': 31, 'label': 0, 'height': 73}), (84, {'value': 68, 'label': 0, 'height': 72}), (85, {'value': 63, 'label': 0, 'height': 71}), (86, {'value': 3, 'label': 0, 'height': 70}), (87, {'value': 22, 'label': 0, 'height': 69}), (88, {'value': 71, 'label': 0, 'height': 68}), (89, {'value': 59, 'label': 0, 'height': 67}), (90, {'value': 18, 'label': 0, 'height': 66}), (91, {'value': 19, 'label': 0, 'height': 65}), (92, {'value': 55, 'label': 0, 'height': 64}), (93, {'value': 62, 'label': 0, 'height': 63}), (94, {'value': 49, 'label': 0, 'height': 62}), (95, {'value': 6, 'label': 0, 'height': 61}), (96, {'value': 23, 'label': 0, 'height': 60}), (97, {'value': 42, 'label': 0, 'height': 59}), (98, {'value': 69, 'label': 0, 'height': 58}), (99, {'value': 17, 'label': 0, 'height': 57}), (100, {'value': 36, 'label': 0, 'height': 56}), (101, {'value': 60, 'label': 0, 'height': 55}), (102, {'value': 75, 'label': 0, 'height': 54}), (103, {'value': 11, 'label': 0, 'height': 53}), (104, {'value': 46, 'label': 0, 'height': 52}), (105, {'value': 73, 'label': 0, 'height': 51}), (106, {'value': 20, 'label': 0, 'height': 50}), (107, {'value': 61, 'label': 0, 'height': 49}), (108, {'value': 57, 'label': 0, 'height': 48}), (109, {'value': 12, 'label': 0, 'height': 47}), (110, {'value': 37, 'label': 0, 'height': 46}), (111, {'value': 65, 'label': 0, 'height': 45}), (112, {'value': 16, 'label': 0, 'height': 44}), (113, {'value': 4, 'label': 0, 'height': 43}), (114, {'value': 24, 'label': 0, 'height': 42}), (115, {'value': 48, 'label': 0, 'height': 41}), (116, {'value': 27, 'label': 0, 'height': 40}), (117, {'value': 76, 'label': 0, 'height': 39}), (118, {'value': 50, 'label': 0, 'height': 38}), (119, {'value': 78, 'label': 0, 'height': 37}), (120, {'value': 54, 'label': 0, 'height': 36}), (121, {'value': 67, 'label': 0, 'height': 35}), (122, {'value': 66, 'label': 0, 'height': 34}), (123, {'value': 41, 'label': 0, 'height': 33}), (124, {'value': 53, 'label': 0, 'height': 32}), (125, {'value': 35, 'label': 0, 'height': 31}), (126, {'value': 40, 'label': 0, 'height': 30}), (127, {'value': 26, 'label': 0, 'height': 29}), (128, {'value': 51, 'label': 0, 'height': 28}), (129, {'value': 9, 'label': 0, 'height': 27}), (130, {'value': 29, 'label': 0, 'height': 26}), (131, {'value': 58, 'label': 0, 'height': 25}), (132, {'value': 1, 'label': 0, 'height': 24}), (133, {'value': 14, 'label': 0, 'height': 23}), (134, {'value': 45, 'label': 0, 'height': 22}), (135, {'value': 15, 'label': 0, 'height': 21}), (136, {'value': 74, 'label': 0, 'height': 20}), (137, {'value': 72, 'label': 0, 'height': 19}), (138, {'value': 5, 'label': 0, 'height': 18}), (139, {'value': 21, 'label': 0, 'height': 17}), (140, {'value': 52, 'label': 0, 'height': 16}), (141, {'value': 43, 'label': 0, 'height': 15}), (142, {'value': 38, 'label': 0, 'height': 14}), (143, {'value': 70, 'label': 0, 'height': 13}), (144, {'value': 64, 'label': 0, 'height': 12}), (145, {'value': 44, 'label': 0, 'height': 11}), (146, {'value': 13, 'label': 0, 'height': 10}), (147, {'value': 47, 'label': 0, 'height': 9}), (148, {'value': 30, 'label': 0, 'height': 8}), (149, {'value': 7, 'label': 0, 'height': 7}), (150, {'value': 39, 'label': 0, 'height': 6}), (151, {'value': 34, 'label': 0, 'height': 5}), (152, {'value': 28, 'label': 0, 'height': 4}), (153, {'value': 77, 'label': 0, 'height': 3}), (154, {'value': 25, 'label': 0, 'height': 2}), (155, {'value': 79, 'label': 0, 'height': 1})])
    new_tree1.add_edges_from([(0, 1), (0, 155), (1, 2), (1, 154), (2, 3), (2, 153), (3, 4), (3, 152), (4, 5), (4, 151), (5, 6), (5, 150), (6, 7), (6, 149), (7, 8), (7, 148), (8, 9), (8, 147), (9, 10), (9, 146), (10, 11), (10, 145), (11, 12), (11, 144), (12, 13), (12, 143), (13, 14), (13, 142), (14, 15), (14, 141), (15, 16), (15, 140), (16, 17), (16, 139), (17, 18), (17, 138), (18, 19), (18, 137), (19, 20), (19, 136), (20, 21), (20, 135), (21, 22), (21, 134), (22, 23), (22, 129), (23, 24), (23, 132), (23, 133), (24, 25), (24, 131), (25, 26), (25, 130), (26, 27), (27, 28), (27, 128), (28, 29), (28, 127), (29, 30), (29, 126), (30, 31), (30, 125), (31, 32), (31, 124), (32, 33), (32, 123), (33, 34), (33, 122), (34, 35), (34, 121), (35, 36), (35, 120), (36, 37), (36, 119), (37, 38), (37, 118), (38, 39), (38, 117), (39, 40), (39, 116), (40, 41), (40, 115), (41, 42), (41, 114), (42, 43), (42, 113), (43, 44), (43, 112), (44, 45), (44, 111), (45, 46), (45, 110), (46, 47), (46, 109), (47, 48), (47, 108), (48, 49), (48, 107), (49, 50), (49, 106), (50, 51), (50, 105), (51, 52), (51, 104), (52, 53), (52, 103), (53, 54), (53, 102), (54, 55), (54, 101), (55, 56), (55, 100), (56, 57), (56, 99), (57, 58), (57, 98), (58, 59), (58, 97), (59, 60), (59, 96), (60, 61), (60, 95), (61, 62), (61, 94), (62, 63), (62, 93), (63, 64), (63, 92), (64, 65), (64, 91), (65, 66), (65, 67), (65, 90), (67, 68), (67, 89), (68, 69), (68, 88), (69, 70), (69, 87), (70, 71), (70, 86), (71, 72), (71, 73), (71, 85), (73, 74), (73, 84), (74, 75), (74, 83), (75, 76), (75, 82), (76, 77), (76, 81), (77, 78), (77, 80), (78, 79)])
    
    trees.append(new_tree1)

    total_distance, duration, intermediate_tree = calc_distance(trees, current_number_leaves, 1)