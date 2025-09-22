f = open("output/Output_10_mcat.txt", "r")

lines = f.readlines()

total_time = 0
total_closest = 0
total_median = 0
total_normalized_gap_closest = 0
total_normalized_gap_median = 0

for line in lines:
    line = line.split()
    if line[0] == "Duration":
        continue
    
    total_time += float(line[0])
    total_closest += float(line[2])
    total_median += float(line[4])
    total_normalized_gap_closest += float(line[6])
    total_normalized_gap_median += float(line[8])

print(f'Value for 10 leaves with MCAT: Duration = {total_time / 100}, closest = {total_closest / 100}, median = {total_median / 100}, normalized gap closest = {total_normalized_gap_closest / 100} and normalized gap median = {total_normalized_gap_median / 100}' )

f.close()

f = open("output/Output_20_mcat.txt", "r")

lines = f.readlines()

total_time = 0
total_closest = 0
total_median = 0
total_normalized_gap_closest = 0
total_normalized_gap_median = 0

for line in lines:
    line = line.split()
    if line[0] == "Duration":
        continue
    
    total_time += float(line[0])
    total_closest += float(line[2])
    total_median += float(line[4])
    total_normalized_gap_closest += float(line[6])
    total_normalized_gap_median += float(line[8])

print(f'Value for 20 leaves with MCAT: Duration = {total_time / 100}, closest = {total_closest / 100} and median = {total_median / 100}, normalized gap closest = {total_normalized_gap_closest / 100} and normalized gap median = {total_normalized_gap_median / 100}')

f.close()

f = open("output/Output_10_phylo.txt", "r")

lines = f.readlines()

total_time = 0
total_closest = 0
total_median = 0
total_normalized_gap_closest = 0
total_normalized_gap_median = 0

for line in lines:
    line = line.split()
    if line[0] == "Duration":
        continue
    
    total_time += float(line[0])
    total_closest += float(line[2])
    total_median += float(line[4])
    total_normalized_gap_closest += float(line[6])
    total_normalized_gap_median += float(line[8])

print(f'Value for 10 leaves with phylo: Duration = {total_time / 100}, closest = {total_closest / 100} and median = {total_median / 100}, normalized gap closest = {total_normalized_gap_closest / 100} and normalized gap median = {total_normalized_gap_median / 100}')

f.close()

f = open("output/Output_20_phylo.txt", "r")

lines = f.readlines()

total_time = 0
total_closest = 0
total_median = 0
total_normalized_gap_closest = 0
total_normalized_gap_median = 0

for line in lines:
    line = line.split()
    if line[0] == "Duration":
        continue
    
    total_time += float(line[0])
    total_closest += float(line[2])
    total_median += float(line[4])
    total_normalized_gap_closest += float(line[6])
    total_normalized_gap_median += float(line[8])

print(f'Value for 20 leaves with phylo: Duration = {total_time / 100}, closest = {total_closest / 100} and median = {total_median / 100}, normalized gap closest = {total_normalized_gap_closest / 100} and normalized gap median = {total_normalized_gap_median / 100}')

f.close()