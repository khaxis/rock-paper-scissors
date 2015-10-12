import sys
import random
from sklearn import svm
import os
from sklearn.externals import joblib
import shutil
import pickle
from multiprocessing import Pool

OUTPUT_DIR = 'output'

def getHelp(argv):
	res = ""
	res += "Use format: python {0} <class_0> <class_1> [<other_class_2>...]\n".format(argv[0])
	return res

def readClasses(filenames):
	classes = dict()
	for filename in filenames:
		key = os.path.split(filename)[1]
		classes[key] = []
		with open(filename) as f:
			for line in f:
				lineData = [ float(s) for s in line.rstrip('\n').split() ]
				if len(lineData)>1:
					classes[key].append(lineData)
		
		random.shuffle(classes[key])	# shuffle for fun
	
	return classes

def oneVsOne(A, B):
	trainingRate = 0.8
	
	setA = A[:int(trainingRate*len(A))] # take first trainingRate elements
	setB = B[:int(trainingRate*len(B))] # take first trainingRate elements
	testA = A[int(trainingRate*len(A)):]
	testB = B[int(trainingRate*len(B)):]
	
	X = setA + setB
	Y = [0]*len(setA) + [1]*len(setB)
	clf = svm.SVC()

	clf.fit(X, Y)  
	
	## test model
	
	X = testA + testB
	Y = [0]*len(testA) + [1]*len(testB)
	successful = 0
	
	for i in range(len(X)):
		test = X[i]
		expected = Y[i]
		res = clf.predict(test)
		print expected, res[0]
		successful = successful + 1 if expected == res[0] else 0
	
	N = len(X)
	print float(successful)/N

# 
def trainOneVsOne2(classes):
	keys = classes.keys()
	for i in range(len(keys)):
		for j in range(i+1, len(keys)):
			A, B = keys[i], keys[j]
			oneVsOne(classes[A], classes[B])
	
	return


def performTests(clf, data, labels):
	if len(data) != len(labels):
		raise "sizes of data and labels do not match"

	N = len(labels)
	keys = set()
	for label in labels:
		keys.add(label)
	keys = [k for k in keys]

	sizes = dict()
	successes = dict()
	for key in keys:
		sizes[key] = sum( 1 for label in labels if label == key)
		successes[key] = 0

	
	for i in range(N):
		sample = data[i]
		expected = labels[i]
		res = clf.predict(sample)
		s = (1 if expected == res[0] else 0)
		#print "%s\t%s"%(expected, res[0])
		successes[expected] = successes[expected] + s

	totalRate = float( sum(successes[key] for key in keys ) ) / N
	rateByClass = dict()

	for key in keys:
		rateByClass[key] = float(successes[key]) / sizes[key]

	return totalRate, rateByClass

def parallelTrain(x):
	i = x[0]
	gamma = x[1]
	c = x[2]
	bulkData = x[3]
	bulkLabels = x[4]
	validationData = x[5]
	validationLabels = x[6]
	#
	# Train model
	#
	clf = svm.SVC(kernel='rbf', gamma=gamma, C=c)
	clf.fit(bulkData[i], bulkLabels[i])
	# 
	# Perform testing
	#
	
	totalRate, rateByClass = performTests(clf, validationData[i], validationLabels[i])
	meanRate = sum( rateByClass[key] for key in rateByClass ) / len(rateByClass)
	return meanRate, totalRate

def trainOneVsOne(classes):
	keys = classes.keys()
	crossPacN = 5
	trainingRate = 0.8
	data = []
	dataLabels = []
	
	minValues = []	# needed for normalization
	maxValues = []	# needed for normalization
	
	for key in keys:
		d = classes[key]
		data = data + d
		dataLabels = dataLabels + [key]*len(d)

	dim = len(data[0])
	minValues = [ min( d[i] for d in data ) for i in range(dim) ]
	maxValues = [ max( d[i] for d in data ) for i in range(dim) ]
	
	#
	# shuffle data
	#
	data_shuf = []
	dataLabels_shuf = []
	index_shuf = range(len(data))
	random.shuffle(index_shuf)
	for i in index_shuf:
		data_shuf.append(data[i])
		dataLabels_shuf.append(dataLabels[i])
	data = data_shuf
	dataLabels = dataLabels_shuf
	
	# normalize data
	for i in range(len(data)):
		for j in range(dim):
			if minValues[j] == maxValues[j]:
				continue
			data[i][j] = (data[i][j] - minValues[j]) / (maxValues[j] - minValues[j])

	#print minValues
	#print maxValues

	# divide data by bulks for cross validation
	bulkData = dict()
	bulkLabels = dict()
	validationData = dict()
	validationLabels = dict()
	for i in range(crossPacN):
		r0 = float(i)/crossPacN
		r1 = float(i+1)/crossPacN
		validationData[i] = data[ int(r0*len(data)) : int(r1*len(data)) ]
		validationLabels[i] = dataLabels[ int(r0*len(data)) : int(r1*len(data)) ]
		bulkData[i] = data[ : int(r0*len(data)) ] + data[ int(r1*len(data)) : ]
		bulkLabels[i] = dataLabels[ : int(r0*len(data))] + dataLabels[ int(r1*len(data)) : ]

	#########################################
	# Iterate through model's parameters
	#########################################

	for u in range(2, 8):
		for v in range(1, 12):
			c = 0.5 * (2**u)
			t = v/10.0
			t = -2*(1-t) + 0*t
			gamma = 3.0**t
			#print "%f\t%f"%(c, gamma)
			#continue
			
			# perform cross validation
			mr = []
			tr = []
			multithread = False
			if multithread:
				pool = Pool()
				args = []
				for i in range(crossPacN):
					t = []
					t.append(i)
					t.append(gamma)
					t.append(c)
					t.append(bulkData)
					t.append(bulkLabels)
					t.append(validationData)
					t.append(validationLabels)
					args.append(t)
				
				results = pool.map(parallelTrain, args)
				
				for r in results:
					mr.append(r[0])
					tr.append(r[1])
			else:
				for i in range(crossPacN):
					#
					# Train model
					#
					clf = svm.SVC(kernel='rbf', gamma=gamma, C=c)
					clf.fit(bulkData[i], bulkLabels[i])
					# 
					# Perform testing
					#
					
					totalRate, rateByClass = performTests(clf, validationData[i], validationLabels[i])
					meanRate = sum( rateByClass[key] for key in rateByClass ) / len(rateByClass)
					mr.append(meanRate)
					tr.append(totalRate)
			
			# consalidate results
			meanRate = sum( x for x in mr ) / len(mr)
			totalRate = sum (x for x in tr ) / len(tr)
			print "%f\t%f\t%f\t%f"%(c, gamma, meanRate, totalRate)
			sys.stdout.flush()

	exit(1)
	
	#
	# 
	# save to filename.pkl'
	#

	shutil.rmtree(OUTPUT_DIR)
	os.mkdir(OUTPUT_DIR)
	joblib.dump(clf, OUTPUT_DIR+'/svm.pkl')
	with open(OUTPUT_DIR+'/normalization', 'w') as f:
		pickle.dump([minValues, maxValues], f)

	print "---"
	print clf
	print "---"
	print "dim: %d"%dim
	print "---"
	totalRatios = []
	for key in keys:
		print "[%s]: %f"%(key, float(testSuccess[key]) / testN[key] )
		totalRatios.append(float(testSuccess[key]) / testN[key] );
	print '---'
	print "min rate: ", min(r for r in totalRatios)
	print "avg rate: ", sum(r for r in totalRatios) / len(totalRatios)
	print "---"
	print successful,N
	print float(successful)/N


def main(argv):
	if len(argv) < 3:
		print getHelp(argv)
		exit(1)
	
	filenames = argv[1:]
	classes = readClasses(filenames)
	trainOneVsOne(classes)
	
	
main(sys.argv)
