import sys
import random
from sklearn import svm
import os
from sklearn.externals import joblib
import shutil
import pickle

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


def trainOneVsOne(classes):
	keys = classes.keys()
	trainingRate = 0.6
	validationRate = 0.2
	data = []
	tests = []
	validations = []
	dataLabels = []
	validationLabels = []
	testLabels = []
	testN = dict()
	testSuccess = dict()
	validationN = dict()
	validationSuccess = dict()

	minValues = []	# needed for normalization
	maxValues = []	# needed for normalization
	
	for key in keys:
		s = classes[key]
		d = s[:int(trainingRate*len(s))]	# first [0, trainingRate] samples
		v = s[int(trainingRate*len(s)):int((trainingRate+validationRate)*len(s))]	# first [trainingRate, trainingRate+validationRate]
		t = s[int((trainingRate+validationRate)*len(s)):]

		data = data + d
		validations = validations + v
		tests = tests + t

		dataLabels = dataLabels + [key]*len(d)
		validationLabels = validationLabels + [key]*len(v)
		testLabels = testLabels + [key]*len(t)

		validationN[key] = len(v)
		validationSuccess[key] = 0
		testN[key] = len(t)
		testSuccess[key] = 0

	dim = len(data[0])
	minValues = [ min( d[i] for d in data ) for i in range(dim) ]
	maxValues = [ max( d[i] for d in data ) for i in range(dim) ]

	for i in range(len(data)):
		for j in range(dim):
			if minValues[j] == maxValues[j]:
				continue
			data[i][j] = (data[i][j] - minValues[j]) / (maxValues[j] - minValues[j])

	for i in range(len(validations)):
		for j in range(dim):
			if minValues[j] == maxValues[j]:
				continue
			validations[i][j] = (validations[i][j] - minValues[j]) / (maxValues[j] - minValues[j])

	for i in range(len(tests)):
		for j in range(dim):
			if minValues[j] == maxValues[j]:
				continue
			tests[i][j] = (tests[i][j] - minValues[j]) / (maxValues[j] - minValues[j])

	#print minValues
	#print maxValues

	#########################################
	# Iterate through model's parameters
	#########################################

	for t in range(1, 150, 1):
		c = t*4
		#
		# Train model
		#
		clf = svm.SVC(kernel='rbf', gamma = 0.00*1.5, C=c)
		clf.fit(data, dataLabels)
	 
		# 
		# Perform testing
		#
		
		totalRate, rateByClass = performTests(clf, tests, testLabels)
		meanRate = sum( rateByClass[key] for key in rateByClass ) / len(rateByClass)

		print "%f\t%f\t%f"%(c, meanRate, totalRate)

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
