import fnmatch
import cv2
import sys
import descriptors

def getDescriptor(filename):
	img = cv2.imread(filename)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	return descriptors.hog(img)
	#return descriptors.lbp(img)

def main(argv):
	for filename in argv[1:]:
		res = getDescriptor(filename)
		
		for i in res:
			print i,
		print
	
main(sys.argv)
