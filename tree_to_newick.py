import networkx as nx
from networkx_algo_common_subtree.tree_isomorphism import *

def input_trees():
    
    f = open("input.txt", "r")

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


def create_newick(tree, node):
    newick = ""
    for i in list(tree.neighbors(node)):
        if len(list(tree.neighbors(i))) == 0:
            if newick != "":
                if newick[-1].isdigit() or newick[-1] == ")":
                    newick += ","
            newick += str(tree.nodes[i]['value'])

        else:
            if newick != "":
                if newick[-1].isdigit() or newick[-1] == ")":
                    newick += ","
            newick += "("
            newick += create_newick(tree, i)
            newick += ")"
            
    return newick 

# Read the file input.txt and print the tree with the Newick format
if __name__ == '__main__':
    trees, number_leaves = input_trees()

    newick = "("
    newick += create_newick(trees[0], 0)
    newick += ")"