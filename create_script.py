f = open("script_10.sh", "w")

for i in range(100):
    f.write("python3 philogenetic_tree.py 10 " + str(i) + "\n")

for i in range(100):
    f.write("python3 mcat.py 10 " + str(i) + "\n")

f.close()
f = open("script_20.sh", "w")

for i in range(100):
    f.write("python3 philogenetic_tree.py 20 " + str(i) + "\n")

for i in range(100):
    f.write("python3 mcat.py 20 " + str(i) + "\n")