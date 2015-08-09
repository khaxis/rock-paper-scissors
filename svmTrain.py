import sys
import numpy as np
import cv2
import os # need to create a directory
import glob
import uuid

def getUniqueName():
	return str(uuid.uuid1())

def getHelp(argv):
	res = ""
	res += "Use format: python {0} <posDir> <negDir>\n".format(argv[0])
	res += "\t: describes where to store images"
	return res

def lineToRect(line):
	words = line.split(" ")
	x, y, w, h = 0, 0, 0, 0
	if len(words) == 4:
		x = int(words[0])
		y = int(words[1])
		w = int(words[2])
		h = int(words[3])
	return x, y, w, h
		
def getDescriptor(imgPath):
	
	if not os.path.isfile(imgPath):
		raise Exception ("No file or directory: {0}".format(imgPath))
	img = cv2.imread(imgPath);
	
	cv2.imshow("abc", img)
	while True:
		

		if cv2.waitKey(10) >= 0:
			break

def main(argv):
	argv.append("/home/ivan/workspace/python/rock-paper-scissors/rock/good")
	argv.append("/home/ivan/workspace/python/rock-paper-scissors/rock/bad")

	if len(argv) < 2:
		print getHelp(argv)
		exit(1)
	else:
		goodDir = argv[1].rstrip("/\\")
		badDir = argv[2].rstrip("/\\")
		if not os.path.exists(goodDir):
			raise Exception ("wrong directory")
		if not os.path.exists(badDir):
			raise Exception ("wrong directory")
		
		posFilenames = []
		negFilenames = []
		for filename in glob.glob(goodDir + "/*.png"):
			posFilenames.append(filename)
		for filename in glob.glob(badDir + "/*.png"):
			negFilenames.append(filename)
		
		for filename in posFilenames:
			getDescriptor(filename);
		
	
if __name__ == "__main__":
	main(sys.argv)
