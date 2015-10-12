import sys
import random
import fileinput

rate = .2

filenames = []
for line in fileinput.input():
	filenames.append(line.replace('\n', ''))

random.shuffle(filenames)
filenames = filenames[:int(rate*len(filenames))]

for r in filenames:
	print r
