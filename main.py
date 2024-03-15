import networkx as nx
from networkx.algorithms import isomorphism
from networkx_algo_common_subtree.tree_isomorphism import *
from networkx_algo_common_subtree.utils import graph_str

global total_leaves
total_leaves = 0

def selectionSort(array, size):
    op = 0
    for ind in range(size):
        min_index = ind
 
        for j in range(ind + 1, size):
            # select the minimum element in every iteration
            if array[j] < array[min_index]:
                min_index = j
         # swapping the elements to sort the array
        (array[ind], array[min_index]) = (array[min_index], array[ind])
        if ind != min_index:
            op += 1
    
    return op

def isomorphism_subtree(node1, node2):
    
    global total_leaves

    sons_node1 = []
    sons_node2 = []

    label1 = []
    label2 = []

    nodes_used = []
    iteration = []

    iterator = tree1.successors(node1)
    while True:
        try:
            sons_node1.append(next(iterator))
        except StopIteration:
            break

    if len(sons_node1) == 0:
        return

    iterator = tree2.successors(node2)
    while True:
        try:
            sons_node2.append(next(iterator))
        except StopIteration:
            break
    
    if len(sons_node2) == 0:
        return
    
    for i in sons_node1:
        nodes_used_aux = []
        
        for j in sons_node2:
            
            iso = isomorphism.rooted_tree_isomorphism(tree1, i, tree2, j)
            if len(iso) != 0:
                label1_aux = []
                label2_aux = []
                for k in range (len(iso)):
                    try:
                        next(tree1.successors(iso[k][0]))
                    except StopIteration:
                        if tree1.nodes[iso[k][0]]["value"] != 0:
                            label1_aux.append(tree1.nodes[iso[k][0]]["value"])
                            label2_aux.append(tree2.nodes[iso[k][1]]["value"])
        
                label1.append(label1_aux)
                label2.append(label2_aux)
                nodes_used_aux.append(i)
                nodes_used_aux.append(j)
                
        iteration.append(-1)
        nodes_used.append(nodes_used_aux)
    

    solution = []

    number_leaves = 0
    while i != -1:
        
        leaves1 = []
        leaves2 = []
        possible = True
        space = 0
        for j in range(len(nodes_used)):
            if nodes_used[j] != []:
                for k in range(len(label1[iteration[j] + space])):
                    if iteration[j] == -1:
                        continue

                    if label2[iteration[j] + space][k] not in leaves2:
                        leaves2.append(label2[iteration[j] + space][k])
                    else:
                        possible = False
                        break

                    if label1[iteration[j] + space][k] not in leaves1:
                        leaves1.append(label1[iteration[j] + space][k])
                    else:
                        possible = False
                        break
                space += len(nodes_used[j]) // 2
        
        if possible:
            leaves1.sort()
            leaves2.sort()
            if leaves1 == leaves2:
                if number_leaves < len(leaves1):
                    number_leaves = len(leaves1)
                    solution = []
                    for j in range(len(iteration)):
                        solution.append([])
                        if iteration[j] != -1:
                            solution[-1].append(nodes_used[j][2 * iteration[j]])
                            solution[-1].append(nodes_used[j][2 * iteration[j] + 1])

            
        i = len(nodes_used) - 1
        aux = 0
        while aux == 0:
            if iteration[i] + 1 == len(nodes_used[i]) // 2:
                iteration[i] = -1
                i -= 1
                if i == -1:
                    break
            else:
                iteration[i] += 1
                aux = 1
    
    if solution:
        total_leaves -= number_leaves
        return solution

f = open("Input.txt", "r")
out = open("Output.txt", "a")

out.write("Input: \n")

lines = f.readlines()
trees = []

first = 0
height = 0
swap = True
for line in lines:
    trees.append(nx.DiGraph())
    trees[-1].add_node(0, value= 0)
    out.write(line)
    newick = line.split()
    amount_node = 0
    current_node = 0
    for i in range(len(newick)):
        if newick[i] == "(":
            height += 1
            amount_node += 1
            trees[-1].add_edge(current_node, amount_node)
            trees[-1].nodes[amount_node]["value"] = 0
            current_node = amount_node
            
        elif newick[i] == ")":
            current_node = next(trees[-1].predecessors(current_node))
            height -= 1

        else:
            if first == 0:
                total_leaves += 1
            if height != 1:
                swap = False
            number = int(newick[i])
            amount_node += 1
            trees[-1].add_edge(current_node, amount_node)
            trees[-1].nodes[amount_node]["value"] = number
    
    first = 1

tree1 = trees[0]
tree2 = trees[1]

# print(list(tree1.nodes(data=True)))
# print(list(tree2.nodes(data=True)))

if len(tree1) < len(tree2):
    tree1, tree2 = tree2, tree1

print("Iniciais: ")
print(graph_str(tree1))
# print(list(tree1.nodes(data=True)))
print(graph_str(tree2))
# print(list(tree2.nodes(data=True)))

quant = 0
distance = 0

new_tree1 = list(tree1.nodes())
new_tree2 = list(tree2.nodes())

iso = []
if swap:
    permutation1 = []
    permutation2 = []

    for i in tree1:
        if tree1.nodes[i]["value"] != 0:
            permutation1.append(tree1.nodes[i]["value"])
    for i in tree2:
        if tree2.nodes[i]["value"] != 0:
            permutation2.append(tree2.nodes[i]["value"])

    dict_swap = dict()
    for i in range(total_leaves):
        dict_swap.update({permutation1[i] : i + 1})
    for i in range(total_leaves):
        permutation2[i] = dict_swap.get(permutation2[i])
    distance = selectionSort(permutation2, total_leaves)
else:
    while total_leaves != 0:

        # List for the nodes that needs to be removed
        nodes1_to_remove = []
        nodes2_to_remove = []

        found = 0
        for i in new_tree1[:]:
            if i in tree1:
                for j in new_tree2[:]:
                    if j in tree2:
                        solution = isomorphism_subtree(i, j)
                        if solution:
                            found = 1
                            while True:
                                try:
                                    solution.remove([])
                                except ValueError:
                                    break
                            # print(solution)
                            for k in solution:
                                iso = isomorphism.rooted_tree_isomorphism(tree1, k[0], tree2, k[1])
                                # print(iso)
                                for l in iso:
                                    nodes1_to_remove.append(l[0])
                                    nodes2_to_remove.append(l[1])
                    if found:
                        break
            if found:
                break

        path = dict()
        quant = quant + 1

        # print(nodes1_to_remove)

        # Search for the nodes that need to ne changed
        # Try e excpet uused to detect leaves
        # Each element from nodes_to_change represents a pair of leaves that need to be change possitions
        nodes_to_change = []
        for i in range(len(nodes1_to_remove)):
            try:
                next(tree1.successors(nodes1_to_remove[i]))
            except StopIteration:
                #print(f'The node {nodes1_to_remove[i]} is a leave with label {tree1.nodes[nodes1_to_remove[i]]["value"]}')
                for j in range(len(nodes2_to_remove)):
                    try:
                        if tree1.nodes[nodes1_to_remove[i]]["value"] == tree2.nodes[nodes2_to_remove[j]]["value"]:
                            if not [nodes1_to_remove[i], nodes2_to_remove[j]] in nodes_to_change:
                                nodes_to_change.append([nodes1_to_remove[i], nodes2_to_remove[j]])
                                nodes_to_change.append([nodes2_to_remove[j], nodes1_to_remove[i]])
                    except KeyError:
                        pass
        
        # print(nodes_to_change)
        

        for i in range(len(nodes_to_change)):
            # If they are brothers, no need to change
            if next(tree1.predecessors(nodes_to_change[i][0])) == next(tree1.predecessors(nodes_to_change[i][1])):
                # print("Brothers")
                continue         

            # If they aren't, go up in the tree to find a common node 
            # Considerer the patch from both leaves to thid node
            # Store this path so if other leaves need to use the same one, the distance isn't counted
            node1 = next(tree1.predecessors(nodes_to_change[i][0]))
            node2 = next(tree1.predecessors(nodes_to_change[i][1]))

            node1_vet = [node1]
            node2_vet = [node2]

            # print("Antes")
            # print(node1_vet)
            # print(node2_vet)

            end = 0

            while ((node1 != 0) or (node2 != 0)) and end == 0:
                if node1 != 0:
                    node1 = next(tree1.predecessors(node1))
                    node1_vet.append(node1)
                
                if node2 != 0:
                    node2 = next(tree1.predecessors(node2))
                    node2_vet.insert(0, node2)
                
                # If the path 
                if node1 != 0:
                    for j in range(len(node2_vet)):
                        if node1 == node2_vet[j]:
                            end = 1
                            # Comparação com os elementos do vetor node1_vet com os do caminho
                            for k in range(len(node1_vet) - 1):
                                element = path.get(node1_vet[k])
                                # Caso o elemento inicial não pertença ao dicionário, então será adicionado essa chave com o seu caminho
                                if element == None:
                                    path.update({node1_vet[k] : [node1_vet[k + 1]]})
                                    distance = distance + 1
                                else:
                                    if not node1_vet[k + 1] in element:
                                        distance = distance + 1
                                        element.append(node1_vet[k + 1])
                                        path.update({node1_vet[k] : element})
                            for k in range(0, j): 
                                element = path.get(node2_vet[k])
                                if element == None:
                                    path.update({node2_vet[k] : [node2_vet[k + 1]]})
                                    distance = distance + 1
                                else:
                                    if not node2_vet[k + 1] in element:
                                        distance = distance + 1
                                        element.append(node2_vet[k + 1])
                                        path.update({node2_vet[k] : element})
                            break

                elif node2 != 0:
                    for j in range(len(node1_vet)):
                        if node2 == node1_vet[j]:
                            end = 1
                            for k in range(len(node2_vet) - 1):
                                element = path.get(node2_vet[k])
                                # If the element doesn't belong to the dictionary, then add a key with this path
                                if element == None:
                                    path.update({node2_vet[k] : [node2_vet[k + 1]]})
                                    distance = distance + 1
                                else:
                                    if not node2_vet[k + 1] in element:
                                        distance = distance + 1
                                        element.append(node2_vet[k + 1])
                                        path.update({node2_vet[k] : element})
                            for k in range(0, j):
                                element = path.get(node1_vet[k])
                                if element == None:
                                    path.update({node1_vet[k] : [node1_vet[k + 1]]})
                                    distance = distance + 1
                                else:
                                    if not node1_vet[k + 1] in element:
                                        distance = distance + 1
                                        element.append(node1_vet[k + 1])
                                        path.update({node1_vet[k] : element})
                            break

                else: # node1 e node2 == 0
                    end = 1
                    for j in range(len(node1_vet) - 1):
                        element = path.get(node1_vet[j])
                        if element == None:
                            path.update({node1_vet[j] : [node1_vet[j + 1]]})
                            distance = distance + 1
                        else:
                            if not node1_vet[j + 1] in element:
                                    distance = distance + 1
                                    element.append(node1_vet[j + 1])
                                    path.update({node1_vet[j] : element})
                    
                    for j in range(len(node2_vet) - 1):
                        element = path.get(node2_vet[j])
                        if element == None:
                            path.update({node2_vet[j] : [node2_vet[j + 1]]})
                            distance = distance + 1
                        else:
                            if not node2_vet[j + 1] in element:
                                    distance = distance + 1
                                    element.append(node2_vet[j + 1])
                                    path.update({node2_vet[j] : element})
                                

                
            # print("After")
            # print(node1_vet)
            # print(node2_vet)

            # print(path)
        # Remoção dos nós da árvore original
        for i in range(len(nodes1_to_remove)):
            tree1.remove_node(nodes1_to_remove[i])
            tree2.remove_node(nodes2_to_remove[i])

        # print(f'Result after {quant} execution')

        # print(graph_str(tree1))
        # print(list(tree1.nodes(data=True)))
        # print(graph_str(tree2))

        # print(list(tree2.nodes(data=True)))
        # print("Total leaves = ",  total_leaves)

        new_tree1 = list(tree1.nodes())
        new_tree2 = list(tree2.nodes())


    distance += (len(tree1) - len(tree2))

print("Distance = ", distance)

out.write(f'\n\nDistance = {distance}\n\n')