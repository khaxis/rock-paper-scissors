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
	res += "Use format: python {0} <dir>\n".format(argv[0])
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

# make a square out of a rect
def squareRect(x, y, w, h):
	dx, dy = 0, 0
	dw, dh = 0, 0
	if w<h:	# vertical
		dx = -(h-w)/2
		dw = h-w
	if h<w:	# horizontal
		dy = -(w-h)/2
		dh = w-h
	return x + dx, y + dy, w + dw, h + dh
		
def checkRect(img, x, y, w, h):
	height, width = img.shape[:2]
	if x<0 or y<0 or x+w>=width or y+h>=height:
		return False;
	return True;
		
def cropImage(imgPath, goodDir, badDir):
	fileName, fileExtension = os.path.splitext(imgPath)
	goodFilename = fileName + "_good.txt"
	badFilename = fileName + "_bad.txt"
	if not os.path.isfile(goodFilename):
		return
	img = cv2.imread(imgPath);
	if os.path.isfile(goodFilename):
		f = open(goodFilename, 'r')
		line = f.readline();
		f.close()
		x, y, w, h = lineToRect(line)
		x, y, w, h = squareRect(x, y, w, h)
		print x, y, w, h
		if w*h != 0 and checkRect(img, x, y, w, h):
			img_good = img[y:y+h, x:x+w]
			cv2.imwrite(goodDir + "/" + getUniqueName() + "_r.png", img_good)
			cv2.imwrite(goodDir + "/" + getUniqueName() + "_l.png", cv2.flip(img_good, 1))
			#cv2.imshow("good", img_good)
	if os.path.isfile(badFilename):
		f = open(badFilename, 'r')
		for line in f:
			x, y, w, h = lineToRect(line)
			x, y, w, h = squareRect(x, y, w, h)
			print x, y, w, h
			if w*h != 0 and checkRect(img, x, y, w, h):
				img_bad = img[y:y+h, x:x+w]
				cv2.imwrite(badDir + "/" + getUniqueName() + "_r.png", img_bad)
				cv2.imwrite(badDir + "/" + getUniqueName() + "_l.png", cv2.flip(img_bad, 1))
				#cv2.imshow("bad "+line, img_good)
		f.close()


def main(argv):
	#testImage("/home/ivan/workspace/python/rock-paper-scissors/rock/0a2e2642-a065-11e4-8a77-9c4e365d31a4.png")
	#cv2.destroyAllWindows()
	#exit(0)
	if len(argv) == 1:
		print getHelp(argv)
		exit(1)
	else:
		directory = argv[1].rstrip("/\\")
		goodDir = directory + "/pos"
		badDir = directory + "/neg"
		if not os.path.exists(goodDir):
			os.makedirs(goodDir)
		if not os.path.exists(badDir):
			os.makedirs(badDir)
			
		for filename in glob.glob(argv[1] + "/*.png"):
			cropImage(filename, goodDir, badDir)
			#break;
	
if __name__ == "__main__":
	main(sys.argv)
