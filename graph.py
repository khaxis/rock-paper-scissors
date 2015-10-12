import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import sys
from math import *
import random

def main(argv):
	filename = argv[1]
	
	f = open(filename, 'r')
	data = []
	for line in f:
		d = [ float(e) for e in line.split('\t')]
		data.append(d)
	f.close()
	
	d = dict()
	for row in data:
		c = row[0]
		gamma = row[1]
		if c not in d:
			d[c] = dict()
		d[c][gamma] = row[2]
	
	# set up styles
	styles = ['r', 'g', 'b', 'k', 'y', 'm', 'c']
	styles = [ s + ":" for s in styles ] + [s + "--" for s in styles] #+ [s + "-." for s in styles]
	random.shuffle(styles)
	styles = styles*3
	
	plt.xkcd()
	for (c, style) in zip(d, styles):
		gs = sorted([k for k in d[c]])
		y = [d[c][v] for v in gs]
		x = [log(x) for x in gs]
		plt.plot(x, y, style+"o", label=str(c))
	plt.legend()
	plt.xticks(x, gs, rotation='vertical')
	plt.show()
	
if __name__ == "__main__":
	main(sys.argv)
