import sys
import random
from sklearn import svm


def getHelp(argv):
	res = ""
	res += "Use format: python {0} <class_0> <class_1> [<other_class_2>...]\n".format(argv[0])
	return res

def readClasses(filenames):
	classes = dict()
	index = 0
	for filename in filenames:
		classes[index] = []
		with open(filename) as f:
			for line in f:
				lineData = [ float(s) for s in line.rstrip('\n').split() ]
				if len(lineData)>1:
					classes[index].append(lineData)
		
		random.shuffle(classes[index])	# shuffle for fun
		index = index + 1
	
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


def trainOneVsOne(classes):
	keys = classes.keys()
	trainingRate = 0.8
	data = []
	tests = []
	dataLabels = []
	testLabels = []
	testN = dict()
	testSuccess = dict()
	
	for key in keys:
		s = classes[key]
		d = s[:int(trainingRate*len(s))]
		t = s[int(trainingRate*len(s)):]
		data = data + d
		tests = tests + t
		dataLabels = dataLabels + [key]*len(d)
		testLabels = testLabels + [key]*len(t)
		testN[key] = len(t)
		testSuccess[key] = 0

	clf = svm.SVC()
	clf.fit(data, dataLabels)
	
	#for i in range(len(keys)):
	#	for j in range(i+1, len(keys)):
	#		A, B = keys[i], keys[j]
	#		oneVsOne(classes[A], classes[B])
	
	successful = 0
	N = len(tests)
	
	for i in range(N):
		test = tests[i]
		expected = testLabels[i]
		res = clf.predict(test)
		print expected, res[0]
		s = (1 if expected == res[0] else 0)
		successful = successful + s
		testSuccess[expected] = testSuccess[expected] + s
		
	print "---"
	for key in keys:
		print "[%s]: %f"%(key, float(testSuccess[key]) / testN[key] )
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
