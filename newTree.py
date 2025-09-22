import sys
import random, math

def removeOnlyChild(list):
    i = 0
    aux = 0
    while(i < len(list)):
        if list[i] == "(" and list[i + 1] == ")":
            list.pop(i)
            list.pop(i)
            aux = 1
        elif list[i] == "(" and list[i + 2] == ")" and (list[i + 1] != "(" and list[i + 1] != ")"):
            list.pop(i + 2)
            list.pop(i)
            aux = 1
        else:
            i += 1


        if i == len(list) and aux:
            aux = 0
            i = 0
    return list


def createTree(leaves, count):
    for i in range(4):
        list = ["(", ")"]
        nodes = [0] * leaves
        for i in range(int(math.log(leaves, 2))):
            left = random.randint(1, len(list) - 1)
            list.insert(left, "(")
            right = random.randint(1 , len(list) - 1)
            while left >= right:
                right = random.randint(1 , len(list) - 1)
            
            list.insert(right, ")")
        
        
        for i in range(leaves):
            leaf = random.randint(1, leaves)
            pos = random.randint(1, len(list) - 2)
            while nodes[leaf - 1] == 1:
                leaf = random.randint(1, leaves)
            nodes[leaf - 1] = 1
            list.insert(pos, leaf)

        list = removeOnlyChild(list)

        list.pop()
        list.pop(0)
        
        f = open("Datasets/" + str(leaves) + "/" + str(count) + ".txt", "a")
        string = ""
        for i in list:
            string += str(i) + " "
        
        f.write(string + "\n")
    
    return 

lenght = int(sys.argv[1])
amount = int(sys.argv[2])

vector = []
for i in range (amount):
    createTree(lenght, i)